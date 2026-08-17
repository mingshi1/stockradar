from __future__ import annotations

import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from app.database.database import Database


def main():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = (
            Path(tmp)
            / "scheduled-task-test.sqlite"
        )

        database = Database(
            db_path
        )

        payload = {
            "id": None,
            "name": "Android save regression test",
            "enabled": True,
            "run_time": "07:30",
            "sectors": [
                "白酒/食品饮料"
            ],
            "analysis_mode": "current",
            "report_type": "morning",
            "generate_pdf": True,
            "report_directory": "",
        }

        task_id = database.save_scheduled_task(
            payload
        )

        assert task_id > 0

        rows = database.list_scheduled_tasks()

        assert len(rows) == 1
        assert rows[0]["id"] == task_id
        assert rows[0]["name"] == payload["name"]
        assert rows[0]["sectors"] == payload["sectors"]

        payload["id"] = task_id
        payload["name"] = (
            "Android save update test"
        )

        updated_id = database.save_scheduled_task(
            payload
        )

        assert updated_id == task_id

        rows = database.list_scheduled_tasks()

        assert len(rows) == 1
        assert rows[0]["name"] == payload["name"]

        print(
            "Scheduled task SQLite save/update test: OK"
        )


if __name__ == "__main__":
    main()
