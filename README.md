# Python Multi-Threaded Port Scanner

A lightweight, fast TCP port scanner written in Python. It includes OS fingerprinting via ICMP TTL and service banner grabbing.

## Features
* **Multi-threaded:** Scans ports in parallel using `ThreadPoolExecutor`.
* **OS Hinting:** Guesses the target OS based on TTL values.
* **Banner Grabbing:** Attempts to identify service versions (HTTP, SSH, etc.).
* **Zero Dependencies:** Uses only Python standard libraries.

## Usage
1. Clone the repo: `git clone https://github.com/sineeshs/portscanner.git`
2. Run the script: `port_scanner.py`
3. Enter the target IP and port range.

## Disclaimer
This tool is for educational and ethical testing purposes only. Only use it on networks you own or have explicit permission to scan.
