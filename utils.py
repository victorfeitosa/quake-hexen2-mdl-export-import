import importlib

def getPaletteFromName(palette_name):
  palette_module_name = "..{0}pal".format(palette_name.lower())
  palette = importlib.import_module(palette_module_name, __name__).palette
  return palette
