"""Robust per-asset anomaly scoring with reasons suitable for operations review."""

from __future__ import annotations

from collections import defaultdict
from statistics import median


METRICS = ("temperature_c", "vibration_mm_s", "pressure_bar", "power_kw")


def _robust_z(value: float, baseline: list[float]) -> float:
    center = median(baseline)
    mad = median([abs(item - center) for item in baseline])
    if mad == 0:
        return 0.0 if value == center else float("inf")
    return 0.6745 * (value - center) / mad


def detect(rows: list[dict[str, object]], warning_threshold: float = 3.5, critical_threshold: float = 6.0) -> list[dict[str, object]]:
    """Return explainable detections; no model is allowed to silently alert."""
    by_asset: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_asset[str(row["asset_id"])].append(row)
    findings: list[dict[str, object]] = []
    for asset, asset_rows in by_asset.items():
        if len(asset_rows) < 8:
            continue
        baselines = {metric: [float(row[metric]) for row in asset_rows] for metric in METRICS}
        for row in asset_rows:
            reasons, scores = [], []
            for metric in METRICS:
                score = _robust_z(float(row[metric]), baselines[metric])
                if abs(score) >= warning_threshold:
                    reasons.append(f"{metric} robust-z={score:.2f}")
                    scores.append(abs(score))
            if float(row["temperature_c"]) >= 92:
                reasons.append(f"temperature critical ({float(row['temperature_c']):.1f} °C)")
            if float(row["vibration_mm_s"]) >= 11:
                reasons.append(f"vibration critical ({float(row['vibration_mm_s']):.1f} mm/s)")
            if not reasons:
                continue
            score = max(scores, default=critical_threshold)
            severity = "critical" if score >= critical_threshold or float(row["temperature_c"]) >= 92 or float(row["vibration_mm_s"]) >= 11 else "warning"
            findings.append({"asset_id": asset, "occurred_at": row["occurred_at"], "severity": severity, "score": round(score, 3), "reasons": reasons})
    return sorted(findings, key=lambda finding: str(finding["occurred_at"]))
