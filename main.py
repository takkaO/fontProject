from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from bezier_clipping import BezierClipping
from bezier_module import Bezier3, Bezier4, LineSegment

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
	
	def control2Path(self, control, log=True):
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
			if log:
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
				l = LineSegment(path_start_point, start_point)
				lines.append(l)
			elif val[0] == "moveTo":
				## Update close path start point
				start_point = val[1][0]
				path_start_point = val[1][0]
			elif val[0] == "qCurveTo":
				if len(val[1]) == 2:
					## quadratic Bezier curve
					b = Bezier3(start_point, val[1][0], val[1][1])
					lines.append(b)
					start_point = val[1][1]
				elif len(val[1]) == 3:
					## cubic Bezier curve
					b = Bezier4(start_point, val[1][0], val[1][1], val[1][2])
					lines.append(b)
					start_point = val[1][2]
				else:
					print("Error")
					exit(1)
			elif val[0] == "lineTo":
				l = LineSegment(start_point, val[1][0])
				lines.append(l)
				start_point = val[1][0]
			else:
				print("Uncatch: ", val[0])
		return lines
	
	def draw(self, char, control_path = True, show=True):
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
		if show:
			plt.show()
	
	def fetchGravityPoint(self, arg):
		verts = arg
		if type(arg) == str:
			verts, _ = self.control2Path(self.getVectorControl(arg), log=False)
		
		gx = 0.0
		gy = 0.0
		for point in verts:
			gx += point[0]
			gy += point[1]
		gx /= len(verts)
		gy /= len(verts)

		g_point = np.array([gx, gy])
		return g_point
	
	def make_lines(self, base_line, div_num):
		"""
		ベースラインを基準にdiv_numで指定した数の放射線集合を作成する

		--- Parameters ---
		base_line : 基準となる線（LineSegmentオブジェクト）
		div_num   : 作成する線の数 
		--- Return ---
		lines : LineSegmentの集合
		"""
		deg_per = 360 / div_num
		lines = []
		for n in range(div_num):
			rad = np.deg2rad(deg_per * n)
			l = base_line.translation(base_line.v1).rotate(rad).translation(-base_line.v1)
			lines.append(l)
		return lines
	

	def test2(self, char="a", line_num=32):
		"""
		文字中心から文字交点までの最大，最小の長さ集合を取得する

		--- Parameters ---
		char     : 調査する文字
		line_num : 使用する放射線の数 
		--- Return ---
		selected_point_max : 最大長をとる座標の場所 
		selected_point_min : 最小長をとる座標の場所
		r_max : 最大長集合
		r_min : 最小長集合
		"""
		ctrl = self.getVectorControl(char)
		lines = self.control2Lines(ctrl, log=False)
		verts, _ = self.control2Path(ctrl, log=False)
		
		## 文字の座標範囲をチェック（放射線の長さを決めるのに使用）
		xs, ys = zip(*verts)
		s_x, b_x = min(xs), max(xs)
		s_y, b_y = min(ys), max(ys)

		## 文字を描画（for debug）
		_, ax = plt.subplots()
		for l in lines:
			if isinstance(l, Bezier4) or isinstance(l, Bezier3):
				pass
				ax = l.plot_bezier(ax)
				#l.plot_control_point(ax)
			elif isinstance(l, LineSegment):
				ax = l.plot_line(ax, color="black")
				pass
		
		## アンカーポイントと制御点の重心を取得
		#gp = self.fetchGravityPoint(char)

		## 文字の中心座標を取得
		gp = (s_x + (b_x - s_x) / 2, s_y + (b_y - s_y) / 2)

		## 基準線を作成
		base_line = LineSegment((gp[0], gp[1]), (gp[0] + max(b_x, b_y) ,gp[1]))
		## 放射線との交点を調査
		points = []
		for line in self.make_lines(base_line, line_num):
			tmp = []
			line.plot_line(ax, color="gray")
			for l in lines:
				if isinstance(l, Bezier4) or isinstance(l, Bezier3):
					bc = BezierClipping(l, line)
					ts = bc.clipping()
					if bc.has_failed and bc.result:
						print("Failed occur!!!!")
					if not bc.result:
						continue
					for t in ts:
						p = l.beizer_point(t)
						#ax.plot(p[0], p[1], 'o', color="red")
						if line.is_point_on_line(p):
							#ax.plot(p[0], p[1], 'o', color="blue")
							tmp.append(p)
				elif isinstance(l, LineSegment):
					res = l.cross_point(line)
					if res is None:
						continue
					res = line.cross_point(l)
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
		for p, line in zip(points, self.make_lines(base_line, line_num)):
			max_len = 0
			min_len = line.length
			max_p = gp
			min_p = gp
			for pp in p:
				l1 = LineSegment(gp, pp)
				if max_len < l1.length:
					max_p = pp
					max_len = l1.length
				if min_len > l1.length:
					min_p = pp
					min_len = l1.length
			selected_point_max.append(max_p)
			selected_point_min.append(min_p)
		
		## 抽出した最大点と最小点を描画（for debug）
		xs, ys = zip(*selected_point_max)
		ax.plot(xs, ys, 'o', color="red")
		xs, ys = zip(*selected_point_min)
		ax.plot(xs, ys, '.', color="blue")
		
		## 中心と最大点，最小点の距離集合を作成
		r_max = [LineSegment(gp, p).length for p in selected_point_max]
		r_min = [LineSegment(gp, p).length for p in selected_point_min]

		return selected_point_max, selected_point_min, r_max, r_min


def main():
	char1 = "黑"
	char2 = "黒"
	myfont = MyFont("./IPAfont00303/ipag.ttf")
	#myfont = MyFont("./unifont-12.0.01.ttf")
	#myfont = MyFont("./NotoMono-hinted/NotoMono-Regular.ttf")

	_, _, r1, r2 = myfont.test2(char1)
	n1 = np.array(r1)
	n2 = np.array(r2)
	plt.grid()

	_, _, r3, r4 = myfont.test2(char2)
	n3 = np.array(r3)
	n4 = np.array(r4)

	print(char1, "<->", char2)
	print("Max vector: ", np.dot(n1, n3) / (np.linalg.norm(n1) * np.linalg.norm(n3)))
	print("Min vector: ", np.dot(n2, n4) / (np.linalg.norm(n2) * np.linalg.norm(n4)))

	plt.grid()
	plt.show()


if __name__ == "__main__":
	main()
