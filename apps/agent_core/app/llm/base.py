from __future__ import annotations

from typing import Any, Protocol


class ProposalGenerator(Protocol):
    def generate(self, *, parsed_event: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        ...
