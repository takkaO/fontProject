from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen, DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
import matplotlib.pyplot as plt
import numpy as np
from bezier_clipping_module.bezier_clipping import BezierClipping
from bezier_clipping_module.line_module import Point, Bezier, PlaneLine

import warnings
warnings.filterwarnings('error')

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
		if isinstance(char, int):
			glyph_name = self.cmap[char]
		else:
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
		#recording_pen = RecordingPen()
		recording_pen = DecomposingRecordingPen(self.glyph_set)
		obj = self.getGlyph(char)
		obj.draw(recording_pen)
		return recording_pen.value
	
	def control2Lines(self, control, log=True):
		"""
		抽出した制御点情報をベジェ曲線と直線の集合系に変換する

		--- Parameters ---
		control : getVectorControl()で取得した制御点情報
		--- Return ---
		lines : Bezier3, Bezier4, LineSegment の集合
		"""
		path_start_point = None
		start_point = None
		lines = []

		for val in control:
			if log:
				print(val)
			if val[0] == "closePath":
				l = PlaneLine([path_start_point, start_point])
				lines.append(l)
			elif val[0] == "moveTo":
				## Update close path start point
				start_point = val[1][0]
				path_start_point = val[1][0]
			elif val[0] == "qCurveTo" or val[0] == "curveTo":
				b = Bezier([start_point] + list(val[1]))
				lines.append(b)
				start_point = tuple(b.plist[-1])
			elif val[0] == "lineTo":
				l = PlaneLine([start_point, val[1][0]])
				lines.append(l)
				start_point = val[1][0]
			elif val[0] == "addComponent":
				print("[ERROR] 'addComponent' is not implemented!")
				print("Please use 'DecomposingRecordingPen'")
			else:
				print("[ERROR] Unknown command: ", val[0])
		return lines
	
	def draw(self, char, control_path = False, show=True):
		"""
		指定した文字を描画する
		--- Parameters ---
		char : 描画する1文字
		control_path : 制御点も描画するかどうか
		"""
		ctrl = self.getVectorControl(char)
		lines = self.control2Lines(ctrl, False)
		
		ax = None
		for line in lines:
			if isinstance(line, Bezier):
				ax = line.plot(ax, control_path, resolution=20)
			elif isinstance(line, PlaneLine):
				ax = line.plot(ax, linestyle="-", color="black")
		#ax.set_xlim(0, 2000)
		#ax.set_ylim(0, 2000)
		#ax.grid()
		if show:
			plt.show()
		return ax
	

	def make_lines(self, base_line, div_num):
		"""
		ベースラインを基準にdiv_numで指定した数の放射線集合を作成する

		--- Parameters ---
		base_line : 基準となる線（PlaneLineオブジェクト）
		div_num   : 作成する線の数 
		--- Return ---
		lines : PlaneLineの集合
		"""
		deg_per = 360 / div_num
		lines = []
		for n in range(div_num):
			rad = np.deg2rad(deg_per * n)
			l = base_line.translation().rotate(rad).translation(base_line.plist[0])
			lines.append(l)
		return lines
	
	
	def fetch_distance_vectors(self, char="a", line_num=32, debug=False):
		"""
		文字中心から文字交点までの最大，最小の長さ集合を取得する

		--- Parameters ---
		char     : 調査する文字
		line_num : 使用する放射線の数 
		--- Return ---
		selected_point_max : 最大長をとる座標の集合 
		selected_point_min : 最小長をとる座標の集合
		r_max : 最大長集合
		r_min : 最小長集合
		"""
		ctrl = self.getVectorControl(char)
		lines = self.control2Lines(ctrl, log=False)
		
		## 文字の座標範囲をチェック（放射線の長さを決めるのに使用）
		verts = [p for line in lines for p in line.plist]
		xs, ys = zip(*verts)
		min_p = Point(min(xs), min(ys))
		max_p = Point(max(xs), max(ys))
		
		if debug:
			## 文字を描画（for debug）
			ax = self.draw(char, show=False)

		## 文字の中心座標を取得
		gp = Point(min_p.x + (max_p.x - min_p.x) / 2, min_p.y + (max_p.y - min_p.y) / 2)

		## 基準線を作成
		base_line = PlaneLine([gp.point, (gp.x + max(max_p.x, max_p.y) ,gp.y)])
		radial_lines = self.make_lines(base_line, line_num)
		if debug:
			for line in radial_lines:
				line.plot(ax, color="gray")


		## 放射線との交点を調査
		points = []
		bc = BezierClipping()
		for line in radial_lines:
			tmp = []
			for l in lines:
				if isinstance(l, Bezier):
					result = bc.detect_intersection(l, line)
					if result == []:
						continue
					_, ps = zip(*result)
					for p in ps:
						tmp.append(p)
				elif isinstance(l, PlaneLine):
					res = l.intersection(line)
					if res is None:
						continue
					#print("line", res)
					#ax.plot(res[0], res[1], 'o', color="red")
					#plt.pause(1)
					tmp.append(res)
			points.append(tmp)

		## 1つの線に対して最大点と最小点だけを抽出
		selected_point_max = []
		selected_point_min = []
		for p, line in zip(points, radial_lines):
			max_len = 0
			min_len = line.length
			max_p = gp
			min_p = gp
			for pp in p:
				l1 = PlaneLine([gp, pp])
				if max_len < l1.length:
					max_p = pp
					max_len = l1.length
				if min_len > l1.length:
					min_p = pp
					min_len = l1.length
			selected_point_max.append(max_p.point)
			selected_point_min.append(min_p.point)
		
		if debug:
			## 抽出した最大点と最小点を描画（for debug）
			xs, ys = zip(*selected_point_max)
			ax.plot(xs, ys, 'o', color="red")
			xs, ys = zip(*selected_point_min)
			ax.plot(xs, ys, '.', color="blue")
		
		## 中心と最大点，最小点の距離集合を作成
		r_max = [PlaneLine([gp.point, p]).length for p in selected_point_max]
		r_min = [PlaneLine([gp.point, p]).length for p in selected_point_min]

		return selected_point_max, selected_point_min, r_max, r_min
		

def main():
	char1 = "黑"
	char2 = "黒"
	myfont = MyFont("./IPAfont00303/ipag.ttf")	
	#myfont = MyFont("./unifont-12.0.01.ttf")
	#myfont = MyFont("./NotoMono-hinted/NotoMono-Regular.ttf")
	#myfont = MyFont("./Ubuntu-R.ttf")

	line_num = 32

	_, _, r1, r2 = myfont.fetch_distance_vectors(char1, line_num, debug = True)
	n1 = np.array(r1)
	n2 = np.array(r2)
	plt.grid()

	_, _, r3, r4 = myfont.fetch_distance_vectors(char2, line_num, debug=True)
	n3 = np.array(r3)
	n4 = np.array(r4)

	print(char1, "<->", char2)
	print("Max vector: ", np.dot(n1, n3) / (np.linalg.norm(n1) * np.linalg.norm(n3)))
	print("Min vector: ", np.dot(n2, n4) / (np.linalg.norm(n2) * np.linalg.norm(n4)))

	plt.grid()
	plt.show()


if __name__ == "__main__":
	main()
