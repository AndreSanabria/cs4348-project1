from __future__ import annotations

import sys


def main() -> int:
    for raw_line in sys.stdin:
        line = raw_line.rstrip("\r\n")
        if not line.strip():
            continue
        if line.strip().upper() == "QUIT":
            break
        print("ERROR Not implemented", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())