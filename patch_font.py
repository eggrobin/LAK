import fontforge

SALT = "'salt' Stylistic Alternatives lookup 3 subtable"
LIGA = "'liga' Standard Ligatures lookup 2 subtable"

font = fontforge.open("LAK.ttf")

def assign(code_point: str, glyph_name: str):
  font.createChar(ord(code_point))
  font.selection.select(glyph_name)
  font.copy()
  font.selection.select(f"u{ord(code_point):X}")
  font.paste()

def add_alternate(code_point: str, glyph_name: str):
  glyph = font['u%X' % ord(code_point)]
  salt = glyph.getPosSub(SALT)
  salt = glyph.getPosSub(SALT)[0][2:] if salt else tuple()
  salt = (*salt, glyph_name)
  glyph.addPosSub(SALT, salt)
  print(f"added salt{len(salt)} to U+{ord(code_point):04X} {code_point}")
  font.buildOrReplaceAALTFeatures()

def add_ligature(code_points: str, glyph_name: str):
  if font[glyph_name].getPosSub(LIGA):
    raise ValueError(f"{glyph_name} already has a LIGA mapping: {font[glyph_name].getPosSub(LIGA)}")
  font[glyph_name].addPosSub(LIGA, tuple('u%X' % ord(code_point) for code_point in code_points))
  print("liga:", " ".join('U+%X' % ord(code_point) for code_point in code_points), "↦", glyph_name)
  font.buildOrReplaceAALTFeatures()

# The index form comes from 12778 (a lexical text), whose dcclt/ebla
# transliteration avoids reading them and calls them LAK011.  It makes sense to
# hold off on identifying that one.  The other form of LAK011 form comes from
# 12610 in še-numun; it is just a sloppy numun=KUL.
add_alternate('𒆰', 'uF009C.1')
# On LAK020, but transliterated bal in dcclt/ebla (in kuš-AN-ti-bal).
add_alternate('𒁄', 'uF0086.1')
# Note that the alternates also become 𒊩𒆳.
add_ligature("𒊩𒆳", "uF00A0")
assign('𒉋', "uF00B0")
add_alternate('𒉋', 'uF00B0.1')
add_alternate('𒉋', 'uF00B0.2')
add_alternate('𒉋', 'uF00B1')
# See https://github.com/oracc/osl/pull/40.
assign('𒌝', f"u{ord('𒈩'):X}")

font.generate("LAK.ttf")
font.close()
