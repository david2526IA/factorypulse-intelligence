# FactoryPulse Intelligence

> Explainable anomaly detection over FactoryPulse silver telemetry data.

[![Intelligence CI](https://github.com/david2526IA/factorypulse-intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/david2526IA/factorypulse-intelligence/actions/workflows/ci.yml)
[![DuckDB](https://img.shields.io/badge/reads-DuckDB%20%2F%20Parquet-FFF000?logo=duckdb&logoColor=111827)](https://duckdb.org/)
[![Contracts](https://img.shields.io/badge/publishes-anomaly.v1-2563EB)](https://github.com/david2526IA/factorypulse-contracts)

FactoryPulse Intelligence reads `silver_telemetry.parquet` produced by [FactoryPulse Lakehouse](https://github.com/david2526IA/factorypulse-lakehouse), detects abnormal measurements per asset and emits validated `anomaly.v1` JSONL events for a dashboard or alerting consumer.

## Detection approach

The detector uses median absolute deviation (MAD) robust z-scores for temperature, vibration, pressure and power. Unlike a mean/stddev baseline, MAD is less distorted by the very outliers being detected. It also applies explicit critical conditions for temperature and vibration.

Every alert includes its severity, score and concrete reasons; there is no opaque "anomaly" label without evidence.

## Quick start

```bash
git clone https://github.com/david2526IA/factorypulse-intelligence.git
cd factorypulse-intelligence
python -m venv .venv
```

After generating a silver layer with FactoryPulse Lakehouse, activate the environment and run:

```bash
pip install -e ".[dev]"
factorypulse-intelligence ../factorypulse-lakehouse/artifacts/warehouse/silver_telemetry.parquet --output artifacts/anomalies.jsonl
pytest -q
```

## Integration flow

```text
FactoryPulse Ingestion → FactoryPulse Lakehouse → silver_telemetry.parquet
                                                        │
                                                        ▼
                                  robust scoring + critical rules
                                                        │
                                                        ▼
                                  validated `anomaly.v1` JSONL events
```

## Scope and safety

This project is a reproducible portfolio/reference implementation. It does not control equipment, diagnose assets or replace calibrated condition-monitoring thresholds, safety systems or expert maintenance decisions. A production model needs asset-specific baselines, validation against labelled maintenance history, drift monitoring and human review.

## License

MIT © 2026 David Falcon
