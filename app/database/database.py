import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from app.analysis.models import AnalysisBundle
from app.config.settings import APP_DATA_DIR, DATABASE_FILE
from app.report.models import ReportArtifact


class Database:
    SCHEMA_VERSION = 3

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

                CREATE TABLE IF NOT EXISTS provider_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_run_id INTEGER NOT NULL,
                    phase TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    status TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL DEFAULT 0,
                    input_tokens INTEGER NOT NULL DEFAULT 0,
                    output_tokens INTEGER NOT NULL DEFAULT 0,
                    total_tokens INTEGER NOT NULL DEFAULT 0,
                    estimated_cost REAL,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (analysis_run_id)
                        REFERENCES analysis_runs(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS saved_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_run_id INTEGER NOT NULL,
                    report_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    html_content TEXT NOT NULL,
                    markdown_content TEXT NOT NULL,
                    plain_summary TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(analysis_run_id, report_type),
                    FOREIGN KEY (analysis_run_id)
                        REFERENCES analysis_runs(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_runs_created
                ON analysis_runs(created_at DESC);

                CREATE INDEX IF NOT EXISTS idx_events_seen
                ON events(last_seen_at DESC);

                CREATE INDEX IF NOT EXISTS idx_provider_results_run
                ON provider_results(analysis_run_id);

                CREATE INDEX IF NOT EXISTS idx_provider_calls_run
                ON provider_calls(analysis_run_id);

                CREATE INDEX IF NOT EXISTS idx_provider_calls_provider
                ON provider_calls(provider, phase, status);

                CREATE INDEX IF NOT EXISTS idx_reports_run
                ON saved_reports(analysis_run_id);

                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    run_time TEXT NOT NULL,
                    sectors_json TEXT NOT NULL,
                    analysis_mode TEXT NOT NULL DEFAULT 'current',
                    report_type TEXT NOT NULL DEFAULT 'morning',
                    generate_pdf INTEGER NOT NULL DEFAULT 1,
                    report_directory TEXT NOT NULL DEFAULT '',
                    email_enabled INTEGER NOT NULL DEFAULT 0,
                    email_recipients TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_run_at TEXT,
                    last_status TEXT
                );

                CREATE TABLE IF NOT EXISTS task_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    status TEXT NOT NULL,
                    analysis_run_id INTEGER,
                    report_id INTEGER,
                    email_status TEXT NOT NULL DEFAULT 'not_requested',
                    error TEXT,
                    FOREIGN KEY (task_id)
                        REFERENCES scheduled_tasks(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_task_runs_task
                ON task_runs(task_id, id DESC);

                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );
            """)

            self._apply_schema_version(conn)


    def _apply_schema_version(
        self,
        conn,
    ):
        current = int(
            conn.execute(
                "PRAGMA user_version"
            ).fetchone()[0]
        )

        if current < 1:
            now = datetime.now().isoformat(
                timespec="seconds"
            )

            conn.execute(
                """
                INSERT OR IGNORE INTO schema_migrations(
                    version,
                    applied_at
                )
                VALUES (?, ?)
                """,
                (
                    1,
                    now,
                ),
            )
            current = 1

        if current < 2:
            now = datetime.now().isoformat(
                timespec="seconds"
            )

            conn.execute(
                """
                INSERT OR IGNORE INTO schema_migrations(
                    version,
                    applied_at
                )
                VALUES (?, ?)
                """,
                (
                    2,
                    now,
                ),
            )
            current = 2

        if current < 3:
            columns = {
                row["name"]
                for row in conn.execute(
                    "PRAGMA table_info(scheduled_tasks)"
                ).fetchall()
            }

            if "report_directory" not in columns:
                conn.execute(
                    """
                    ALTER TABLE scheduled_tasks
                    ADD COLUMN report_directory
                    TEXT NOT NULL DEFAULT ''
                    """
                )

            now = datetime.now().isoformat(
                timespec="seconds"
            )

            conn.execute(
                """
                INSERT OR IGNORE INTO schema_migrations(
                    version,
                    applied_at
                )
                VALUES (?, ?)
                """,
                (
                    3,
                    now,
                ),
            )
            current = 3

        conn.execute(
            f"PRAGMA user_version = {self.SCHEMA_VERSION}"
        )

    def schema_version(self) -> int:
        with self.connect() as conn:
            return int(
                conn.execute(
                    "PRAGMA user_version"
                ).fetchone()[0]
            )

    def backup_database(
        self,
        destination: Path,
    ):
        destination = Path(destination)
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        source = sqlite3.connect(
            self.db_path
        )
        target = sqlite3.connect(
            destination
        )

        try:
            source.backup(target)
            target.commit()
        finally:
            target.close()
            source.close()

    def validate_database_file(
        self,
        source_path: Path,
    ) -> tuple[bool, str]:
        source_path = Path(
            source_path
        )

        if not source_path.exists():
            return (
                False,
                "备份文件不存在。",
            )

        try:
            conn = sqlite3.connect(
                source_path
            )
            conn.row_factory = sqlite3.Row

            tables = {
                row["name"]
                for row in conn.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                    """
                ).fetchall()
            }

            required = {
                "analysis_runs",
                "events",
                "custom_sectors",
            }

            if not required.issubset(
                tables
            ):
                return (
                    False,
                    "这不是有效的 StockEventRadar 数据库备份。",
                )

            conn.close()
        except Exception as exc:
            return (
                False,
                f"无法读取备份数据库：{exc}",
            )

        return (
            True,
            "数据库备份有效。",
        )

    def restore_database(
        self,
        source_path: Path,
    ):
        source_path = Path(
            source_path
        )

        valid, message = (
            self.validate_database_file(
                source_path
            )
        )

        if not valid:
            raise RuntimeError(
                message
            )

        source = sqlite3.connect(
            source_path
        )
        target = sqlite3.connect(
            self.db_path
        )

        try:
            source.backup(target)
            target.commit()
        finally:
            target.close()
            source.close()

        self.initialize()

    # =========================================================
    # Custom sectors
    # =========================================================

    def add_custom_sector(self, name: str) -> bool:
        name = " ".join(name.strip().split())

        if not name:
            return False

        try:
            with self.connect() as conn:
                conn.execute(
                    """
                    INSERT INTO custom_sectors(name, created_at)
                    VALUES (?, ?)
                    """,
                    (
                        name,
                        datetime.now().isoformat(timespec="seconds"),
                    ),
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

    # =========================================================
    # Analysis history
    # =========================================================

    def save_analysis(self, bundle: AnalysisBundle) -> int:
        created_at = bundle.generated_at.isoformat(
            timespec="seconds"
        )

        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO analysis_runs(
                    created_at,
                    provider,
                    model,
                    sectors_json,
                    market_summary,
                    result_json,
                    research_text
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    bundle.provider,
                    bundle.model,
                    json.dumps(
                        bundle.sectors,
                        ensure_ascii=False,
                    ),
                    str(
                        bundle.structured.get(
                            "market_summary",
                            "",
                        )
                    ),
                    json.dumps(
                        bundle.structured,
                        ensure_ascii=False,
                    ),
                    bundle.research_text,
                ),
            )

            run_id = int(cursor.lastrowid)

            self._save_events(
                conn,
                run_id,
                bundle,
                created_at,
            )
            self._save_provider_results(
                conn,
                run_id,
                bundle,
                created_at,
            )
            self._save_provider_calls(
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
                item["sectors"] = json.loads(
                    item.pop("sectors_json")
                )
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

        item["sectors"] = json.loads(
            item.pop("sectors_json")
        )
        item["result"] = json.loads(
            item.pop("result_json")
        )

        return item

    def get_provider_results(
        self,
        run_id: int,
    ) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    provider,
                    model,
                    result_json,
                    error,
                    created_at
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

    def get_provider_calls(
        self,
        run_id: int,
    ) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM provider_calls
                WHERE analysis_run_id = ?
                ORDER BY id
                """,
                (run_id,),
            ).fetchall()

        return [dict(row) for row in rows]

    # =========================================================
    # Provider statistics
    # =========================================================

    def list_provider_stats(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    provider,
                    COUNT(*) AS call_count,
                    SUM(
                        CASE
                            WHEN status = 'success' THEN 1
                            ELSE 0
                        END
                    ) AS success_count,
                    AVG(
                        CASE
                            WHEN status = 'success' THEN duration_ms
                            ELSE NULL
                        END
                    ) AS avg_duration_ms,
                    SUM(input_tokens) AS input_tokens,
                    SUM(output_tokens) AS output_tokens,
                    SUM(total_tokens) AS total_tokens,
                    SUM(
                        CASE
                            WHEN estimated_cost IS NOT NULL
                            THEN estimated_cost
                            ELSE 0
                        END
                    ) AS estimated_cost,
                    SUM(
                        CASE
                            WHEN estimated_cost IS NOT NULL
                            THEN 1
                            ELSE 0
                        END
                    ) AS priced_call_count
                FROM provider_calls
                WHERE phase IN ('research', 'analysis', 'judge')
                GROUP BY provider
                ORDER BY call_count DESC, provider
                """
            ).fetchall()

        return [dict(row) for row in rows]

    # =========================================================
    # Sector trend
    # =========================================================

    def list_sector_names(self) -> list[str]:
        names = set(
            self.list_custom_sectors()
        )

        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT result_json
                FROM analysis_runs
                ORDER BY id DESC
                LIMIT 500
                """
            ).fetchall()

        for row in rows:
            try:
                data = json.loads(
                    row["result_json"]
                )
            except Exception:
                continue

            for sector in data.get(
                "sectors",
                [],
            ):
                name = str(
                    sector.get(
                        "sector",
                        "",
                    )
                ).strip()

                if name:
                    names.add(name)

        return sorted(names)

    def list_sector_trends(
        self,
        sector_name: str,
        limit: int = 30,
    ) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    id,
                    created_at,
                    result_json
                FROM analysis_runs
                ORDER BY id DESC
                LIMIT 500
                """
            ).fetchall()

        target = sector_name.strip().lower()
        result = []

        for row in rows:
            try:
                data = json.loads(
                    row["result_json"]
                )
            except Exception:
                continue

            match = None

            for sector in data.get(
                "sectors",
                [],
            ):
                name = str(
                    sector.get(
                        "sector",
                        "",
                    )
                ).strip()

                if name.lower() == target:
                    match = sector
                    break

            if match is None:
                continue

            result.append(
                {
                    "run_id": row["id"],
                    "created_at": row["created_at"],
                    "score": self._safe_float(
                        match.get("score", 0)
                    ),
                    "agreement": self._safe_float(
                        match.get("agreement", 0)
                    ),
                    "confidence": self._safe_float(
                        match.get("confidence", 0)
                    ),
                    "direction": str(
                        match.get(
                            "direction",
                            "",
                        )
                    ),
                    "event_count": len(
                        match.get(
                            "events",
                            [],
                        )
                    ),
                }
            )

            if len(result) >= limit:
                break

        result.reverse()
        return result

    # =========================================================
    # Event Pool
    # =========================================================

    def list_events(self, limit: int = 300) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    id,
                    title,
                    event_date,
                    source,
                    url,
                    analysis,
                    first_seen_at,
                    last_seen_at
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


    # =========================================================
    # Scheduled automation
    # =========================================================

    def save_scheduled_task(
        self,
        payload: dict,
    ) -> int:
        now = datetime.now().isoformat(
            timespec="seconds"
        )

        sectors = [
            str(item).strip()
            for item in payload.get(
                "sectors",
                [],
            )
            if str(item).strip()
        ]

        if not sectors:
            raise ValueError(
                "自动任务至少需要一个板块。"
            )

        task_id = payload.get("id")

        values = (
            str(
                payload.get(
                    "name",
                    "每日任务",
                )
            ).strip()
            or "每日任务",
            1 if payload.get("enabled") else 0,
            str(
                payload.get(
                    "run_time",
                    "07:30",
                )
            ),
            json.dumps(
                sectors,
                ensure_ascii=False,
            ),
            str(
                payload.get(
                    "analysis_mode",
                    "current",
                )
            ),
            str(
                payload.get(
                    "report_type",
                    "morning",
                )
            ),
            1 if payload.get("generate_pdf") else 0,
            str(
                payload.get(
                    "report_directory",
                    "",
                )
            ).strip(),
            0,
            "",
        )

        with self.connect() as conn:
            if task_id:
                conn.execute(
                    """
                    UPDATE scheduled_tasks
                    SET
                        name = ?,
                        enabled = ?,
                        run_time = ?,
                        sectors_json = ?,
                        analysis_mode = ?,
                        report_type = ?,
                        generate_pdf = ?,
                        report_directory = ?,
                        email_enabled = ?,
                        email_recipients = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        *values,
                        now,
                        int(task_id),
                    ),
                )

                row = conn.execute(
                    """
                    SELECT id
                    FROM scheduled_tasks
                    WHERE id = ?
                    """,
                    (int(task_id),),
                ).fetchone()

                if row is None:
                    raise ValueError(
                        "要更新的自动任务不存在。"
                    )

                return int(row["id"])

            cursor = conn.execute(
                """
                INSERT INTO scheduled_tasks(
                    name,
                    enabled,
                    run_time,
                    sectors_json,
                    analysis_mode,
                    report_type,
                    generate_pdf,
                    report_directory,
                    email_enabled,
                    email_recipients,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    *values,
                    now,
                    now,
                ),
            )

            return int(cursor.lastrowid)

    def delete_scheduled_task(
        self,
        task_id: int,
    ):
        with self.connect() as conn:
            conn.execute(
                """
                DELETE FROM scheduled_tasks
                WHERE id = ?
                """,
                (int(task_id),),
            )

    def list_scheduled_tasks(
        self,
    ) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM scheduled_tasks
                ORDER BY enabled DESC, run_time, id
                """
            ).fetchall()

        return [
            self._decode_task_row(row)
            for row in rows
        ]

    def get_scheduled_task(
        self,
        task_id: int,
    ) -> dict | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM scheduled_tasks
                WHERE id = ?
                """,
                (int(task_id),),
            ).fetchone()

        if row is None:
            return None

        return self._decode_task_row(row)

    @staticmethod
    def _decode_task_row(
        row,
    ) -> dict:
        item = dict(row)

        try:
            item["sectors"] = json.loads(
                item.pop("sectors_json")
            )
        except Exception:
            item.pop("sectors_json", None)
            item["sectors"] = []

        for key in (
            "enabled",
            "generate_pdf",
            "email_enabled",
        ):
            item[key] = bool(
                item.get(key)
            )

        return item

    def start_task_run(
        self,
        task_id: int,
    ) -> int:
        now = datetime.now().isoformat(
            timespec="seconds"
        )

        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO task_runs(
                    task_id,
                    started_at,
                    status,
                    email_status
                )
                VALUES (?, ?, 'running', 'not_requested')
                """,
                (
                    int(task_id),
                    now,
                ),
            )

            conn.execute(
                """
                UPDATE scheduled_tasks
                SET
                    last_run_at = ?,
                    last_status = 'running'
                WHERE id = ?
                """,
                (
                    now,
                    int(task_id),
                ),
            )

            return int(cursor.lastrowid)

    def finish_task_run(
        self,
        *,
        task_run_id: int,
        task_id: int,
        status: str,
        analysis_run_id: int | None,
        report_id: int | None,
        email_status: str,
        error: str | None,
    ):
        now = datetime.now().isoformat(
            timespec="seconds"
        )

        with self.connect() as conn:
            conn.execute(
                """
                UPDATE task_runs
                SET
                    finished_at = ?,
                    status = ?,
                    analysis_run_id = ?,
                    report_id = ?,
                    email_status = ?,
                    error = ?
                WHERE id = ?
                """,
                (
                    now,
                    status,
                    analysis_run_id,
                    report_id,
                    email_status,
                    error,
                    int(task_run_id),
                ),
            )

            conn.execute(
                """
                UPDATE scheduled_tasks
                SET
                    last_run_at = ?,
                    last_status = ?,
                    updated_at = updated_at
                WHERE id = ?
                """,
                (
                    now,
                    status,
                    int(task_id),
                ),
            )

    def list_task_runs(
        self,
        limit: int = 100,
    ) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    tr.*,
                    st.name AS task_name
                FROM task_runs tr
                JOIN scheduled_tasks st
                  ON st.id = tr.task_id
                ORDER BY tr.id DESC
                LIMIT ?
                """,
                (int(limit),),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    # =========================================================
    # Saved reports
    # =========================================================

    def save_report(
        self,
        analysis_run_id: int,
        artifact: ReportArtifact,
    ) -> int:
        now = datetime.now().isoformat(
            timespec="seconds"
        )

        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO saved_reports(
                    analysis_run_id,
                    report_type,
                    title,
                    html_content,
                    markdown_content,
                    plain_summary,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(analysis_run_id, report_type)
                DO UPDATE SET
                    title = excluded.title,
                    html_content = excluded.html_content,
                    markdown_content = excluded.markdown_content,
                    plain_summary = excluded.plain_summary,
                    updated_at = excluded.updated_at
                """,
                (
                    analysis_run_id,
                    artifact.report_type,
                    artifact.title,
                    artifact.html,
                    artifact.markdown,
                    artifact.plain_summary,
                    now,
                    now,
                ),
            )

            row = conn.execute(
                """
                SELECT id
                FROM saved_reports
                WHERE analysis_run_id = ?
                  AND report_type = ?
                """,
                (
                    analysis_run_id,
                    artifact.report_type,
                ),
            ).fetchone()

        return int(row["id"])

    def list_saved_reports(
        self,
        limit: int = 100,
    ) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    sr.id,
                    sr.analysis_run_id,
                    sr.report_type,
                    sr.title,
                    sr.created_at,
                    sr.updated_at
                FROM saved_reports sr
                ORDER BY sr.updated_at DESC, sr.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def get_saved_report(
        self,
        report_id: int,
    ) -> dict | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM saved_reports
                WHERE id = ?
                """,
                (report_id,),
            ).fetchone()

        return dict(row) if row else None

    # =========================================================
    # Internal save helpers
    # =========================================================

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

    def _save_provider_calls(
        self,
        conn,
        run_id: int,
        bundle: AnalysisBundle,
        created_at: str,
    ):
        for metric in bundle.call_metrics:
            conn.execute(
                """
                INSERT INTO provider_calls(
                    analysis_run_id,
                    phase,
                    provider,
                    model,
                    status,
                    duration_ms,
                    input_tokens,
                    output_tokens,
                    total_tokens,
                    estimated_cost,
                    error,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    metric.phase,
                    metric.provider,
                    metric.model,
                    metric.status,
                    metric.duration_ms,
                    metric.input_tokens,
                    metric.output_tokens,
                    metric.total_tokens,
                    metric.estimated_cost,
                    metric.error,
                    created_at,
                ),
            )

    def _save_events(
        self,
        conn,
        run_id: int,
        bundle: AnalysisBundle,
        created_at: str,
    ):
        for sector in bundle.structured.get(
            "sectors",
            [],
        ):
            sector_name = str(
                sector.get(
                    "sector",
                    "",
                )
            ).strip()

            for event in sector.get(
                "events",
                [],
            ):
                title = str(
                    event.get(
                        "title",
                        "",
                    )
                ).strip()

                if not title:
                    continue

                event_date = str(
                    event.get(
                        "date",
                        "",
                    )
                ).strip()
                source = str(
                    event.get(
                        "source",
                        "",
                    )
                ).strip()
                url = str(
                    event.get(
                        "url",
                        "",
                    )
                ).strip()
                analysis = str(
                    event.get(
                        "analysis",
                        "",
                    )
                ).strip()

                fingerprint = self._fingerprint(
                    title,
                    event_date,
                    source,
                )

                conn.execute(
                    """
                    INSERT INTO events(
                        fingerprint,
                        title,
                        event_date,
                        source,
                        url,
                        analysis,
                        first_seen_at,
                        last_seen_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(fingerprint)
                    DO UPDATE SET
                        url = excluded.url,
                        analysis = excluded.analysis,
                        last_seen_at = excluded.last_seen_at
                    """,
                    (
                        fingerprint,
                        title,
                        event_date,
                        source,
                        url,
                        analysis,
                        created_at,
                        created_at,
                    ),
                )

                event_row = conn.execute(
                    """
                    SELECT id
                    FROM events
                    WHERE fingerprint = ?
                    """,
                    (fingerprint,),
                ).fetchone()

                try:
                    importance = int(
                        event.get(
                            "importance",
                            0,
                        )
                    )
                except Exception:
                    importance = 0

                conn.execute(
                    """
                    INSERT INTO analysis_events(
                        analysis_run_id,
                        event_id,
                        sector,
                        impact,
                        impact_type,
                        importance
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        event_row["id"],
                        sector_name,
                        str(
                            event.get(
                                "impact",
                                "",
                            )
                        ),
                        str(
                            event.get(
                                "impact_type",
                                "",
                            )
                        ),
                        importance,
                    ),
                )

    @staticmethod
    def _fingerprint(
        title: str,
        event_date: str,
        source: str,
    ) -> str:
        raw = "|".join([
            title.strip().lower(),
            event_date.strip().lower(),
            source.strip().lower(),
        ])

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _safe_float(value) -> float:
        try:
            return float(value)
        except Exception:
            return 0.0
