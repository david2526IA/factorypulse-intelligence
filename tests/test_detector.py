import json
import uuid

import duckdb

from factorypulse_contracts import validate_event

from factorypulse_intelligence.pipeline import analyse_parquet


def test_pipeline_publishes_valid_explainable_anomaly(tmp_path) -> None:
    events = []
    for index in range(10):
        abnormal = index >= 8
        events.append((str(uuid.uuid4()), f"2026-01-01T00:{index:02d}:00Z", "PUMP-01", 63 + (31 if abnormal else 0), 2.5 + (10 if abnormal else 0), 7.4, 18.0))
    parquet = tmp_path / "silver.parquet"
    connection = duckdb.connect()
    connection.execute("CREATE TABLE telemetry(event_id VARCHAR, occurred_at TIMESTAMPTZ, asset_id VARCHAR, temperature_c DOUBLE, vibration_mm_s DOUBLE, pressure_bar DOUBLE, power_kw DOUBLE)")
    connection.executemany("INSERT INTO telemetry VALUES (?, ?, ?, ?, ?, ?, ?)", events)
    path = str(parquet).replace("'", "''")
    connection.execute(f"COPY telemetry TO '{path}' (FORMAT PARQUET)")
    connection.close()
    output = tmp_path / "anomalies.jsonl"
    result = analyse_parquet(parquet, output)
    anomalies = [json.loads(line) for line in output.read_text().splitlines()]
    assert result["anomalies"] == 2
    assert result["critical"] == 2
    assert "vibration critical" in " ".join(anomalies[0]["reasons"])
    for anomaly in anomalies:
        validate_event("anomaly.v1", anomaly)
