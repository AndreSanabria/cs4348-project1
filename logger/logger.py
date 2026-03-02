from __future__ import annotations

from datetime import datetime
import sys


def parse_log_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped:
        return None

    action, _, message = stripped.partition(" ")
    return action, message.lstrip()


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python logger/logger.py <log_file>", file=sys.stderr)
        return 1

    log_path = sys.argv[1]

    with open(log_path, "a", encoding="utf-8") as log_file:
        for raw_line in sys.stdin:
            line = raw_line.rstrip("\r\n")

            if line.strip().upper() == "QUIT":
                break

            parsed = parse_log_line(line)
            if parsed is None:
                continue

            action, message = parsed
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

            if message:
                log_file.write(f"{timestamp} [{action}] {message}\n")
            else:
                log_file.write(f"{timestamp} [{action}]\n")

            log_file.flush()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())