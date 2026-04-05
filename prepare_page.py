import re

lines = []
id = 0
in_template = False

with open("LAK.html", encoding="utf-8") as f:
  for line in f.readlines():
    match = re.search(r'th id="(\d+)"', line)
    if match:
      id = int(match.group(1))
    if re.search(r'th id="NNN"', line):
      id += 1
    if "<!-- Template:" in line:
      in_template = True
    lines.append(line if in_template else line.replace("NNN", str(id)))

with open("LAK.html", encoding="utf-8", mode="w") as f:
  f.writelines(lines)
