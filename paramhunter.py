#!/usr/bin/env python3
"""
ParamHunter v0.8 - Real and operational CLI tool for extracting URL parameters.
"""

import argparse, concurrent.futures, csv, json, time
from urllib.parse import urlparse, parse_qs
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from rich.console import Console
    from rich.table import Table
except ImportError:
    Console = None

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

def make_session(timeout, retries, backoff_factor, proxy):
    session = requests.Session()
    retries_obj = Retry(
        total=retries, backoff_factor=backoff_factor,
        status_forcelist=[429,500,502,503,504],
        allowed_methods=frozenset(['GET','POST','PUT','DELETE','HEAD','OPTIONS'])
    )
    adapter = HTTPAdapter(max_retries=retries_obj)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    if proxy:
        session.proxies.update({'http': proxy,'https': proxy})
    return session

def extract_params(url):
    parsed = urlparse(url)
    return list(parse_qs(parsed.query).keys())

def check_url(session, url, method='GET', data=None, timeout=5):
    start = time.time()
    try:
        if method.upper() == 'GET':
            resp = session.get(url, timeout=timeout)
        else:
            resp = session.post(url, data=data, timeout=timeout)
        elapsed = time.time()-start
        return {"url": url, "status": resp.status_code, "params": extract_params(url), "time_ms": int(elapsed*1000), "error": None}
    except Exception as e:
        elapsed = time.time()-start
        return {"url": url, "status": None, "params": [], "time_ms": int(elapsed*1000), "error": str(e)}

def load_targets(file):
    with open(file,'r',encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def save_txt(path, lines):
    with open(path,'w',encoding='utf-8') as f:
        f.write('\n'.join(lines))

def save_json(path, results):
    with open(path,'w',encoding='utf-8') as f:
        json.dump(results,f,indent=2,ensure_ascii=False)

def save_csv(path, results):
    fieldnames=['url','status','params','time_ms','error']
    with open(path,'w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            row=r.copy()
            row['params']=','.join(r.get('params',[]))
            writer.writerow(row)

def pretty_print(results):
    if Console:
        console=Console()
        table=Table(show_header=True, header_style="bold magenta")
        table.add_column("URL")
        table.add_column("Status")
        table.add_column("Params")
        table.add_column("Time(ms)",justify="right")
        for r in results:
            table.add_row(r['url'], str(r['status']) if r['status'] else 'ERR', ','.join(r['params']) if r['params'] else '-', str(r['time_ms']))
        console.print(ASCII_BANNER)
        console.print(table)
    else:
        print(ASCII_BANNER)
        for r in results:
            if r['error']:
                print(f"[ERROR] {r['url']} -> {r['error']}")
            elif r['params']:
                print(f"[+] {r['url']} -> params: {', '.join(r['params'])} (http {r['status']})")
            else:
                print(f"[-] {r['url']} -> no params (http {r['status']})")

def main():
    parser=argparse.ArgumentParser(description="ParamHunter v0.8 - Real operational CLI parameter extractor")
    parser.add_argument("-u","--url",help="Single target URL")
    parser.add_argument("-l","--list",help="File with list of target URLs")
    parser.add_argument("-o","--output",default="results",help="Base name for output files")
    parser.add_argument("--json",action="store_true",help="Save JSON output")
    parser.add_argument("--csv",action="store_true",help="Save CSV output")
    parser.add_argument("--txt",action="store_true",help="Save TXT output")
    parser.add_argument("--threads",type=int,default=DEFAULT_WORKERS)
    parser.add_argument("--method",choices=['GET','POST'],default='GET')
    parser.add_argument("--data",help="POST data to send")
    parser.add_argument("--proxy",help="Proxy URL")
    parser.add_argument("--timeout",type=float,default=5.0)
    parser.add_argument("--retries",type=int,default=2)
    parser.add_argument("--backoff",type=float,default=0.5)
    parser.add_argument("--no-banner",action="store_true")
    args=parser.parse_args()

    targets=[]
    if args.url: targets.append(args.url)
    if args.list: targets.extend(load_targets(args.list))
    if not targets:
        print("No targets provided. Use -u or -l.")
        return

    session=make_session(timeout=args.timeout,retries=args.retries,backoff_factor=args.backoff,proxy=args.proxy)
    results=[]
    lines=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_map={executor.submit(check_url,session,t,method=args.method,data=args.data,timeout=args.timeout):t for t in targets}
        for fut in concurrent.futures.as_completed(future_map):
            res=fut.result()
            results.append(res)
            if res['error']:
                lines.append(f"[ERROR] {res['url']} -> {res['error']}")
            elif res['params']:
                lines.append(f"[+] {res['url']} -> params: {', '.join(res['params'])} (http {res['status']})")
            else:
                lines.append(f"[-] {res['url']} -> no params (http {res['status']})")

    if not args.no_banner:
        pretty_print(results)

    base=args.output
    save_txt(base+".txt",lines)
    if args.json: save_json(base+".json",results)
    if args.csv: save_csv(base+".csv",results)

if __name__=="__main__":
    main()
