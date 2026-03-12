from datetime import datetime, timezone

from libs.contracts.event import EventIn

from apps.ingestion_service.app.adapters.base import ProviderAdapter


class MockNewsAdapter(ProviderAdapter):
    async def fetch(self, limit: int = 5) -> list[EventIn]:
        samples = [
            EventIn(
                source="mock_news",
                event_type="macro",
                title="PBOC announces targeted liquidity support",
                content="Policy tools target credit easing for real economy sectors.",
                asset_scope=["CN10Y", "CNY", "banking"],
                impact_direction="positive",
                confidence=0.73,
                raw_payload={"source_url": "mock://macro/1"},
                occurred_at=datetime.now(timezone.utc),
            ),
            EventIn(
                source="mock_news",
                event_type="commodity",
                title="South America weather risk rises for soybean supply",
                content="Extended drought may reduce output and tighten global stocks.",
                asset_scope=["soybean", "meal", "oil"],
                impact_direction="positive",
                confidence=0.81,
                raw_payload={"source_url": "mock://commodity/1"},
                occurred_at=datetime.now(timezone.utc),
            ),
            EventIn(
                source="mock_news",
                event_type="equity",
                title="Semiconductor capex guidance revised upward",
                content="Leading chip manufacturers raised equipment spending outlook.",
                asset_scope=["semiconductor", "A-share-tech"],
                impact_direction="positive",
                confidence=0.67,
                raw_payload={"source_url": "mock://equity/1"},
                occurred_at=datetime.now(timezone.utc),
            ),
        ]
        return samples[:limit]
