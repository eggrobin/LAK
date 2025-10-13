from collections import defaultdict
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
vat_numbers_seen : set[int] = set()
artefact_designation_to_link : dict[str, str] = {}

max_lak_number = 0
with open("LAK.html") as f:
  for line in f.readlines():
    match = re.search(r'id=\"(\d+)[a-z]?\"', line)
    if match:
      max_lak_number = int(match.group(1))

in_body = False

with open("LAK.html") as f:
  for line in f.readlines():
    if "<body>" in line:
      in_body = True
    if not in_body:
      lines.append(line)
      continue
    def linkify_internal(match: re.Match[str]):
      referenced_lak_number = int(match.group("n"))
      if match.group("href") and int(match.group("href")) != referenced_lak_number:
        raise ValueError(f"n. {referenced_lak_number} links to {match.group('href')}")
      if referenced_lak_number < max_lak_number:
        return f' <a href="#{referenced_lak_number}">n. {referenced_lak_number}</a>'
      return match.group(0)
    line = re.sub(r'(?<!Mus\.) (?:<a href="#(?P<href>\d+)">)?n\. (?P<n>\d+)(?:</a>)?', linkify_internal, line)
    def linkify_artefact(match: re.Match[str]):
      vat_number = match.group("VAT") or match.group("Linked_VAT")
      vat_number = int(vat_number) if vat_number else None
      if vat_number:
        vat_numbers_seen.add(vat_number)
      p_number = match.group("P")
      link = p_number or match.group("Other_Link")
      if link:
        artefact_designation = match.group("VAT") or match.group("Linked_VAT") or match.group("Other_Artefact")
        if artefact_designation not in artefact_designation_to_link:
          artefact_designation_to_link[artefact_designation] = link
        if artefact_designation_to_link[artefact_designation] != link:
          raise ValueError(f"Mismatch for {artefact_designation}: Linked to {artefact_designation_to_link[artefact_designation]} then {link}")
      else:
        artefact_designation = match.group()
      if match.group("Other_Link"):
        return match.group()
      else:
        if p_number and vat_number and vat_to_p[vat_number] != p_number:
          raise ValueError(f"Mismatch for VAT {vat_number}: {match.group('P')} vs. EDSL {vat_to_p[vat_number]}")
        if p_number:
          return f'<a href="http://cdli.earth/{p_number}">{artefact_designation}</a>'
        else:
          return match.group()
    line = re.sub(r'(?:<a href="(?:https?://cdli.earth/(?P<P>P\d+)|(?P<Other_Link>(?!#|http://oracc.org/([a-z]+/)+P\d+\.\d)[^"]*))">(?:(?P<Linked_VAT>\d{4,})|(?P<Other_Artefact>[^<]*))</a>)|\b(?P<VAT>\d{4,})(?:\b|(?=R))', linkify_artefact, line)
    match = re.search(r'id=\"(\d+[a-z]?)\"', line)
    if match:
      if lak_number:
        for ref in refs[lak_number]:
          if ref not in vat_numbers_seen:
            print(f"*** LAK {lak_number}: in EDSL but not found: {ref}")
        for ref in vat_numbers_seen:
          if ref not in refs[lak_number]:
            print(f"*** LAK {lak_number}: {ref} found but not in EDSL")
        if set(refs[lak_number]) == vat_numbers_seen:
          print(f"--- {len(vat_numbers_seen)} references as expected for {lak_number}")
      lak_number = match.group(1)
      vat_numbers_seen = set()
    lines.append(line)

with open("LAK.html", "w") as f:
  f.writelines(lines)

link_to_artefact_designation : dict[str, set[str]] = defaultdict(set)

for designation, link in artefact_designation_to_link.items():
  link_to_artefact_designation[link].add(designation)

with open("links.log", "w") as f:
  for link, designations in sorted(link_to_artefact_designation.items()):
    print(link, sorted(designations), file=f)