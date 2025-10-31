import argparse
from typing import List

from .core import (
    DEFAULT_WORKERS,
    load_targets,
    pretty_print,
    run,
    save_csv,
    save_json,
    save_txt,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ParamHunter v0.8 - Real operational CLI parameter extractor"
    )
    parser.add_argument("-u", "--url", help="Single target URL")
    parser.add_argument("-l", "--list", help="File with list of target URLs")
    parser.add_argument("-o", "--output", default="results", help="Base name for output files")
    parser.add_argument("--json", action="store_true", help="Save JSON output")
    parser.add_argument("--csv", action="store_true", help="Save CSV output")
    parser.add_argument("--txt", action="store_true", help="Save TXT output")
    parser.add_argument("--threads", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--method", choices=["GET", "POST"], default="GET")
    parser.add_argument("--data", help="POST data to send")
    parser.add_argument("--proxy", help="Proxy URL")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--backoff", type=float, default=0.5)
    parser.add_argument("--no-banner", action="store_true")
    return parser.parse_args()


def collect_targets(args: argparse.Namespace) -> List[str]:
    targets: List[str] = []
    if args.url:
        targets.append(args.url)
    if args.list:
        targets.extend(load_targets(args.list))
    return targets


def main() -> None:
    args = parse_args()
    targets = collect_targets(args)
    if not targets:
        print("No targets provided. Use -u or -l.")
        return

    results = run(
        targets=targets,
        threads=args.threads,
        method=args.method,
        data=args.data,
        timeout=args.timeout,
        retries=args.retries,
        backoff=args.backoff,
        proxy=args.proxy,
    )

    lines = []
    for r in results:
        if r["error"]:
            lines.append(f"[ERROR] {r['url']} -> {r['error']}")
        elif r["params"]:
            lines.append(
                f"[+] {r['url']} -> params: {', '.join(r['params'])} (http {r['status']})"
            )
        else:
            lines.append(f"[-] {r['url']} -> no params (http {r['status']})")

    if not args.no_banner:
        pretty_print(results)

    base = args.output
    save_txt(base + ".txt", lines)
    if args.json:
        save_json(base + ".json", results)
    if args.csv:
        save_csv(base + ".csv", results)


if __name__ == "__main__":
    main()


