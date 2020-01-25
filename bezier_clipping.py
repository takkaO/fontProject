from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from bezier_module import Bezier4, LineSegment


def test_detection_point():
	#parent_bp = Bezier4((0, 2), (1.0/3.0, 6), (2.0/3.0, 4), (1, -3))
	parent_bp = Bezier4((0, 2), (0/3.0, 6), (2.0/3.0, 4), (2, -3))
	parent_line = LineSegment((0, 0), (1, 1))

	ax = parent_bp.plot_bezier(color="darkblue")
	parent_bp.plot_control_point(ax, color="gray")
	parent_line.plot_line(ax)

	# 描画
	ax = parent_bp.plot_bezier(color="darkblue")
	parent_bp.plot_control_point(ax)
	parent_line.plot_line(ax)

	bc = BezierClippingOld(parent_bp, parent_line)
	res = bc.recursion_clipping(limit=1e-3, debug=True)
	print(res)
	if res:
		t = round(bc.current_line.v1[0], 3)
		point = parent_bp.beizer_point(t)
		print(point)

		ax.plot(point[0], point[1], 'o', color="red")
	plt.grid()
	plt.show()


class BezierClippingOld:
	def __init__(self, parent_bezier, parent_line):
		# 現状ではx:0-1に正規化されているものとする
		# Bezier4とLineSegmentオブジェクト
		self.parent_bezier = parent_bezier
		self.parent_line = parent_line
		self.current_bezier = parent_bezier
		self.current_line = parent_line
	
	def recursion_clipping(self, limit=1e-3, debug=False):
		try:
			while self.current_line.length > limit:
				ax = None
				if debug:
					_, ax = plt.subplots()
					self.parent_line.plot_line(ax)
					self.parent_bezier.plot_bezier(ax, color="darkblue")
				nb, nl = self.clipping(ax)

				if not nb is None:
					self.current_bezier, self.current_line = nb, nl
				else:
					return False
			return True
		except:
			import traceback
			traceback.print_exc()
			return False
	
	def clipping(self, ax = None):
		# 凸包の4線分を取得
		convex = self.current_bezier.getConvexLineSegment()
		if not ax is None:
			for line in convex:
				line.plot_line(ax, '--', color="gray")
		

		t = []
		for i in range(len(convex)):
			p = convex[i].cross_point(self.current_line, 1e-12)
			if not p is None:
				t.append(p)
				if not ax is None:
					ax.plot(p[0], p[1], 'o-', color="red")
		if len(t) < 2:
			print("No cross point") 

		# tmin, tmax
		t = sorted(t)
		print("t:", t)

		p = []
		for i in range(len(t)):
			# ベジェ曲線上のポイントを取得
			z = self.parent_bezier.beizer_point(t[i][0])
			p.append(z)
			if not ax is None:
				ax.plot(z[0], z[1], 'o', color="blue")
				LineSegment(t[i], z).plot_line(ax, ':', color="green")

		_, b1 = self.parent_bezier.split_bezier(self.parent_line.calc_rate(t[0]), p[0])

		rate = LineSegment(t[0], self.parent_line.v2).calc_rate(t[1])

		b2, _ = b1.split_bezier(rate, p[1])
		if not ax is None:
			b2.plot_bezier(ax)
			convex = b2.getConvexLineSegment()
			for line in convex:
				line.plot_line(ax, '--', color="gray")
			plt.grid()

		return b2, LineSegment(t[0], t[1])	

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
			return None
		else:
			return None

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
			# TODO:1個だけの場合
			print("No cross point")
			return current_line.midpoint[0], False
		
		# tmin, tmax
		t = sorted(t)
		print("t:", t)

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
	#test_detection_point()

	parent_bp = Bezier4((0, 2), (0.0/3.0, 3), (1.0/3.0, -4), (1.0, -3))
	parent_line = LineSegment((0, 0), (0.7, 2))

	
	ax = parent_bp.plot_bezier(color="darkblue")
	parent_bp.plot_control_point(ax, color="gray")
	parent_line.plot_line(ax)

	bc = BezierClipping(parent_bp, parent_line)
	t, res = bc.clipping(limit=1e-3)

	print(t)
	print(res)

	bc.converted_bezier.plot_bezier(ax)

	point = parent_bp.beizer_point(t)
	ax.plot(point[0], point[1], 'o', color="red")

	plt.grid()
	plt.show()

	
	

if __name__ == "__main__":
	main()
