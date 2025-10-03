import fontforge

SALT = "'salt' Stylistic Alternatives lookup 3 subtable"

font = fontforge.open("LAK.ttf")

def add_alternate(code_point: str, glyph_name: str):
  glyph = font['u%X' % ord(code_point)]
  salt = glyph.getPosSub(SALT)
  salt = glyph.getPosSub(SALT)[0][2:] if salt else tuple()
  salt = (*salt, glyph_name)
  glyph.addPosSub(SALT, salt)
  print(f"added salt{len(salt)} to U+{ord(code_point):04X} {code_point}")
  font.buildOrReplaceAALTFeatures()

# Straightforward.
add_alternate('𒀭', 'u1202D.1.2')
# The index form comes from 12778 (a lexical text), whose dcclt/ebla
# transliteration avoids reading them and calls them LAK011.  It makes sense to
# hold off on identifying that one.  The other form of LAK011 form comes from
# 12610 in še-numun; it is just a sloppy numun=KUL.
add_alternate('𒆰', 'uF009C.1')
# On LAK020, but transliterated bal in dcclt/ebla (in kuš-AN-ti-bal).
add_alternate('𒁄', 'uF0086.1')
# LAK120.
add_alternate('𒍜', 'uF00AB')
font.createChar(ord("𒉋"))
font.selection.select(f"uF00B0")
font.copy()
font.selection.select(f"u{ord('𒉋'):X}")
font.paste()
add_alternate('𒉋', 'uF00B0.1')
add_alternate('𒉋', 'uF00B0.2')
add_alternate('𒉋', 'uF00B1')

font.generate("LAK.ttf")
font.close()
