# 🔎 **ParamHunter**

![CI](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/ParamHunter/ci.yml?branch=main)
![PyPI - Version](https://img.shields.io/pypi/v/paramhunter)
![License](https://img.shields.io/badge/license-MIT-green)

**ParamHunter v0.8** is a real and operational CLI tool for extracting URL parameters from websites.
It is designed for security researchers, bug bounty hunters, and penetration testers.

---

## ⚡ **Features**

- Multithreading scanning for faster processing
- GET and POST request support with optional data
- Proxy support for anonymous scanning
- Timeout, retry, and backoff settings
- Output in TXT, JSON, and CSV formats
- Rich CLI banner (if `rich` library is installed)
- ASCII banner for professional CLI appearance
- Handles multiple URLs from a list file
  
  > ⚠️ **Important** > Use this tool only on websites you have permission to test. Unauthorized scanning may be illegal.

---

## 🛠️ **Installation**

Recommended (from PyPI):

```bash
pip install paramhunter[rich]
```

Or from source:

```bash
git clone https://github.com/YOUR_USERNAME/ParamHunter.git
cd ParamHunter
pip install -e .[rich]
```


## **Scan a single URL**

```bash
paramhunter -u "https://example.com/?id=1" --txt --json --csv
```

## **Scan multiple URLs from a list**

```bash
paramhunter -l urls_example.txt --txt --csv
```

| Option            | Description                                   |
| ----------------- | --------------------------------------------- |
| `-u`, `--url`     | Scan a single target URL                      |
| `-l`, `--list`    | Scan multiple URLs from a file                |
| `-o`, `--output`  | Base name for output files (default: results) |
| `--txt`           | Save output as TXT                            |
| `--json`          | Save output as JSON                           |
| `--csv`           | Save output as CSV                            |
| `--threads`       | Number of concurrent threads (default: 10)    |
| `--method`        | Request method: GET or POST (default: GET)    |
| `--data`          | POST data to send                             |
| `--proxy`         | Proxy URL                                     |
| `--timeout`       | Request timeout in seconds (default: 5.0)     |
| `--retries`       | Number of retry attempts (default: 2)         |
| `--backoff`       | Backoff factor for retries (default: 0.5)     |
| `--no-banner`     | Disable ASCII/Rich CLI banner                 |

## **Example URLs**

See `urls_example.txt` for sample targets.

> ⚠️ Use this tool only on websites you have permission to test.