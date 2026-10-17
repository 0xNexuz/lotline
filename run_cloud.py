from __future__ import annotations

import json
import os
from pathlib import Path


ALLOWED_KEYS = {
    "FALKORDB_URL",
    "FALKORDB_HOST",
    "FALKORDB_PORT",
    "FALKORDB_USERNAME",
    "FALKORDB_PASSWORD",
    "FALKORDB_TLS",
    "FALKORDB_GRAPH",
    "FALKORDB_TIMEOUT_SECONDS",
}


def load_local_env() -> None:
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in ALLOWED_KEYS:
            continue
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def main() -> None:
    load_local_env()
    if not (os.environ.get("FALKORDB_URL") or os.environ.get("FALKORDB_HOST")):
        raise SystemExit(
            "Cloud connection missing. Create an ignored .env file containing FALKORDB_URL."
        )
    from cloud_demo import run

    evidence = run()
    path = Path(__file__).parent / "evidence" / "cloud-demo-run.json"
    path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    print(f"\nCloud evidence written to {path}")


if __name__ == "__main__":
    main()
