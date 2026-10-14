"""
parse_results.py  -  Parse MT4 HTML backtest reports, update TEST_LOG and candidate_log.
Reads hst_out/*.htm reports, extracts profit, trades, PF, DD, updates logs.

Run: python -I data/parse_results.py [--tag TAG]
     or just: python -I data/parse_results.py   (processes all new .htm in hst_out)
"""

import os, re, sys, csv, datetime

HST_OUT   = r"C:\Users\endos\Desktop\hst_out"
TEST_LOG  = r"C:\Users\endos\Desktop\hst_out\winners\TEST_LOG.txt"
CAND_LOG  = r"C:\Users\endos\Signal\data\candidate_log.csv"
HIST_LABEL = 'PATCHWORK(mixed clocks, holes)'  # set by auto_loop (--clean => CLEAN(UTC+2/+3 USDST, FXOpen raw M1 bid))
COMMISSION = 6  # FXOpen ECN EURUSD round-trip pts (c) Nasif Hossain confirmed 2026-10-13

# â”€â”€ HTML parser â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def parse_report(path):
    with open(path, encoding='utf-8', errors='ignore') as f:
        html = f.read()

    def find(pattern, default='?'):
        m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else default

    # MT4 report fields
    profit    = find(r'Total net profit.*?<td[^>]*>([\-\d\., ]+)</td>')
    trades    = find(r'Total trades.*?<td[^>]*>(\d+)</td>')
    pf        = find(r'Profit factor.*?<td[^>]*>([\d\.]+)</td>')
    dd_pct    = find(r'Maximal drawdown.*?<td[^>]*>[^<]*\(([0-9\.]+)%\)')
    modeling  = find(r'Modelling quality.*?<td[^>]*>([0-9\.]+)%')
    bars      = find(r'Bars in test.*?<td[^>]*>([\d ]+)</td>')
    gross_p   = find(r'Gross profit.*?<td[^>]*>([\-\d\., ]+)</td>')
    gross_l   = find(r'Gross loss.*?<td[^>]*>([\-\d\., ]+)</td>')

    # clean profit string
    profit = re.sub(r'[^\d\.\-]', '', profit.replace(' ',''))

    return {
        "profit": profit, "trades": trades,
        "pf": pf, "dd_pct": dd_pct,
        "modeling": modeling, "bars": bars,
        "gross_p": gross_p, "gross_l": gross_l,
    }

# â”€â”€ update candidate log â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def update_cand_log(tag, result_str):
    if not os.path.exists(CAND_LOG): return
    rows = []
    with open(CAND_LOG) as f:
        rows = list(csv.DictReader(f))
    changed = False
    for row in rows:
        if row.get('tag') == tag:
            row['result'] = result_str; changed = True
    if changed:
        with open(CAND_LOG, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=["name","year","tag","rationale","result"])
            w.writeheader(); w.writerows(rows)
        print(f"  Updated candidate_log: {tag} -> {result_str}")

# â”€â”€ append to TEST_LOG â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def append_test_log(tag, r):
    try:
        comm_pts = int(r['trades']) * COMMISSION
    except Exception:
        comm_pts = '?'
    # Spread cost in $ = gross_profit + gross_loss - net_profit
    # (all three are already net of spread in MT4 tester model 0,
    #  but gross_p/gross_l show winners/losers before subtracting spread;
    #  we report comm_pts as the honest broker-rate estimate)
    line = (f"{datetime.date.today()} | MT4  | b31   | "
            f"ER/MMR gate test ({tag}) | "
            f"profit {r['profit']} | trades {r['trades']} | PF {r['pf']} | "
            f"DD {r['dd_pct']}% | model {r['modeling']}% | sp{COMMISSION} | hist={HIST_LABEL} | "
            f"comm_pts {comm_pts} | gross_p {r['gross_p']} | gross_l {r['gross_l']}")
    with open(TEST_LOG, 'a') as f:
        f.write(line + '\n')
    print(f"  TEST_LOG appended: {line[:100]}...")

# â”€â”€ main â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main():
    tag_filter = None
    for i, a in enumerate(sys.argv[1:]):
        if a == '--tag' and i+2 <= len(sys.argv)-1:
            tag_filter = sys.argv[i+2]

    print("=== parse_results.py ===\n")
    reports = [f for f in os.listdir(HST_OUT) if f.endswith('.htm')]
    if tag_filter:
        reports = [f for f in reports if tag_filter in f]
    reports.sort()

    print(f"Found {len(reports)} report(s){' matching '+tag_filter if tag_filter else ''}:\n")
    for fname in reports:
        path = os.path.join(HST_OUT, fname)
        tag = fname.replace('.htm','')
        print(f"  {fname}")
        try:
            r = parse_report(path)
            result_str = (f"profit={r['profit']} trades={r['trades']} "
                          f"PF={r['pf']} DD={r['dd_pct']}% model={r['modeling']}%")
            print(f"    {result_str}")
            update_cand_log(tag, result_str)
            append_test_log(tag, r)
        except Exception as e:
            print(f"    ERROR: {e}")

    print("\nDone. Check TEST_LOG and candidate_log.csv.")

if __name__ == '__main__':
    main()

