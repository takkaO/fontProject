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
		"""
		フォントファイルからグリフ情報を抽出する
		--- Parameters ---
		char : ターゲットの1文字
		--- Return ---
		グリフ情報
		"""
		# TODO: 数値を直接指定しても良いようにする
		glyph_name = self.cmap[ord(char)]
		return self.glyph_set[glyph_name]
	
	def getVectorControl(self, char):
		"""
		グリフ情報からベクタ画像用の制御点情報を抽出する
		--- Parameters ---
		char : ターゲットの1文字
		--- Return ---
		制御点情報
		"""
		recording_pen = RecordingPen()
		obj = self.getGlyph(char)
		obj.draw(recording_pen)
		return recording_pen.value
	
	def control2Path(self, control):
		"""
		抽出した制御点情報をmatplotlibで描画できる形式に変換する

		--- Parameters ---
		control : getVectorControl()で取得した制御点情報
		--- Return ---
		(座標のリスト, 制御フラグのリスト)
		"""
		dummy_point = (0, 0)
		verts = []
		codes = []

		for val in control:
			print(val)
			if val[0] == "closePath":
				codes.append(Path.CLOSEPOLY)
				verts.append(dummy_point)
			elif val[0] == "moveTo":
				codes.append(Path.MOVETO)
				verts.append(val[1][0])
				## Update close path start point
				dummy_point = val[1][0]
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
	
	def draw(self, char, control_path = True):
		"""
		指定した文字を描画する
		--- Parameters ---
		char : 描画する1文字
		control_path : 制御点も描画するかどうか
		"""
		ctrl = self.getVectorControl(char)
		verts, codes = self.control2Path(ctrl)
		path = Path(verts, codes)

		_, ax = plt.subplots()
		patch = patches.PathPatch(path, facecolor='none', lw=2)
		ax.add_patch(patch)

		## 制御点も描画する
		if control_path:
			## パスの切れ目を抽出
			split_index = [i for i, val in enumerate(codes) if val == Path.CLOSEPOLY]
			xs, ys = zip(*verts)

			start_index = 0
			for end_index in split_index:
				ax.plot(xs[start_index:end_index+1], ys[start_index:end_index+1], 'x--', lw=2, color='black', ms=10)
				start_index = end_index + 1
		else:
			ax.plot()
		#ax.set_xlim(0, 2000)
		#ax.set_ylim(0, 2000)
		#ax.grid()
		plt.show()

def main():
	myfont = MyFont("./IPAfont00303/ipag.ttf")
	#myfont = MyFont("./NotoMono-hinted/NotoMono-Regular.ttf")
	myfont.draw("a")

	
if __name__ == "__main__":
	main()
