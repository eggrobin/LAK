from collections import defaultdict
import csv
import os
import re

import artefacts

lines : list[str] = []

refs : dict[str, list[int]] = {}
vat_to_p : dict[int, str] = {}
dp_to_p : dict[int, str] = {}
rtc_to_p : dict[int, str] = {}
nik_to_p : dict[int, str] = {}
ct_to_p : dict[int, dict[int, list[str]]] = {}
tdt_to_p : dict[int, dict[int, str]] = {}

ct_keys : list[str] = ["n/a", "King1896CT1"]

# Key: LAK number, CT volume, CT plate, Deimel’s disambiguator.
# Value: Artefact referred to, count of artefacts on the plate.
CT_DISAMBIGUATION = {
  ( "16" ,  7,  4,  "a") : ("P315281", 4),
  ( "40" ,  5, 39, None) : ("P108485", 2),
  ( "41" ,  7, 29,  "a") : ("P108530", 2),
  ( "48" ,  5, 50,  "b") : ("P108493", 2),
  ( "63" ,  7, 29,  "b") : ("P108530", 2),
  ( "63" ,  7, 43,  "a") : ("P108555", 2),
  # TODO(egg): Maybe also P212954 (but not P212952).
  ("148" ,  1,  1, None) : ("P212953", 3),
  ("156" ,  7, 25,  "b") : ("P108521", 2),
  ("179" ,  5, 46, None) : ("P108490", 2),
  ("180" ,  5, 46, None) : ("P108490", 2),
  ("193" , 10, 46,  "c") : ("P108641", 4),
  ("194" ,  3, 18, None) : ("P108452", 5),
  ("194" ,  3, 16,  "c") : ("P108446", 4),
  ("205" ,  7, 31,  "a") : ("P108533", 2),
  ("214" ,  7, 18,  "a") : ("P108507", 2),
  ("221b",  7, 38,  "b") : ("P108548", 2),
  ("240" , 32, 36, None) : ("P108676", 2),
  ("282" ,  7, 20, None) : ("P108511", 2),
  ("287" , 10, 49,  "d") : ("P108656", 4),
  ("289" ,  7, 20,  "b") : ("P108512", 2),
  ("308" ,  7, 21, None) : ("P108513", 2),
  ("323" ,  5, 46, None) : ("P108489", 2),
}

KNOWN_AMBIGUITIES = set(("CT 5, 46",))

with open("CT.csv", encoding="utf-8") as f:
  for i, line in enumerate(csv.reader(f)):
    if i == 0:
      continue
    if line[16].isdigit() or line[0].endswith("CT9"):
      volume = 9 if line[0].endswith("CT9") else int(line[16])
      while len(ct_keys) <= volume:
        ct_keys.append("n/a")
      ct_keys[volume] = line[0]

for name in os.listdir():
  match = re.match(r"CT(\d+).csv", name)
  if match:
    number = int(match.group(1))
    key = ct_keys[number]
    volume = defaultdict(list)
    with open(name, encoding="utf-8") as f:
      for i, line in enumerate(csv.reader(f)):
        if i == 0:
          continue
        if line[40] == "composite text":
          continue
        try:
          publications = [p.strip() for p in line[3].split(";")]
          reference = line[5].split(";")[publications.index(key)]
          ct_range = reference.strip().removeprefix("pl. ").split(",")[0].split(" BM ")[0].split("(")[0]
          try:
            if "-" in ct_range:
              first, last = ct_range.split("-")
              cts = range(int(first), int(last)+1)
            else:
              cts = (int(ct_range),)
          except ValueError as e:
            print(f"Weird plate number CT {number}, {ct_range} = P{int(line[0]):06}")
            continue
          for ct in cts:
            volume[ct].append(f"P{int(line[0]):06}")
        except Exception as e:
          print(line)
          raise
    ct_to_p[number] = volume

  
# See this mess: https://cdli.earth/publications/1734640.
# Unfortunately this kind of join of publications means we do not get those in the CSV dumps for a CT volume.
ct_to_p[25][8] = ["P365753"]

with open("Nik.csv", encoding="utf-8") as f:
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

for volume, key in ((1, "Thureau-Dangin1910ITT1"),
                    (2, "Genouillac1910-1911ITT2"),
                    (3, "deGenouillac1912ITT3")):  # Argh!
  with open(f"TDT{volume}.csv", encoding="utf-8") as f:
    tdt_volume = {}
    for i, line in enumerate(csv.reader(f)):
      if i == 0:
        continue
      try:
        publications = [p.strip() for p in line[3].split(";")]
        tdt = line[5].split(";")[publications.index(key)].strip()
        if not tdt.isdigit():
          print(f"Weird number TDT {volume}, {tdt}")
          continue
        tdt = int(tdt)
        if (line[2].startswith("ITT") and
            "+" not in line[2] and
            line[2].strip() != f"ITT {volume}, {tdt:05}"):
          raise ValueError(f'{line[2].strip()!r} != {f"ITT {volume}, {tdt:05}"!r}')
        tdt_volume[tdt] = f"P{int(line[0]):06}"
      except Exception as e:
        print(line)
        raise
      tdt_to_p[volume] = tdt_volume

with open("Nik.csv", encoding="utf-8") as f:
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

with open("DP.csv", encoding="utf-8") as f:
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

with open("RTC.csv", encoding="utf-8") as f:
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

with open("../edsl/lak/etc/lak-refs.tsv", encoding="utf-8") as f:
  for line in csv.reader(f, delimiter="\t"):
    refs[line[0].removeprefix("LAK").lstrip("0")] = [int(n) for n in line[1:] if n and n != "TSA_6"]

with open("../edsl/lak/etc/vat.P", encoding="utf-8") as f:
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
with open("LAK.html", encoding="utf-8") as f:
  for line in f.readlines():
    match = re.search(r'id=\"(\d+)[a-z]?\"', line)
    if match:
      max_lak_number = int(match.group(1))

print("Max LAK", max_lak_number)

in_signlist = False

NON_VAT_ARTEFACT_DESIGNATION = (
  "(?P<Non_VAT>" +
  "|".join(re.escape(s) for s in sorted(artefacts.NON_VAT_ARTEFACTS, key=lambda k: -len(k))) +
  "|" +
  r"(?:DP\.?|<!--DP-->) ?[0-9]{1,3}" +
  "|" +
  r"(?:RTC,?|<!--RTC-->) ?[0-9]{1,3}" +
  "|" +
  r"(?:Nik\.?|<!--Nik-->) ?[0-9]{1,3}" +
  "|" +
  r"(?:<!--)?CT ?\d+(?:,|-->) ?\d+(?:(?: |<br>)*[a-z](?:\)|(?=[,\d])))?" +
  "|" +
  r"(?:<!--)?TDT(?:-->)? ?\d+(?:,? ?II|,|-->) ?\d+" +
  ")"
)

# TODO(egg): Automate replacement of
# (DP(?:-->)? ?\d+</a>, ?\d+; *)(\d+)
# with $1<!--DP-->$2

with open("LAK.html", encoding="utf-8") as f:
  for line in f.readlines():
    if '<table class="signlist">' in line:
      in_signlist = True
    if not in_signlist:
      lines.append(line)
      continue
    def linkify_internal(match: re.Match[str]):
      referenced_lak_number = int(match.group("n"))
      suffix = match.group("suffix") or ""
      if match.group("href") and match.group("href") != f"{referenced_lak_number}{suffix.removesuffix(')')}":
        raise ValueError(f"n. {referenced_lak_number}{suffix} links to {match.group('href')}")
      if referenced_lak_number < max_lak_number:
        return f'<a href="#{referenced_lak_number}{suffix}">n. {referenced_lak_number}{f"<sup>{suffix}</sup>" if suffix else ""}</a>'
      return match.group(0)
    line = re.sub(r'(?<!\w)(?:<a href="#(?P<href>\d+[a-z]?)">)?n\. (?P<n>\d+)(?:<sup>(?P<suffix>[a-z])\)?</sup>)?(?:</a>)?', linkify_internal, line)
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
        if artefact_designation_to_p_number[artefact_designation] != p_number and artefact_designation not in KNOWN_AMBIGUITIES:
          raise ValueError(f"Mismatch for {artefact_designation}: Linked to {artefact_designation_to_p_number[artefact_designation]} then {p_number}")
      else:
        artefact_designation = match.group()
      if artefact_designation.removeprefix("<!--").startswith("DP"):
        m = re.search(r"recte (\d+)", artefact_designation)
        if m:
          dp_number = int(m.group(1))
        else:
          dp_number = int(re.sub(r"^(<!--DP-->|DP\.? *)", "", artefact_designation))
      else:
        dp_number = None
      if artefact_designation.removeprefix("<!--").startswith("RTC"):
        m = re.search(r"recte (\d+)", artefact_designation)
        if m:
          rtc_number = int(m.group(1))
        else:
          rtc_number = int(re.sub(r"^(<!--RTC-->|RTC,? *)", "", artefact_designation))
      else:
        rtc_number = None
      if artefact_designation.removeprefix("<!--").startswith("Nik"):
        m = re.search(r"recte (\d+)", artefact_designation)
        if m:
          nik_number = int(m.group(1))
        else:
          nik_number = int(re.sub(r"^(<!--Nik-->|Nik\.? *)", "", artefact_designation))
      else:
        nik_number = None
      ct_volume, ct_plate, p_from_ct = None, None, None
      if artefact_designation.removeprefix("<!--").startswith("CT"):
        m = re.match(r"(?:<!--)?CT ?(\d{1,2})(?:,|-->) ?(\d{1,2})(?:(?: |<br>)*([a-z])\)?)?$", artefact_designation)
        ct_volume, ct_plate, ct_disambiguator = int(m.group(1)), int(m.group(2)), m.group(3)
        candidates = ct_to_p[ct_volume][ct_plate]
        if candidates:
          disambiguation, count = CT_DISAMBIGUATION.get(
            (lak_number, ct_volume, ct_plate, ct_disambiguator),
            (None, 1))
          if disambiguation:
            if count != len(candidates):
              raise ValueError(f"""Disambiguation of reference {
                artefact_designation} in LAK {lak_number}: Expected {
                count}, got {len(candidates)} candidates""")
            if disambiguation not in candidates:
              raise ValueError(f"""Disambiguation {
                disambiguation} not in candidates {candidates} for CT {
                ct_volume}, {ct_plate}""")
            p_from_ct = disambiguation
          elif len(candidates) > 1:
            raise ValueError(f"""Ambiguous reference {
              artefact_designation} in LAK {
              lak_number} could be any of the following:{
              ''.join(f'{chr(0xA)}    http://cdli.earth/{n}'
                      for n in ct_to_p[ct_volume][ct_plate])}""")
          else:
            p_from_ct, = candidates
      tdt_volume, tdt_number = None, None
      if artefact_designation.removeprefix("<!--").startswith("TDT"):
        m = re.match(r"(?:<!--)?TDT(?:-->)? ?([123])(?:,? ?II|,|-->) ?(\d+)$", artefact_designation)
        if not m:
          raise ValueError(f"Could not parse TDT reference {artefact_designation}")
        tdt_volume, tdt_number = int(m.group(1)), int(m.group(2))
      if p_number and dp_number and dp_to_p[dp_number] != p_number:
        raise ValueError(f"Mismatch for DP {dp_number}: {match.group('P')} vs. CDLI {dp_to_p[dp_number]}")
      if p_number and rtc_number and rtc_to_p[rtc_number] != p_number:
        raise ValueError(f"Mismatch for RTC {rtc_number}: {match.group('P')} vs. CDLI {rtc_to_p[rtc_number]}")
      if p_number and nik_number and nik_to_p[nik_number] != p_number:
        raise ValueError(f"Mismatch for Nik {nik_number}: {match.group('P')} vs. CDLI {nik_to_p[nik_number]}")
      if p_number and ct_volume and p_from_ct != p_number:
        raise ValueError(f"Mismatch for CT {ct_volume}, {ct_plate}: {match.group('P')} vs. CDLI {p_from_ct}")
      if p_number and tdt_volume and tdt_number and tdt_to_p[tdt_volume][tdt_number] != p_number:
        raise ValueError(f"Mismatch for TDT {tdt_volume}, {tdt_number}: {match.group('P')} vs. CDLI {tdt_to_p[tdt_volume][tdt_number]}")
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
      if not p_number and p_from_ct:
        p_number = p_from_ct
      if not p_number and tdt_volume and tdt_number:
        p_number = tdt_to_p[tdt_volume][tdt_number]
      if p_number:
        return f'<a href="http://cdli.earth/{p_number}">{artefact_designation}</a>'
      else:
        return match.group()
    line = re.sub(r'(?:<a href="https?://cdli.earth/(?P<P>P\d+)">(?:(?P<Linked_VAT>\d{4,})|(?P<Other_Artefact>(?:[^<]|<(?!/a>))*))</a>)|(?:\b|(?=<!--))(?:(?P<VAT>\d{4,})|%s)(?!</a)(?:(?<=[a-z])(?=\d)|(?<=\))|\b|(?=R))' % NON_VAT_ARTEFACT_DESIGNATION, linkify_artefact, line)
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

with open("LAK.html", "w", encoding="utf-8") as f:
  f.writelines(lines)

p_number_to_artefact_designation : dict[str, set[str]] = defaultdict(set)

with open("artefacts.py", "w", encoding="utf-8") as f:
  print("NON_VAT_ARTEFACTS = {", file=f)
  for designation, p_number in sorted(artefact_designation_to_p_number.items(), key=lambda kv: kv[1]):
    p_number_to_artefact_designation[p_number].add(designation)
    if not designation.isdigit() or int(designation) not in vat_to_p:
      print(f"  {designation!r} : {p_number!r},", file=f)
  print("}", file=f)

with open("links.log", "w", encoding="utf-8") as f:
  for p_number, designations in sorted(p_number_to_artefact_designation.items()):
    print(p_number, sorted(designations), file=f)