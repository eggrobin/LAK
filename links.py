import csv
import re

lines : list[str] = []

refs : dict[str, list[int]] = {}
vat_to_p : dict[int, str] = {}

with open("../edsl/lak/etc/lak-refs.tsv") as f:
  for line in csv.reader(f, delimiter="\t"):
    refs[line[0].removeprefix("LAK").lstrip("0")] = [int(n) for n in line[1:] if n and n != "TSA_6"]

with open("../edsl/lak/etc/vat.P") as f:
  for line in csv.reader(f, delimiter="\t"):
    _, vat_number = line[0].split()
    vat_number = int(vat_number)
    p_number = line[1].removeprefix("cdli:")
    if p_number:
      vat_to_p[vat_number] = p_number

lak_number : str|None = None
numbers_seen : set[int] = set()

max_lak_number = 0
with open("LAK.html") as f:
  for line in f.readlines():
    match = re.search(r'id=\"(\d+)[a-z]?\"', line)
    if match:
      max_lak_number = int(match.group(1))

with open("LAK.html") as f:
  for line in f.readlines():
    def linkify_internal(match: re.Match[str]):
      referenced_lak_number = int(match.group("n"))
      if match.group("href") and int(match.group("href")) != referenced_lak_number:
        raise ValueError(f"n. {referenced_lak_number} links to {match.group('href')}")
      if referenced_lak_number < max_lak_number:
        return f' <a href="#{referenced_lak_number}">n. {referenced_lak_number}</a>'
      return match.group(0)
    line = re.sub(r'(?<!Mus\.) (?:<a href="#(?P<href>\d+)">)?n\. (?P<n>\d+)(?:</a>)?', linkify_internal, line)
    def linkify_vat(match: re.Match[str]):
      vat_number = int(match.group("VAT"))
      numbers_seen.add(vat_number)
      if match.group("P"):
        if vat_to_p[vat_number] != match.group("P"):
          raise ValueError(f"Mismatch for VAT {vat_number}: {match.group('P')} vs. EDSL {vat_to_p[vat_number]}")
        return match.group()
      elif vat_number in vat_to_p and not match.group("other"):
        return f'<a href="http://cdli.earth/{vat_to_p[vat_number]}">{match.group()}</a>'
      else:
        return match.group()
    line = re.sub(r'(?:<a href="(?:http://cdli.earth/(?P<P>P\d+)|(?P<other>.*))">)?(?P<VAT>\d{4,})(?:</a>)?', linkify_vat, line)
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
    lines.append(line)

with open("LAK.html", "w") as f:
  f.writelines(lines)