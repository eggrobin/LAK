
import html.parser
import pprint
import re
from typing import Optional
import urllib.request

def deromanize(s: str) -> int:
  numerals = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000}
  total = 0
  last_value = None
  for c in s.lower():
     value = numerals[c]
     if last_value and value > last_value:
       total += value - last_value
       last_value = None
     else:
       if last_value:
         total += last_value
       last_value = value
  if last_value:
    total += last_value
  return total

class Parser(html.parser.HTMLParser):
    line_id : Optional[str] = None
    xlabel_start : Optional[str] = None

    def __init__(self, *, convert_charrefs: bool = True) -> None:
      self.line_to_id: dict[tuple[str, ...], Optional[str]] = {}
      super().__init__(convert_charrefs=convert_charrefs)

    def handle_starttag(self, tag : str, attrs : list[tuple[str, Optional[str]]]):
        attributes = dict(attrs)
        if 'class' in attributes and attributes['class']:
          classes = attributes['class'].split()
        else:
           return
        if (tag == 'tr' and 'l' in classes and 'id' in attributes):
          self.line_id = attributes['id']
        if 'xlabel' in classes:
           self.xlabel_start = tag

    def handle_endtag(self, tag : str):
        if tag == self.xlabel_start:
           self.xlabel_start = None
        if tag == 'tr':
           self.line_id = None

    def handle_data(self, data : str):
        if self.xlabel_start:
           line_number = tuple(str(deromanize(s)) if re.match(r'^[ivxlcdm]+$', s) else s for s in data.split())
           self.line_to_id[line_number] = self.line_id or None

def get_line_to_id_map(project: str, artefact: str):
  with urllib.request.urlopen('https://oracc.museum.upenn.edu/' + project + '/' + artefact) as f:
    page = f.read().decode('utf-8')
  parser = Parser()
  parser.feed(page)
  return parser.line_to_id

with open("gud_cyl.py", mode="w") as f:
  print("LOCATIONS =\\", file=f)
  pprint.pp(get_line_to_id_map("etcsri", "Q000377"), stream=f)