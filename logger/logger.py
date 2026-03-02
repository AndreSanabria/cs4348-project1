from __future__ import annotations

import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python logger/logger.py <log_file>", file=sys.stderr)
        return 1

    log_path = sys.argv[1]

    with open(log_path, "a", encoding="utf-8"):
        pass

    print("Stub logger: not implemented yet.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())