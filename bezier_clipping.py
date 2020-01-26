from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from bezier_module import Bezier3, Bezier4, LineSegment


class BezierClipping:
	def __init__(self, bezier, line):
		self.original_bezier = bezier
		self.original_line = line

		# 変換処理
		self.converted_bezier = self.convert_bezier(self.original_bezier, self.original_line)
		self.converted_line = LineSegment((0,0), (1,0))

	def convert_bezier(self, bezier, line):
		a, b, c = line.equation_coefficient
		tmp = []
		n = len(bezier.verts) - 1
		for i, point in enumerate(bezier.verts):
			d = (a * point[0] + b * point[1] + c) / (np.sqrt(a**2 + b**2))
			tmp.append((i/n, d))
		
		if n == 3:
			# 3次ベジェ
			return Bezier4(tmp[0], tmp[1], tmp[2], tmp[3])
		elif n == 2:
			# 2次ベジェ
			return Bezier3(tmp[0], tmp[1], tmp[2])
		else:
			print("Covert Error")
			exit()
		
	def has_cross_point(self, current_bezier=None, current_line=None):
		if current_bezier is None:
			current_bezier = self.converted_bezier
		if current_line is None:
			current_line = self.converted_line
		# 凸包の4線分を取得
		convex = current_bezier.getConvexLineSegment()

		t = []
		for i in range(len(convex)):
			p = convex[i].cross_point(current_line)
			if not p is None:
				t.append(p)

		# TODO:1個だけの場合の処理を追加
		return len(t) >= 2

	def clipping(self, current_bezier = None, current_line = None, limit=1e-3):
		if current_bezier is None:
			current_bezier = self.converted_bezier
		if current_line is None:
			current_line = self.converted_line
		# 凸包の4線分を取得
		convex = current_bezier.getConvexLineSegment()

		t = []
		for i in range(len(convex)):
			p = convex[i].cross_point(current_line)
			if not p is None:
				t.append(p)
		
		if len(t) < 2:
			# TODO:1個だけの場合の処理を追加
			#print("No cross point")
			return current_line.midpoint[0], False
		
		# tmin, tmax
		t = sorted(t)
		#print("t:", t)

		p = []
		for i in range(len(t)):
			# ベジェ曲線上のポイントを取得
			z = self.converted_bezier.beizer_point(t[i][0])
			p.append(z)
		
		_, b1 = self.converted_bezier.split_bezier(self.converted_line.calc_rate(t[0]), p[0])
		
		rate = LineSegment(t[0], self.converted_line.v2).calc_rate(t[1])

		next_bezier, _ = b1.split_bezier(rate, p[1])
		next_line = LineSegment(t[0], t[1])

		if next_line.length <= limit:
			return next_line.midpoint[0], True
		return self.clipping(next_bezier, next_line)

def main():
	print("Hello World")
	#parent_bp = Bezier4((0, 2), (0.0/3.0, 3), (1.0/3.0, 4), (1.0, -3))
	parent_bp = Bezier3((0, 2), (1.0/3.0, 4), (1.0, -3))

	parent_line = LineSegment((0, 0), (0.4, 2))

	
	ax = parent_bp.plot_bezier(color="darkblue")
	parent_bp.plot_control_point(ax, color="gray")
	parent_line.plot_line(ax)
	
	
	bc = BezierClipping(parent_bp, parent_line)
	t, res = bc.clipping(limit=1e-3)

	print(t)
	print(res)

	bc.converted_bezier.plot_bezier(ax)

	point = parent_bp.beizer_point(t)
	if parent_line.is_point_on_line(point):
		ax.plot(point[0], point[1], 'o', color="red")
	else:
		print("Out of Range")

	plt.grid()
	plt.show()

	
	

if __name__ == "__main__":
	main()
