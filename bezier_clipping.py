from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from bezier_module import Bezier4, LineSegment

class BezierClipping:
	def __init__(self, parent_bezier, parent_line):
		# 現状ではx:0-1に正規化されているものとする
		# Bezier4とLineSegmentオブジェクト
		self.parent_bezier = parent_bezier
		self.parent_line = parent_line
		self.current_bezier = parent_bezier
		self.current_line = parent_line
	
	def recursion_clipping(self, limit=1e-3):
		try:
			while self.current_line.length > limit:
				self.current_bezier, self.current_line = self.clipping()
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
			p = convex[i].cross_point(self.current_line)
			if not p is None:
				t.append(p)
				if not ax is None:
					ax.plot(p[0], p[1], 'o-', color="red")

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
			plt.grid()

		return b2, LineSegment(t[0], t[1])	



def main():
	print("Hello World")
	parent_bp = Bezier4((0, 2), (1.0/3.0, 6), (2.0/3.0, -4), (1, -3))
	parent_line = LineSegment((0, 0), (1, 0))

	# 描画
	ax = parent_bp.plot_bezier(color="darkblue")
	parent_bp.plot_control_point(ax)
	parent_line.plot_line(ax)


	bc = BezierClipping(parent_bp, parent_line)
	res = bc.recursion_clipping(limit=1e-3)
	print(res)
	if res:
		t = round(bc.current_line.v1[0], 3)
		point = parent_bp.beizer_point(t)

		ax.plot(point[0], point[1], 'o', color="red")
		plt.grid()
		plt.show()

if __name__ == "__main__":
	main()
