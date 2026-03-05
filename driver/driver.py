from __future__ import annotations

from pathlib import Path
import subprocess
import sys


MENU = """Commands:
  password
  encrypt
  decrypt
  history
  quit
"""


def send_logger_message(process: subprocess.Popen[str], action: str, message: str) -> None:
    if process.stdin is None or process.poll() is not None:
        raise RuntimeError("Logger process is not available")

    process.stdin.write(f"{action} {message}\n")
    process.stdin.flush()


def send_encryption_command(
    process: subprocess.Popen[str],
    command: str,
    argument: str = "",
) -> tuple[str, str]:
    if process.stdin is None or process.stdout is None or process.poll() is not None:
        raise RuntimeError("Encryption process is not available")

    line = command if not argument else f"{command} {argument}"
    process.stdin.write(f"{line}\n")
    process.stdin.flush()

    response = process.stdout.readline()
    if response == "":
        raise RuntimeError("Encryption process terminated unexpectedly")

    status, _, message = response.rstrip("\r\n").partition(" ")
    return status, message


def start_processes(log_file: str) -> tuple[subprocess.Popen[str], subprocess.Popen[str]]:
    project_dir = Path(__file__).resolve().parents[1]
    logger_script = project_dir / "logger" / "logger.py"
    encryption_script = project_dir / "encryption" / "encryption.py"

    if not logger_script.is_file():
        raise FileNotFoundError(f"Logger script not found: {logger_script}")
    if not encryption_script.is_file():
        raise FileNotFoundError(f"Encryption script not found: {encryption_script}")

    logger_process = subprocess.Popen(
        [sys.executable, "-u", str(logger_script), log_file],
        stdin=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    encryption_process = subprocess.Popen(
        [sys.executable, "-u", str(encryption_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    return logger_process, encryption_process


def stop_process(process: subprocess.Popen[str], send_quit: bool) -> None:
    if send_quit and process.stdin is not None and process.poll() is None:
        try:
            process.stdin.write("QUIT\n")
            process.stdin.flush()
        except BrokenPipeError:
            pass

    if process.stdin is not None:
        process.stdin.close()

    if process.stdout is not None:
        process.stdout.close()

    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python driver/driver.py <log_file>", file=sys.stderr)
        return 1

    log_file = sys.argv[1]
    logger_process: subprocess.Popen[str] | None = None
    encryption_process: subprocess.Popen[str] | None = None

    try:
        logger_process, encryption_process = start_processes(log_file)

        send_logger_message(logger_process, "START", "Driver started.")

        print(MENU, end="")

        # Minimal smoke test: ask encryption to quit immediately so we know pipes work.
        status, message = send_encryption_command(encryption_process, "PASS", "ABC")
        if status == "RESULT":
            send_logger_message(logger_process, "RESULT", "Encryption process responded to PASS.")
        else:
            send_logger_message(logger_process, "ERROR", f"Encryption process PASS failed: {message}")

        return 0

    finally:
        if encryption_process is not None:
            stop_process(encryption_process, send_quit=True)
        if logger_process is not None:
            stop_process(logger_process, send_quit=True)


if __name__ == "__main__":
    raise SystemExit(main())