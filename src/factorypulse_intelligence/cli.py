from __future__ import annotations

import argparse

from .pipeline import analyse_parquet


def main() -> None:
    parser = argparse.ArgumentParser(prog="factorypulse-intelligence")
    parser.add_argument("input", help="silver_telemetry.parquet from factorypulse-lakehouse")
    parser.add_argument("--output", default="artifacts/anomalies.jsonl")
    args = parser.parse_args()
    print(analyse_parquet(args.input, args.output))


if __name__ == "__main__":
    main()
