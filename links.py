import csv
import re

lines : list[str] = []

refs : dict[str, list[int]] = {}

with open("../edsl/lak/etc/lak-refs.tsv") as refs_file:
  for line in csv.reader(refs_file, delimiter="\t"):
    refs[line[0].removeprefix("LAK").lstrip("0")] = [int(n) for n in line[1:] if n and n != "TSA_6"]

lak_number = None
numbers_seen : set[int] = set()

with open("LAK.html") as html:
  for line in html.readlines():
    for match in re.finditer(r'(\d{4,})', line):
      numbers_seen.add(int(match.group(1)))
    match = re.search(r'id=\"(\d+[a-z]?)\"', line)
    if match:
      if lak_number:
        for ref in refs[lak_number]:
          if ref not in numbers_seen:
            print(f"*** LAK {lak_number}: in EDSL but not found: {ref}")
        for ref in numbers_seen:
          if ref not in refs[lak_number]:
            print(f"*** LAK {lak_number}: {ref} found but not in EDSL")
        if set(refs[lak_number]) == numbers_seen:
          print(f"--- {len(numbers_seen)} references as expected for {lak_number}")
      lak_number = match.group(1)
      numbers_seen = set()
