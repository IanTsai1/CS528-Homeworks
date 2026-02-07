#!/usr/bin/env python3
import argparse
import os
import re
from statistics import mean, median
import time


# this regex is used to find reference link by checking for 'href' 
LINK_RE = re.compile(r'href\s*=\s*["\'](\d+)\.html["\']', re.IGNORECASE)

def list_html_files(folder: str) -> list[str]:
    files = []
    for name in os.listdir(folder):
        if name.endswith(".html"):
            files.append(name)

    # ChatGPT said to use sorting here to ensure consistent result from PageRank output
    # PageRank output won't be dependent on the random sinces 'os.listdir' doesn't promise any order
    return sorted(files, key=lambda s: int(s[:-5]))

'''

-input arr: idx = file name, value = # of indegree or outdegree

Used ChatGPT to give me the formula for finding quintile 
'''
def quantiles(values: list[int], qs=(0, 20, 40, 60, 80, 100)) -> dict[int, float]:
    v = sorted(values)
    n = len(v)
    out = {}
    for q in qs:
        if n == 1:
            out[q] = float(v[0])
            continue
        pos = (q / 100) * (n - 1)
        lo = int(pos)
        hi = min(lo + 1, n - 1)
        frac = pos - lo

        out[q] = v[lo] * (1 - frac) + v[hi] * frac
    
    #returns the # of out/indegree for each percentile 
    return out

def summarize(values: list[int]) -> dict[str, float]:
    return {
        "avg": float(mean(values)),
        "median": float(median(values)),
        "min": float(min(values)),
        "max": float(max(values)),
    }

def parse_graph(folder: str):
    files = list_html_files(folder)
    nodes = [int(f[:-5]) for f in files]
    # node_set = set(nodes)

    # create hashmap
    out_links = {u: set() for u in nodes}

    for u in nodes:
        path = os.path.join(folder, f"{u}.html")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except FileNotFoundError:
            continue

        # find reference link; m.group(1) is used to get the digit
        # m.group(0)  # 'href="123.html"' ; m.group(1)  # '123'
        targets = set(int(m.group(1)) for m in LINK_RE.finditer(text))

        # assign adj list values
        out_links[u] = {v for v in targets}

    # create hashmap
    in_links = {u: set() for u in nodes}
    for u, outs in out_links.items():
        for v in outs:
            in_links[v].add(u)

    return nodes, out_links, in_links

def pagerank(nodes, out_links, in_links, max_iters=500):
    n = len(nodes)
    if n == 0:
        return {}, 0

    damping = 0.85
    tol = 0.005  # 0.5%

    node_idx = {u: i for i, u in enumerate(nodes)}
    pr = [1.0 / n] * n

    prev_sum = sum(pr)

    for it in range(1, max_iters + 1):
        new_pr = [(1.0 - damping) / n] * n #in formula given, we set it as 1-0.85 = 0.15; so 0.15/n

        dangling_mass = 0.0
        for u in nodes:
            if len(out_links[u]) == 0:
                dangling_mass += pr[node_idx[u]]

        dangling_share = damping * dangling_mass / n
        for i in range(n):
            new_pr[i] += dangling_share

        for v in nodes:
            i_v = node_idx[v]
            s = 0.0
            for t in in_links[v]:
                c_t = len(out_links[t])
                if c_t > 0:
                    s += pr[node_idx[t]] / c_t
            new_pr[i_v] += damping * s

        new_sum = sum(new_pr)
        # Relative change in sum across iterations
        rel_change = abs(new_sum - prev_sum) / prev_sum if prev_sum != 0 else abs(new_sum - prev_sum)

        pr = new_pr
        prev_sum = new_sum

        if rel_change <= tol:
            return {nodes[i]: pr[i] for i in range(n)}, it

    return {nodes[i]: pr[i] for i in range(n)}, max_iters


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="Folder containing N.html files")

    args = ap.parse_args()

    start = time.perf_counter()

    nodes, out_links, in_links = parse_graph(args.folder)

    out_deg = [len(out_links[u]) for u in nodes]
    in_deg = [len(in_links[u]) for u in nodes]

    out_stats = summarize(out_deg)
    in_stats = summarize(in_deg)
    out_q = quantiles(out_deg)
    in_q = quantiles(in_deg)

    print(f"Pages: {len(nodes)}")
    print("\nOutgoing links (out-degree) stats:")
    print(f"  Avg: {out_stats['avg']:.3f}")
    print(f"  Median: {out_stats['median']:.3f}")
    print(f"  Min: {out_stats['min']:.3f}")
    print(f"  Max: {out_stats['max']:.3f}")
    print("  Quintiles (0,20,40,60,80,100): " + ", ".join(f"{k}:{out_q[k]:.3f}" for k in [0,20,40,60,80,100]))

    print("\nIncoming links (in-degree) stats:")
    print(f"  Avg: {in_stats['avg']:.3f}")
    print(f"  Median: {in_stats['median']:.3f}")
    print(f"  Min: {in_stats['min']:.3f}")
    print(f"  Max: {in_stats['max']:.3f}")
    print("  Quintiles (0,20,40,60,80,100): " + ", ".join(f"{k}:{in_q[k]:.3f}" for k in [0,20,40,60,80,100]))

    pr, iters = pagerank(nodes, out_links, in_links)

    top5 = sorted(pr.items(), key=lambda kv: kv[1], reverse=True)[:5]

    print("Top 5 pages by PageRank:")
    for u, score in top5:
        print(f"  {u}.html  PR={score:.8f}")
    
    end = time.perf_counter()
    print(f"\nTotal runtime: {end - start:.3f} seconds")


if __name__ == "__main__":
    main()
