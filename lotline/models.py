from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


ExposureType = Literal["DIRECT", "CROSS_CONTACT"]


@dataclass(frozen=True)
class EvidencePath:
    evidence_id: str
    exposure_type: ExposureType
    nodes: list[str]
    relationships: list[str]
    reason: str
    query_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Exposure:
    lot_id: str
    sku: str
    exposure_type: ExposureType
    evidence: EvidencePath


@dataclass(frozen=True)
class AlertInput:
    alert_id: str
    ingredient_lot_id: str
    hazard: str
    severity: Literal["low", "medium", "high"]
    description: str = ""


@dataclass
class ActionResult:
    case_id: str
    status: str
    new_effects: int
    existing_effects: int
    effects: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
