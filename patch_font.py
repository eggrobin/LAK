import fontforge
import hashlib

SALT = "'salt' Stylistic Alternatives lookup 3 subtable"
LIGA = "'liga' Standard Ligatures lookup 2 subtable"

font = fontforge.open("LAK.ttf")

with open("glyph_hashes.log", "w") as log:
  for glyph in font:
    font[glyph].layers[1].export("temp.svg")
    with open("temp.svg", "rb") as f:
      print(glyph, hashlib.sha1(f.read()).hexdigest(), file=log)

def assign(code_point: str, glyph_name: str):
  if ord(code_point) in font:
    raise ValueError(f"{code_point} already in font")
  font.createChar(ord(code_point))
  font.selection.select(glyph_name)
  font.copy()
  font.selection.select(f"u{ord(code_point):X}")
  font.paste()
  print(f"{glyph_name} is U+{ord(code_point):04X} {code_point}")

def add_alternate(code_point: str, glyph_name: str):
  glyph = font['u%X' % ord(code_point)]
  salt = glyph.getPosSub(SALT)
  salt = glyph.getPosSub(SALT)[0][2:] if salt else tuple()
  salt = (*salt, glyph_name)
  glyph.addPosSub(SALT, salt)
  print(f"{glyph_name} is an alternate form (salt{len(salt)}) of U+{ord(code_point):04X} {code_point}")
  font.buildOrReplaceAALTFeatures()

def remove_ligature(code_points: str):
  glyph_name = "_".join('u%X' % ord(code_point) for code_point in code_points) + ".liga"
  if glyph_name not in font:
    raise ValueError(f"No {glyph_name} in font")
  if not font[glyph_name].getPosSub(LIGA):
    raise ValueError(f"{glyph_name} does not have a liga mapping")
  if font[glyph_name].getPosSub(LIGA)[0][2:] != tuple('u%X' % ord(code_point) for code_point in code_points):
    raise ValueError(f"{glyph_name} is not a {code_points} ligature: {font[glyph_name].getPosSub(LIGA)}")
  font[glyph_name].removePosSub(LIGA)

def add_ligature(code_points: str, glyph_name: str):
  if font[glyph_name].getPosSub(LIGA):
    raise ValueError(f"{glyph_name} already has a liga mapping: {font[glyph_name].getPosSub(LIGA)}")
  font[glyph_name].addPosSub(LIGA, tuple('u%X' % ord(code_point) for code_point in code_points))
  print(glyph_name, "is a ligature", *('U+%X' % ord(code_point) for code_point in code_points), code_points)
  font.buildOrReplaceAALTFeatures()

# The index form comes from 12778 (a lexical text), whose dcclt/ebla
# transliteration avoids reading them and calls them LAK011.  It makes sense to
# hold off on identifying that one.  The other form of LAK011 comes from
# 12610 in še-numun; it is just a sloppy numun=KUL.
add_alternate('𒆰', 'uF009C.1')
# On LAK020, but transliterated bal in dcclt/ebla (in kuš-AN-ti-bal).
add_alternate('𒁄', 'uF0086.1')
# Note that the alternates also become 𒊩𒆳.
add_ligature("𒊩𒆳", "uF00A0")
assign('𒉋', "uF00B0")
add_alternate('𒉋', 'uF00B0.1')
add_alternate('𒉋', 'uF00B0.2')
add_alternate('𒉋', 'uF00B0.3')
add_alternate('𒉋', 'uF00B1')
add_alternate('𒉋', 'uF00B1.1')
add_alternate('𒉋', 'uF00B1.2')
# https://github.com/oracc/osl/pull/41.
add_alternate("𒆲", "uF009F")
# TODO(egg): This needs an OSL PR.
assign('𒈱', f"u{ord('𒑍'):X}")
font.removeGlyph(f"u{ord('𒑍'):X}")

# We need to do something about those duplicate encodings.
assign("𒐺", "u1203C")

# TODO(egg): This needs an OSL PR.
remove_ligature("𒉣𒇬")
add_ligature("𒁹𒉣𒇬", "uF133A")
add_ligature("𒉣𒇬", "uF00A2")

# Documented as sequences on https://oracc.museum.upenn.edu/listfontdata/lak/.
add_ligature("𒄷𒋛𒀀", "uF3900")
add_ligature("𒑋𒁇", "uF3901")  # Or 𒑋𒁇?

print("# pp. 11–15 corrections")
add_ligature("𒋀𒆳𒊏", "uF00A5.1")
assign("𒉝", "u12599.2")
add_ligature("𒈥𒊮", f"u{ord('𒈥'):X}.2")
add_ligature("𒄑𒋛", f"u{ord('𒌝'):X}.1")
add_ligature("𒉚𒀀", f"u{ord('𒉚'):X}.6")
assign("𒉛", f"u{ord('𒉚'):X}.8")

print("# pp. 16–18 corrections")
assign("𒑎", f"u{ord('𒑀'):X}.1")
assign("𒑍", f"u{ord('𒄿'):X}.2")
add_ligature("𒋗𒆸𒆸", f"u{ord('𒋗'):X}_u{ord('𒆸'):X}.liga.3")
add_alternate("\U000F00B8", f"uF00AF.1")

font.generate("LAK.ttf")
font.close()
