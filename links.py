from collections import defaultdict
import csv
import re

import artefacts

lines : list[str] = []

refs : dict[str, list[int]] = {}
vat_to_p : dict[int, str] = {}
dp_to_p : dict[int, str] = {}
rtc_to_p : dict[int, str] = {}
nik_to_p : dict[int, str] = {}

with open("Nik.csv") as f:
  for i, line in enumerate(csv.reader(f)):
    if i == 0:
      continue
    try:
      publications = [p.strip() for p in line[3].split(";")]
      nik = int(line[5].split(";")[publications.index("Nikol'skij1908")])
      if line[2].startswith("Nik") and line[2] != f"Nik 1, {nik:03}":
        raise ValueError(line[2])
      nik_to_p[nik] = f"P{int(line[0]):06}"
    except Exception as e:
      print(line)
      raise

with open("DP.csv") as f:
  for i, line in enumerate(csv.reader(f)):
    if i == 0:
      continue
    try:
      publications = [p.strip() for p in line[3].split(";")]
      dp = int(line[5].split(";")[publications.index("AllottedelaFuÿe1908-1920DP")])
      if line[2].startswith("DP") and line[2] != f"DP {dp:03}":
        raise ValueError(line[2])
      dp_to_p[dp] = f"P{int(line[0]):06}"
    except Exception as e:
      print(line)
      raise

with open("RTC.csv") as f:
  heading = []
  for i, line in enumerate(csv.reader(f)):
    if i == 0:
      heading = line
      continue
    if line[40] == "composite":
      continue
    try:
      publications = [p.strip() for p in line[3].split(";")]
      rtc_range = line[5].split(";")[publications.index("Thureau-Dangin1903RTC")]
      if "-" in rtc_range:
        first, last = rtc_range.split("-")
        rtcs = range(int(first), int(last)+1)
      else:
        rtcs = (int(rtc_range),)
      for rtc in rtcs:
        if (line[2].startswith("RTC") and
            "+" not in line[2] and
            "-" not in line[2] and
            line[2] != f"RTC {rtc:03}"):
          raise ValueError(line[2], rtc)
        rtc_to_p[rtc] = f"P{int(line[0]):06}"
    except Exception as e:
      for i, field in enumerate(line):
        print(f"{i:2} {heading[i]:30} {field!r}")
      raise

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
artefact_designation_to_p_number : dict[str, str] = {}

max_lak_number = 0
with open("LAK.html") as f:
  for line in f.readlines():
    match = re.search(r'id=\"(\d+)[a-z]?\"', line)
    if match:
      max_lak_number = int(match.group(1))

print("Max LAK", max_lak_number)

in_signlist = False

NON_VAT_ARTEFACT_DESIGNATION = (
  "(?P<Non_VAT>" +
  "|".join(re.escape(s) for s in artefacts.NON_VAT_ARTEFACTS) +
  "|" +
  r"(?:DP\.?|<!--DP-->) ?[0-9]{1,3}" +
  "|" +
  r"(?:RTC,?|<!--RTC-->) ?[0-9]{1,3}" +
  "|" +
  r"(?:Nik\.?|<!--Nik-->) ?[0-9]{1,3}" +
  ")"
)

# TODO(egg): Automate replacement of
# (DP(?:-->)? ?\d+</a>, ?\d+; *)(\d+)
# with $1<!--DP-->$2

with open("LAK.html") as f:
  for line in f.readlines():
    if '<table class="signlist">' in line:
      in_signlist = True
    if not in_signlist:
      lines.append(line)
      continue
    def linkify_internal(match: re.Match[str]):
      referenced_lak_number = int(match.group("n"))
      if match.group("href") and int(match.group("href")) != referenced_lak_number:
        raise ValueError(f"n. {referenced_lak_number} links to {match.group('href')}")
      if referenced_lak_number < max_lak_number:
        return f'<a href="#{referenced_lak_number}">n. {referenced_lak_number}</a>'
      return match.group(0)
    line = re.sub(r'(?<!\w)(?:<a href="#(?P<href>\d+)">)?n\. (?P<n>\d+)(?:</a>)?', linkify_internal, line)
    def linkify_artefact(match: re.Match[str]):
      vat_number = match.group("VAT") or match.group("Linked_VAT")
      vat_number = int(vat_number) if vat_number else None
      if vat_number:
        vat_numbers_seen.add(vat_number)
      p_number = match.group("P")
      if p_number:
        artefact_designation = match.group("VAT") or match.group("Linked_VAT") or match.group("Other_Artefact") or match.group("Non_VAT")
        if artefact_designation not in artefact_designation_to_p_number:
          artefact_designation_to_p_number[artefact_designation] = p_number
        if artefact_designation_to_p_number[artefact_designation] != p_number:
          raise ValueError(f"Mismatch for {artefact_designation}: Linked to {artefact_designation_to_p_number[artefact_designation]} then {link}")
      else:
        artefact_designation = match.group()
      if artefact_designation.startswith("DP") or artefact_designation.startswith("<!--DP"):
        m = re.search(r"recte (\d+)", artefact_designation)
        if m:
          dp_number = int(m.group(1))
        else:
          dp_number = int(re.sub(r"^(<!--DP-->|DP\.? *)", "", artefact_designation))
      else:
        dp_number = None
      if artefact_designation.startswith("RTC") or artefact_designation.startswith("<!--RTC"):
        m = re.search(r"recte (\d+)", artefact_designation)
        if m:
          rtc_number = int(m.group(1))
        else:
          rtc_number = int(re.sub(r"^(<!--RTC-->|RTC,? *)", "", artefact_designation))
      else:
        rtc_number = None
      if artefact_designation.startswith("Nik") or artefact_designation.startswith("<!--Nik"):
        m = re.search(r"recte (\d+)", artefact_designation)
        if m:
          nik_number = int(m.group(1))
        else:
          nik_number = int(re.sub(r"^(<!--Nik-->|Nik\.? *)", "", artefact_designation))
      else:
        nik_number = None
      if p_number and dp_number and dp_to_p[dp_number] != p_number:
        raise ValueError(f"Mismatch for DP {vat_number}: {match.group('P')} vs. CDLI {dp_to_p[dp_number]}")
      if p_number and rtc_number and rtc_to_p[rtc_number] != p_number:
        raise ValueError(f"Mismatch for RTC {vat_number}: {match.group('P')} vs. CDLI {rtc_to_p[rtc_number]}")
      if p_number and nik_number and nik_to_p[nik_number] != p_number:
        raise ValueError(f"Mismatch for Nik {vat_number}: {match.group('P')} vs. CDLI {nik_to_p[nik_number]}")
      if p_number and vat_number and vat_to_p[vat_number] != p_number:
        raise ValueError(f"Mismatch for VAT {vat_number}: {match.group('P')} vs. EDSL {vat_to_p[vat_number]}")
      if vat_number and not p_number:
        p_number = vat_to_p.get(vat_number)
      if not p_number:
        p_number = artefacts.NON_VAT_ARTEFACTS.get(artefact_designation)
      if not p_number and rtc_number:
        p_number = rtc_to_p[rtc_number]
      if not p_number and dp_number:
        p_number = dp_to_p[dp_number]
      if not p_number and nik_number:
        p_number = nik_to_p[nik_number]
      if p_number:
        return f'<a href="http://cdli.earth/{p_number}">{artefact_designation}</a>'
      else:
        return match.group()
    line = re.sub(r'(?:<a href="https?://cdli.earth/(?P<P>P\d+)">(?:(?P<Linked_VAT>\d{4,})|(?P<Other_Artefact>(?:[^<]|<(?!/a>))*))</a>)|(?:\b|(?=<!--))(?:(?P<VAT>\d{4,})|%s)(?!</a)(?:\b|(?=R))' % NON_VAT_ARTEFACT_DESIGNATION, linkify_artefact, line)
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

p_number_to_artefact_designation : dict[str, set[str]] = defaultdict(set)

with open("artefacts.py", "w") as f:
  print("NON_VAT_ARTEFACTS = {", file=f)
  for designation, p_number in sorted(artefact_designation_to_p_number.items(), key=lambda kv: (-len(kv[0]), kv[0])):
    p_number_to_artefact_designation[p_number].add(designation)
    if not designation.isdigit() or int(designation) not in vat_to_p:
      print(f"  {designation!r} : {p_number!r},", file=f)
  print("}", file=f)

with open("links.log", "w") as f:
  for p_number, designations in sorted(p_number_to_artefact_designation.items()):
    print(p_number, sorted(designations), file=f)