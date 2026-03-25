from __future__ import annotations

from datetime import timezone
from uuid import uuid4

from libs.contracts.watch import IntradayWatchRequest, MarketSnapshot, WatchObservation


def run_intraday_watch(payload: IntradayWatchRequest | None = None) -> dict:
    request = payload or IntradayWatchRequest()
    if request.input_mode != "mock_replay":
        return {
            "status": "blocked",
            "reason": "unsupported_input_mode",
            "message": "intraday-watch baseline currently supports mock_replay input only.",
            "input_mode": request.input_mode,
        }

    if not request.snapshots:
        return {
            "status": "blocked",
            "reason": "no_market_input",
            "message": "intraday-watch baseline needs at least one controlled market snapshot.",
            "input_mode": request.input_mode,
        }

    observations: list[WatchObservation] = []
    suppressed: list[dict] = []
    last_emitted_at: dict[str, object] = {}

    snapshots = sorted(request.snapshots, key=lambda item: item.observed_at)
    for snapshot in snapshots:
        for observation in _evaluate_snapshot(snapshot, request):
            previous = last_emitted_at.get(observation.dedup_key)
            if previous is not None:
                delta_seconds = (observation.observed_at - previous).total_seconds()
                if delta_seconds < request.suppression_window_minutes * 60:
                    suppressed.append(
                        {
                            "asset": snapshot.asset,
                            "trigger_type": observation.trigger_type,
                            "dedup_key": observation.dedup_key,
                            "observed_at": observation.observed_at.isoformat(),
                        }
                    )
                    continue
            last_emitted_at[observation.dedup_key] = observation.observed_at
            observations.append(observation)

    return {
        "status": "success",
        "input_mode": request.input_mode,
        "evaluated_snapshot_count": len(snapshots),
        "observation_count": len(observations),
        "suppressed_count": len(suppressed),
        "observations": [item.model_dump(mode="json") for item in observations],
        "suppressed": suppressed,
    }


def _evaluate_snapshot(snapshot: MarketSnapshot, request: IntradayWatchRequest) -> list[WatchObservation]:
    observations: list[WatchObservation] = []

    price_change_pct = ((snapshot.last_price - snapshot.prev_close) / snapshot.prev_close) * 100
    session_range_pct = ((snapshot.session_high - snapshot.session_low) / snapshot.prev_close) * 100
    volume_ratio = snapshot.volume / snapshot.average_volume if snapshot.average_volume else 0.0

    if abs(price_change_pct) >= request.price_change_threshold_pct:
        direction = "up" if price_change_pct >= 0 else "down"
        observations.append(
            _build_observation(
                snapshot=snapshot,
                trigger_type="price_breakout",
                direction_or_bucket=direction,
                severity="high" if abs(price_change_pct) >= request.price_change_threshold_pct * 1.5 else "medium",
                summary=(
                    f"{snapshot.asset} price moved {price_change_pct:.2f}% versus prev close, "
                    f"crossing the {request.price_change_threshold_pct:.2f}% baseline."
                ),
                follow_up_action="research" if abs(price_change_pct) >= request.price_change_threshold_pct * 1.5 else "notify",
                routing_targets=_routing_targets(request.routing_targets, prefer_research=abs(price_change_pct) >= request.price_change_threshold_pct * 1.5),
                evidence={
                    "price_change_pct": round(price_change_pct, 4),
                    "last_price": snapshot.last_price,
                    "prev_close": snapshot.prev_close,
                    "threshold_pct": request.price_change_threshold_pct,
                },
            )
        )

    if session_range_pct >= request.session_range_threshold_pct:
        observations.append(
            _build_observation(
                snapshot=snapshot,
                trigger_type="volatility_expansion",
                direction_or_bucket="range",
                severity="high" if session_range_pct >= request.session_range_threshold_pct * 1.5 else "medium",
                summary=(
                    f"{snapshot.asset} intraday range reached {session_range_pct:.2f}%, "
                    f"crossing the {request.session_range_threshold_pct:.2f}% volatility baseline."
                ),
                follow_up_action="notify",
                routing_targets=_routing_targets(request.routing_targets, prefer_research=False),
                evidence={
                    "session_range_pct": round(session_range_pct, 4),
                    "session_high": snapshot.session_high,
                    "session_low": snapshot.session_low,
                    "prev_close": snapshot.prev_close,
                    "threshold_pct": request.session_range_threshold_pct,
                },
            )
        )

    if volume_ratio >= request.volume_spike_ratio:
        observations.append(
            _build_observation(
                snapshot=snapshot,
                trigger_type="volume_spike",
                direction_or_bucket="elevated",
                severity="medium",
                summary=(
                    f"{snapshot.asset} volume ratio reached {volume_ratio:.2f}x average, "
                    f"crossing the {request.volume_spike_ratio:.2f}x baseline."
                ),
                follow_up_action="notify",
                routing_targets=_routing_targets(request.routing_targets, prefer_research=False),
                evidence={
                    "volume_ratio": round(volume_ratio, 4),
                    "volume": snapshot.volume,
                    "average_volume": snapshot.average_volume,
                    "threshold_ratio": request.volume_spike_ratio,
                },
            )
        )

    return observations


def _build_observation(
    *,
    snapshot: MarketSnapshot,
    trigger_type: str,
    direction_or_bucket: str,
    severity: str,
    summary: str,
    follow_up_action: str,
    routing_targets: list[str],
    evidence: dict,
) -> WatchObservation:
    observed_at = snapshot.observed_at.astimezone(timezone.utc)
    dedup_key = f"{snapshot.asset}:{trigger_type}:{direction_or_bucket}"
    return WatchObservation(
        id=uuid4(),
        asset_scope=[snapshot.asset],
        source=snapshot.source,
        observed_at=observed_at,
        trigger_type=trigger_type,
        severity=severity,
        summary=summary,
        dedup_key=dedup_key,
        evidence=evidence,
        follow_up_action=follow_up_action,
        routing_targets=routing_targets,
        metadata={"snapshot_metadata": snapshot.metadata},
        created_at=observed_at,
    )


def _routing_targets(default_targets: list[str], *, prefer_research: bool) -> list[str]:
    targets = list(default_targets)
    if prefer_research and "research" not in targets:
        targets.append("research")
    return targets
