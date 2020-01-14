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
		dummy_point = None
		verts = []
		codes = []
		# set dummy point
		for val in control:
			# 別に(0, 0)でもいい
			if not val[0] == "closePath":
				dummy_point = val[1][0]
				break

		for val in control:
			print(val)
			if val[0] == "closePath":
				codes.append(Path.CLOSEPOLY)
				verts.append(dummy_point)
			elif val[0] == "moveTo":
				codes.append(Path.MOVETO)
				verts.append(val[1][0])
			elif val[0] == "qCurveTo":
				if len(val[1]) == 2:
					## quadratic Bezier curve
					codes.append(Path.CURVE3)
					verts.append(val[1][0])
					codes.append(Path.CURVE3)
					verts.append(val[1][1])
				elif len(val[1]) == 3:
					## cubic Bezier curve
					codes.append(Path.CURVE4)
					verts.append(val[1][0])
					codes.append(Path.CURVE4)
					verts.append(val[1][1])
					codes.append(Path.CURVE4)
					verts.append(val[1][2])
				else:
					print("Error")
					exit(1)
			elif val[0] == "lineTo":
				codes.append(Path.LINETO)
				verts.append(val[1][0])
			else:
				print("Uncatch: ", val[0])	
		return verts, codes
	
	def draw(self, char):
		ctrl = self.getBeizerControl(char)
		verts, codes = self.control2Path(ctrl)
		path = Path(verts, codes)

		_, ax = plt.subplots()
		patch = patches.PathPatch(path, facecolor='none', lw=2)
		ax.add_patch(patch)

		## パスの切れ目を抽出
		split_index = [i for i, val in enumerate(codes) if val == Path.CLOSEPOLY]

		xs, ys = zip(*verts)
		#ax.plot()
		
		start_index = 0
		for end_index in split_index:
			ax.plot(xs[start_index:end_index], ys[start_index:end_index], 'x--', lw=2, color='black', ms=10)
			start_index = end_index
		plt.show()

def main():
	myfont = MyFont("./IPAfont00303/ipag.ttf")
	#myfont = MyFont("./NotoMono-hinted/NotoMono-Regular.ttf")
	myfont.draw("A")

	
if __name__ == "__main__":
	main()
