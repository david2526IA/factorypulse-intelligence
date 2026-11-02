from __future__ import annotations

import json
import uuid
from pathlib import Path

import duckdb

from factorypulse_contracts import validate_event

from .detector import detect


def analyse_parquet(source: str | Path, output: str | Path) -> dict[str, object]:
    """Read lakehouse silver Parquet and publish validated anomaly event JSONL."""
    source_path, output_path = Path(source).resolve(), Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    source_sql = str(source_path).replace("'", "''")
    connection = duckdb.connect()
    try:
        # Format in UTC inside DuckDB so events have portable ISO 8601 times
        # without requiring optional timezone packages in the host Python.
        columns = "event_id, strftime(occurred_at AT TIME ZONE 'UTC', '%Y-%m-%dT%H:%M:%SZ') AS occurred_at, asset_id, temperature_c, vibration_mm_s, pressure_bar, power_kw"
        cursor = connection.execute(f"SELECT {columns} FROM read_parquet('{source_sql}') ORDER BY occurred_at")
        names = [description[0] for description in cursor.description]
        rows = [dict(zip(names, values)) for values in cursor.fetchall()]
    finally:
        connection.close()
    findings = detect(rows)
    events = []
    for finding in findings:
        event = {
            "event_id": str(uuid.uuid4()), "event_type": "factorypulse.anomaly", "schema_version": "1.0",
            "occurred_at": str(finding["occurred_at"]).replace("+00:00", "Z"), "asset_id": finding["asset_id"],
            "severity": finding["severity"], "score": finding["score"], "reasons": finding["reasons"],
        }
        validate_event("anomaly.v1", event)
        events.append(event)
    output_path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
    return {"input_readings": len(rows), "anomalies": len(events), "critical": sum(event["severity"] == "critical" for event in events), "output": str(output_path)}
