CS4348 Project 1

This project is three separate Python programs that communicate using pipes:
- driver: the interactive menu
- logger: receives log lines on stdin and appends them to a file
- encryption: receives commands on stdin and returns RESULT or ERROR on stdout

Folder layout:
- driver/driver.py
- logger/logger.py
- encryption/encryption.py

How to run

From the repo root:

python driver/driver.py runlog.txt

You will get a menu with:
password, encrypt, decrypt, history, quit

Notes
- Password, encrypt, and decrypt inputs must be letters only.
- Case does not matter because everything is normalized internally.
- The log file is created if it does not exist.
- Passwords are never written to the log file and are not stored in history.