import concurrent.futures
import csv
import json
import time
from typing import Any, Dict, Iterable, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib.parse import parse_qs, urlparse
from urllib3.util.retry import Retry

try:
    from rich.console import Console  # type: ignore
    from rich.table import Table  # type: ignore
except Exception:  # pragma: no cover - rich is optional
    Console = None  # type: ignore
    Table = None  # type: ignore


ASCII_BANNER = r"""
 ____                      _   _hunter v0.8
|  _ \ __ _ ___ ___  _ __ | |_| |__   ___ _ __
| |_) / _` / __/ __|| '_ \| __| '_ \ / _ \ '__|
|  __/ (_| \__ \__ \| |_) | |_| | | |  __/ |
|_|   \__,_|___/___/| .__/ \__|_| |_|\___|_|
                    |_|
ParamHunter - CLI parameter extractor (real & operational)
"""


DEFAULT_WORKERS = 10


def make_session(
    timeout: float,
    retries: int,
    backoff_factor: float,
    proxy: Optional[str],
) -> requests.Session:
    session = requests.Session()
    retries_obj = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]),
    )
    adapter = HTTPAdapter(max_retries=retries_obj)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    if proxy:
        session.proxies.update({"http": proxy, "https": proxy})
    session.headers.update({"User-Agent": "ParamHunter/0.8"})
    session.timeout = timeout  # type: ignore[attr-defined]
    return session


def extract_params(url: str) -> List[str]:
    parsed = urlparse(url)
    return list(parse_qs(parsed.query).keys())


def check_url(
    session: requests.Session,
    url: str,
    method: str = "GET",
    data: Optional[str] = None,
    timeout: float = 5,
) -> Dict[str, Any]:
    start = time.time()
    try:
        if method.upper() == "GET":
            resp = session.get(url, timeout=timeout)
        else:
            resp = session.post(url, data=data, timeout=timeout)
        elapsed = time.time() - start
        return {
            "url": url,
            "status": resp.status_code,
            "params": extract_params(url),
            "time_ms": int(elapsed * 1000),
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - network errors vary
        elapsed = time.time() - start
        return {
            "url": url,
            "status": None,
            "params": [],
            "time_ms": int(elapsed * 1000),
            "error": str(exc),
        }


def load_targets(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def save_txt(path: str, lines: Iterable[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def save_json(path: str, results: List[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def save_csv(path: str, results: List[Dict[str, Any]]) -> None:
    fieldnames = ["url", "status", "params", "time_ms", "error"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in results:
            row = record.copy()
            row["params"] = ",".join(record.get("params", []))
            writer.writerow(row)


def pretty_print(results: List[Dict[str, Any]]) -> None:
    if Console:  # pragma: no cover - formatting only
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("URL")
        table.add_column("Status")
        table.add_column("Params")
        table.add_column("Time(ms)", justify="right")
        for r in results:
            table.add_row(
                r["url"],
                str(r["status"]) if r["status"] else "ERR",
                ",".join(r["params"]) if r["params"] else "-",
                str(r["time_ms"]),
            )
        console.print(ASCII_BANNER)
        console.print(table)
    else:
        print(ASCII_BANNER)
        for r in results:
            if r["error"]:
                print(f"[ERROR] {r['url']} -> {r['error']}")
            elif r["params"]:
                print(
                    f"[+] {r['url']} -> params: {', '.join(r['params'])} (http {r['status']})"
                )
            else:
                print(f"[-] {r['url']} -> no params (http {r['status']})")


def run(
    targets: List[str],
    threads: int,
    method: str,
    data: Optional[str],
    timeout: float,
    retries: int,
    backoff: float,
    proxy: Optional[str],
) -> List[Dict[str, Any]]:
    session = make_session(timeout=timeout, retries=retries, backoff_factor=backoff, proxy=proxy)
    results: List[Dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_map = {
            executor.submit(
                check_url, session, target, method=method, data=data, timeout=timeout
            ): target
            for target in targets
        }
        for future in concurrent.futures.as_completed(future_map):
            results.append(future.result())
    return results


