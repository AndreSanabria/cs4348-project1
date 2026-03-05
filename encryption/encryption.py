from __future__ import annotations

import sys


def normalize_letters(value: str) -> str | None:
    cleaned = value.strip().upper()
    if not cleaned or not cleaned.isalpha():
        return None
    return cleaned


def print_response(kind: str, message: str | None = None) -> None:
    if message:
        print(f"{kind} {message}", flush=True)
    else:
        print(kind, flush=True)


def translate_vigenere(text: str, key: str, decrypt: bool) -> str:
    output: list[str] = []

    for index, character in enumerate(text):
        key_shift = ord(key[index % len(key)]) - ord("A")
        text_shift = ord(character) - ord("A")

        if decrypt:
            shifted = (text_shift - key_shift) % 26
        else:
            shifted = (text_shift + key_shift) % 26

        output.append(chr(shifted + ord("A")))

    return "".join(output)


def main() -> int:
    passkey: str | None = None

    for raw_line in sys.stdin:
        line = raw_line.rstrip("\r\n")
        if not line.strip():
            continue

        command, _, argument = line.partition(" ")
        command = command.strip().upper()
        argument = argument.strip()

        if command == "QUIT":
            break

        if command in {"PASS", "PASSKEY"}:
            normalized = normalize_letters(argument)
            if normalized is None:
                print_response("ERROR", "Password must contain only letters")
                continue

            passkey = normalized
            print_response("RESULT")
            continue

        if command in {"ENCRYPT", "DECRYPT"}:
            normalized = normalize_letters(argument)
            if normalized is None:
                print_response("ERROR", "Input must contain only letters")
                continue

            if passkey is None:
                print_response("ERROR", "Password not set")
                continue

            result = translate_vigenere(
                normalized,
                passkey,
                decrypt=(command == "DECRYPT"),
            )
            print_response("RESULT", result)
            continue

        print_response("ERROR", "Unknown command")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())