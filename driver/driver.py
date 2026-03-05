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


def normalize_letters(value: str) -> str | None:
    cleaned = value.strip().upper()
    if not cleaned or not cleaned.isalpha():
        return None
    return cleaned


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


def show_history(history: list[str]) -> None:
    if not history:
        print("History is empty.")
        return

    print("History:")
    for index, value in enumerate(history, start=1):
        print(f"  {index}. {value}")


def choose_history_value(history: list[str]) -> str | None:
    while True:
        show_history(history)
        print("  0. Enter a new string")
        choice = input("Select an entry: ").strip()

        if not choice.isdigit():
            print("Enter a valid number.")
            continue

        selection = int(choice)
        if selection == 0:
            return None
        if 1 <= selection <= len(history):
            return history[selection - 1]

        print("Enter a valid number.")


def choose_letters(history: list[str], prompt_text: str) -> tuple[str | None, bool]:
    if history:
        while True:
            use_history = input("Use a string from history? (y/n): ").strip().lower()
            if use_history in {"y", "yes"}:
                selected = choose_history_value(history)
                if selected is not None:
                    return selected, True
                break
            if use_history in {"n", "no"}:
                break
            print("Enter y or n.")

    candidate = input(prompt_text)
    normalized = normalize_letters(candidate)
    if normalized is None:
        print("Error: input must contain only letters.")
        return None, False

    return normalized, False


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
    history: list[str] = []

    try:
        logger_process, encryption_process = start_processes(log_file)
        send_logger_message(logger_process, "START", "Driver started.")

        while True:
            print(MENU, end="")
            command = input("Command: ").strip().lower()
            if not command:
                continue

            send_logger_message(logger_process, "COMMAND", command)

            if command == "password":
                password, _ = choose_letters(history, "Enter password: ")
                if password is None:
                    send_logger_message(
                        logger_process,
                        "ERROR",
                        "Password update failed: input must contain only letters.",
                    )
                    continue

                status, message = send_encryption_command(encryption_process, "PASS", password)
                if status == "RESULT":
                    print("Password updated.")
                    send_logger_message(logger_process, "RESULT", "Password updated.")
                else:
                    print(f"Error: {message}")
                    send_logger_message(logger_process, "ERROR", f"Password update failed: {message}")
                continue

            if command in {"encrypt", "decrypt"}:
                value, from_history = choose_letters(history, f"Enter string to {command}: ")
                if value is None:
                    send_logger_message(
                        logger_process,
                        "ERROR",
                        f"{command.title()} failed: input must contain only letters.",
                    )
                    continue

                if not from_history:
                    history.append(value)

                status, message = send_encryption_command(encryption_process, command.upper(), value)
                if status == "RESULT":
                    print(f"Result: {message}")
                    history.append(message)
                    send_logger_message(
                        logger_process,
                        "RESULT",
                        f"{command.title()} produced {message}.",
                    )
                else:
                    print(f"Error: {message}")
                    send_logger_message(logger_process, "ERROR", f"{command.title()} failed: {message}")
                continue

            if command == "history":
                show_history(history)
                send_logger_message(logger_process, "RESULT", f"Displayed {len(history)} history entries.")
                continue

            if command == "quit":
                send_logger_message(logger_process, "RESULT", "Driver exiting.")
                return 0

            print("Error: unknown command.")
            send_logger_message(logger_process, "ERROR", f"Unknown command: {command}")

    finally:
        if encryption_process is not None:
            stop_process(encryption_process, send_quit=True)
        if logger_process is not None:
            stop_process(logger_process, send_quit=True)


if __name__ == "__main__":
    raise SystemExit(main())