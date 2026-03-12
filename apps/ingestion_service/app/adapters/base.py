from abc import ABC, abstractmethod

from libs.contracts.event import EventIn


class ProviderAdapter(ABC):
    @abstractmethod
    async def fetch(self, limit: int = 5) -> list[EventIn]:
        raise NotImplementedError
