import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from app.analysis.models import AnalysisBundle
from app.config.settings import APP_DATA_DIR, DATABASE_FILE


class Database:
    """SQLite 数据访问层。整个数据库就是一个本地 .db 文件。"""

    def __init__(self, db_path: Path = DATABASE_FILE):
        self.db_path = Path(db_path)
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self):
        with self.connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS analysis_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    sectors_json TEXT NOT NULL,
                    market_summary TEXT,
                    result_json TEXT NOT NULL,
                    research_text TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fingerprint TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    event_date TEXT,
                    source TEXT,
                    url TEXT,
                    analysis TEXT,
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS analysis_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_run_id INTEGER NOT NULL,
                    event_id INTEGER NOT NULL,
                    sector TEXT NOT NULL,
                    impact TEXT,
                    impact_type TEXT,
                    importance INTEGER,
                    FOREIGN KEY (analysis_run_id)
                        REFERENCES analysis_runs(id) ON DELETE CASCADE,
                    FOREIGN KEY (event_id)
                        REFERENCES events(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS custom_sectors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS provider_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_run_id INTEGER NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    result_json TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (analysis_run_id)
                        REFERENCES analysis_runs(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_provider_results_run
                ON provider_results(analysis_run_id);

                CREATE INDEX IF NOT EXISTS idx_runs_created
                ON analysis_runs(created_at DESC);

                CREATE INDEX IF NOT EXISTS idx_events_seen
                ON events(last_seen_at DESC);
            """)

    def add_custom_sector(self, name: str) -> bool:
        name = " ".join(name.strip().split())
        if not name:
            return False
        try:
            with self.connect() as conn:
                conn.execute(
                    "INSERT INTO custom_sectors(name, created_at) VALUES (?, ?)",
                    (name, datetime.now().isoformat(timespec="seconds")),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_custom_sector(self, name: str):
        with self.connect() as conn:
            conn.execute(
                "DELETE FROM custom_sectors WHERE name = ?",
                (name,),
            )

    def list_custom_sectors(self) -> list[str]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT name FROM custom_sectors ORDER BY id"
            ).fetchall()
        return [row["name"] for row in rows]

    def save_analysis(self, bundle: AnalysisBundle) -> int:
        created_at = bundle.generated_at.isoformat(timespec="seconds")
        result_json = json.dumps(bundle.structured, ensure_ascii=False)

        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO analysis_runs(
                    created_at, provider, model, sectors_json,
                    market_summary, result_json, research_text
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    bundle.provider,
                    bundle.model,
                    json.dumps(bundle.sectors, ensure_ascii=False),
                    str(bundle.structured.get("market_summary", "")),
                    result_json,
                    bundle.research_text,
                ),
            )
            run_id = int(cursor.lastrowid)
            self._save_events(conn, run_id, bundle, created_at)
            self._save_provider_results(
                conn,
                run_id,
                bundle,
                created_at,
            )

        return run_id

    def list_analysis_runs(self, limit: int = 100) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    ar.id,
                    ar.created_at,
                    ar.provider,
                    ar.model,
                    ar.sectors_json,
                    ar.market_summary,
                    (
                        SELECT COUNT(*)
                        FROM provider_results pr
                        WHERE pr.analysis_run_id = ar.id
                          AND pr.error IS NULL
                    ) AS provider_count
                FROM analysis_runs ar
                ORDER BY ar.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        result = []
        for row in rows:
            item = dict(row)
            try:
                item["sectors"] = json.loads(item.pop("sectors_json"))
            except Exception:
                item["sectors"] = []
            result.append(item)
        return result

    def get_analysis_run(self, run_id: int) -> dict | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM analysis_runs WHERE id = ?",
                (run_id,),
            ).fetchone()

        if row is None:
            return None

        item = dict(row)
        item["sectors"] = json.loads(item.pop("sectors_json"))
        item["result"] = json.loads(item.pop("result_json"))
        return item

    def get_provider_results(
        self,
        run_id: int,
    ) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT provider, model, result_json, error, created_at
                FROM provider_results
                WHERE analysis_run_id = ?
                ORDER BY id
                """,
                (run_id,),
            ).fetchall()

        result = []

        for row in rows:
            item = dict(row)

            if item.get("result_json"):
                try:
                    item["result"] = json.loads(
                        item.pop("result_json")
                    )
                except Exception:
                    item["result"] = None
            else:
                item.pop("result_json", None)
                item["result"] = None

            result.append(item)

        return result

    def list_events(self, limit: int = 300) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, event_date, source, url, analysis,
                       first_seen_at, last_seen_at
                FROM events
                ORDER BY last_seen_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_event_sectors(self, event_id: int) -> list[str]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT DISTINCT sector
                FROM analysis_events
                WHERE event_id = ?
                ORDER BY sector
                """,
                (event_id,),
            ).fetchall()
        return [row["sector"] for row in rows]

    def _save_provider_results(
        self,
        conn,
        run_id: int,
        bundle: AnalysisBundle,
        created_at: str,
    ):
        for analysis in bundle.provider_analyses:
            result_json = None

            if analysis.result is not None:
                result_json = json.dumps(
                    analysis.result,
                    ensure_ascii=False,
                )

            conn.execute(
                """
                INSERT INTO provider_results(
                    analysis_run_id,
                    provider,
                    model,
                    result_json,
                    error,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    analysis.provider,
                    analysis.model,
                    result_json,
                    analysis.error,
                    created_at,
                ),
            )

    def _save_events(self, conn, run_id, bundle, created_at):
        for sector in bundle.structured.get("sectors", []):
            sector_name = str(sector.get("sector", "")).strip()

            for event in sector.get("events", []):
                title = str(event.get("title", "")).strip()
                if not title:
                    continue

                event_date = str(event.get("date", "")).strip()
                source = str(event.get("source", "")).strip()
                url = str(event.get("url", "")).strip()
                analysis = str(event.get("analysis", "")).strip()

                fingerprint = self._fingerprint(
                    title, event_date, source
                )

                conn.execute(
                    """
                    INSERT INTO events(
                        fingerprint, title, event_date, source, url,
                        analysis, first_seen_at, last_seen_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(fingerprint) DO UPDATE SET
                        url = excluded.url,
                        analysis = excluded.analysis,
                        last_seen_at = excluded.last_seen_at
                    """,
                    (
                        fingerprint, title, event_date, source, url,
                        analysis, created_at, created_at,
                    ),
                )

                event_row = conn.execute(
                    "SELECT id FROM events WHERE fingerprint = ?",
                    (fingerprint,),
                ).fetchone()

                try:
                    importance = int(event.get("importance", 0))
                except Exception:
                    importance = 0

                conn.execute(
                    """
                    INSERT INTO analysis_events(
                        analysis_run_id, event_id, sector,
                        impact, impact_type, importance
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        event_row["id"],
                        sector_name,
                        str(event.get("impact", "")),
                        str(event.get("impact_type", "")),
                        importance,
                    ),
                )

    @staticmethod
    def _fingerprint(title: str, event_date: str, source: str) -> str:
        raw = "|".join([
            title.strip().lower(),
            event_date.strip().lower(),
            source.strip().lower(),
        ])
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
