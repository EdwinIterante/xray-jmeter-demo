import csv, sys
from collections import OrderedDict
from xml.sax.saxutils import escape, quoteattr

jtl, out = sys.argv[1], sys.argv[2]
prefix = sys.argv[3] if len(sys.argv) > 3 else "jmeter"
TX_MARK = "Number of samples in transaction"

with open(jtl, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

has_tx = any(r["responseMessage"].startswith(TX_MARK) for r in rows)
suites = OrderedDict()
for r in rows:
    if has_tx and not r["responseMessage"].startswith(TX_MARK):
        continue
    suites.setdefault(r["threadName"], []).append(r)

tot_tests = sum(len(v) for v in suites.values())
tot_fail = sum(1 for v in suites.values() for r in v if r["success"].lower() != "true")

with open(out, "w", encoding="utf-8") as o:
    o.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    o.write(f'<testsuites tests="{tot_tests}" failures="{tot_fail}">\n')
    for thread, samples in suites.items():
        fails = sum(1 for r in samples if r["success"].lower() != "true")
        t = sum(int(r["elapsed"]) for r in samples) / 1000
        o.write(f'  <testsuite name={quoteattr(thread)} tests="{len(samples)}" failures="{fails}" time="{t:.3f}">\n')
        for r in samples:
            o.write(f'    <testcase classname={quoteattr(prefix)} name={quoteattr(r["label"])} time="{int(r["elapsed"])/1000:.3f}">\n')
            if r["success"].lower() != "true":
                msg = (r.get("failureMessage") or r["responseMessage"] or f'HTTP {r["responseCode"]}').strip()
                o.write(f'      <failure message={quoteattr(msg[:200])}>{escape(msg)}</failure>\n')
            o.write('    </testcase>\n')
        o.write('  </testsuite>\n')
    o.write('</testsuites>\n')