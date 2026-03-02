from __future__ import annotations

import sys


MENU = """Commands:
  password
  encrypt
  decrypt
  history
  quit
"""


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python driver/driver.py <log_file>", file=sys.stderr)
        return 1

    print(MENU, end="")
    print("Stub driver: not implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())