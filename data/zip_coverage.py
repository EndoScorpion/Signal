"""zip_coverage.py - M1 lines per month inside the big FXOpen EURUSD zip (bid file), to see whether the holes in the .hst exist in the raw download."""
import zipfile, io, collections
Z = r"C:\Users\endos\Signal\data\quotes_download\2026-10-13_18-48-11\EURUSD_M1_2009-01-01-14-00-51_2026-10-06-00-00-00.zip"
zf = zipfile.ZipFile(Z); per = collections.Counter(); first = last = None
for line in io.TextIOWrapper(zf.open("M1 bid.csv"), encoding="utf-8"):
    if len(line) > 16 and line[:4].isdigit():
        per[line[:7]] += 1
        if first is None: first = line[:19]
        last = line[:19]
print("zip M1 first/last:", first, last, "| total", sum(per.values()))
check = ["2009.01","2009.06","2010.01","2010.03","2010.05","2013.03","2013.04","2013.05","2013.06","2013.07","2013.08","2014.04","2014.05","2014.06","2014.09","2014.12","2015.01","2016.02","2016.03","2016.10","2016.11","2020.02","2020.03","2020.04","2020.05","2021.02","2021.03","2011.08","2022.05"]
print({k: per.get(k, 0) for k in check})
thin = sorted((k, v) for k, v in per.items() if v < 0.75 * 29000 and k >= "2010.07" and k <= "2026.09")
print("zip months with < ~22k M1 lines (full month ~29-31k):", thin)
