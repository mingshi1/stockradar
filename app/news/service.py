from app.database.database import Database


class NewsService:
    def __init__(self, database: Database):
        self.database = database

    def list_events(self, limit: int = 300) -> list[dict]:
        events = self.database.list_events(limit=limit)

        for event in events:
            event["sectors"] = self.database.get_event_sectors(
                event["id"]
            )

        return events
