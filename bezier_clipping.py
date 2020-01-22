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
	
	def recursion_clipping(self, limit=1e-3, debug=False):
		try:
			while self.current_line.length > limit:
				ax = None
				if debug:
					_, ax = plt.subplots()
					self.parent_line.plot_line(ax)
					self.parent_bezier.plot_bezier(ax, color="darkblue")
				self.current_bezier, self.current_line = self.clipping(ax)
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


class MyAfine:
	def __init__(self, bezier, line_segment):
		self.line_segment = line_segment
		self.bezier = bezier

	def	normalize_bezier(self, bezier, ax):
		scale = 1.0 / (bezier.v2[0] - bezier.v1[0])
		#scale = 1.0
		mb = bezier.scaling(scale)
		# x軸だけで良い

		#ax.plot([mb.v1[0], 1.0], [mb.v1[1], mb.v1[1]], '-')
		tv = mb.v1[0]
		bezier_normalize = mb.translation((tv, 0))
		#bezier_normalize = bezier_normalize.h_flip()
		return bezier_normalize, scale
	
	def denormalize_bezier(self, bezier, descale):
		sb = bezier.scaling(1.0 / descale)
		bezier_denormalize = sb.translation((-bezier.v1[0], 0))
		return bezier_denormalize

	def normalize_line(self, ls):
		pass	

	def get_rotate_angle(self):
		# ベースラインはこの直線とする
		base = LineSegment((0, 0), (1, 0))
		# 基準をそろえる
		target = self.line_segment.translation(self.line_segment.v1)

		theta = base.calc_rad(target)
		#print(theta)
		#print(np.rad2deg(theta))
		return theta

	def rotate(self):
		rad = self.get_rotate_angle()

		nb = self.bezier.rotate(-rad)
		nl = self.line_segment.rotate(-rad)
		return nb, nl


def test_detection_point():
	#parent_bp = Bezier4((0, 2), (1.0/3.0, 6), (2.0/3.0, 4), (1, -3))
	parent_bp = Bezier4((0, 2), (0/3.0, 6), (2.0/3.0, 4), (1, -3))
	parent_line = LineSegment((0, 0), (1, 0))

	ax = parent_bp.plot_bezier(color="darkblue")
	parent_bp.plot_control_point(ax, color="gray")
	parent_line.plot_line(ax)

	# 描画
	ax = parent_bp.plot_bezier(color="darkblue")
	parent_bp.plot_control_point(ax)
	parent_line.plot_line(ax)

	bc = BezierClipping(parent_bp, parent_line)
	res = bc.recursion_clipping(limit=1e-3, debug=True)
	print(res)
	if res:
		t = round(bc.current_line.v1[0], 3)
		point = parent_bp.beizer_point(t)
		print(point)

		ax.plot(point[0], point[1], 'o', color="red")
	plt.grid()
	plt.show()


def main():
	print("Hello World")
	test_detection_point()

	return
	parent_bp = Bezier4((0.2, 2), (1.0/3.0, 6), (2.0/3.0, -4), (1.2, -3))
	parent_line = LineSegment((0, 0), (1, 1))

	
	
	ax = parent_bp.plot_bezier(color="darkblue")
	parent_bp.plot_control_point(ax, color="gray")
	parent_line.plot_line(ax)

	

	#_, ax = plt.subplots()
	af = MyAfine(parent_bp, parent_line)
	b, l = af.rotate()
	b.plot_bezier(ax)
	b.plot_control_point(ax)
	l.plot_line(ax)
	nb, scale = af.normalize_bezier(b, ax)
	
	nb.plot_bezier(ax)
	nb.plot_control_point(ax)

	p = nb.beizer_point(0)
	ax.plot(p[0], p[1], 'o', color="red")

	p = nb.beizer_point(0.1)
	ax.plot(p[0], p[1], 'o', color="red")

	p = nb.beizer_point(0.5)
	ax.plot(p[0], p[1], 'o', color="red")
	
	p = nb.beizer_point(0.9)
	ax.plot(p[0], p[1], 'o', color="red")

	p = nb.beizer_point(1)
	ax.plot(p[0], p[1], 'o', color="red")

	ax.set_aspect('equal')

	#bc = BezierClipping(nb, LineSegment((0,0), (1,0)))
	#bc.recursion_clipping(debug=True)

	plt.grid()
	plt.show()

	

if __name__ == "__main__":
	main()
