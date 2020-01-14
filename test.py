from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

class MyFont:
	def __init__(self, font_path):
		self.font = TTFont(font_path)
		self.glyph_set = self.font.getGlyphSet()
		self.cmap = self.font.getBestCmap()
	
	def getGlyph(self, char):
		glyph_name = self.cmap[ord(char)]
		return self.glyph_set[glyph_name]
	
	def getBeizerControl(self, char):
		recording_pen = RecordingPen()
		obj = self.getGlyph(char)
		obj.draw(recording_pen)
		return recording_pen.value
	
	def control2Path(self, control):
		previous = ""
		verts = []
		codes = []
		for val in control:
			if val[0] == "closePath":
				codes.append(Path.STOP)
				verts.append([0,0])
			elif val[0] == "moveTo":
				codes.append(Path.MOVETO)
				verts.append(val[1][0])
			elif val[0] == "qCurveTo":
				codes.append(Path.CURVE3)
				verts.append(val[1][0])
				codes.append(Path.CURVE3)
				verts.append(val[1][1])
				#TODO:previous
			elif val[0] == "lineTo":
				codes.append(Path.LINETO)
				verts.append(val[1][0])
			previous = val[0]
		return verts, codes
	
	def draw(self, char):
		ctrl = self.getBeizerControl(char)
		verts, codes = self.control2Path(ctrl)
		path = Path(verts, codes)

		_, ax = plt.subplots()
		patch = patches.PathPatch(path, facecolor='none', lw=2)
		ax.add_patch(patch)

		xs, ys = zip(*verts)
		ax.plot(xs, ys, 'x--', lw=2, color='black', ms=10)
		plt.show()

def main():
	myfont = MyFont("./IPAfont00303/ipam.ttf")
	myfont.draw("a")
	

	
if __name__ == "__main__":
	main()
