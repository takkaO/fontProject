from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from bezier_module import Bezier3, Bezier4, LineSegment


class BezierClipping:
	def __init__(self, bezier, line, ax=None):
		self.original_bezier = bezier
		self.original_line = line
		self.ax = ax

		# 変換処理
		self.converted_bezier = self.convert_bezier(self.original_bezier, self.original_line)
		self.converted_line = LineSegment((0,0), (1,0))

		self.last_clipped_bezier = None
		self._result = False
		self._has_failed = False

	@property
	def result(self):
		return self._result
	
	@property
	def has_failed(self):
		return self._has_failed

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
		
	def _flatten(self, data):
		if not isinstance(data, list) and not isinstance(data, tuple):
			return [data]
		return [element for item in data for element in (self._flatten(item) if hasattr(item, '__iter__') else [item])]

	def clipping(self, current_bezier = None, current_line = None, limit=1e-3, times=None):
		if current_bezier is None:
			current_bezier = self.converted_bezier
		if current_line is None:
			current_line = self.converted_line
		
		#ax = current_bezier.plot_bezier()
		#current_bezier.plot_control_point(ax)
		# 凸包の4線分を取得
		convex = current_bezier.getConvexLineSegment()

		t = []
		for i in range(len(convex)):
			p = convex[i].cross_point(current_line)
			if not p is None:
				t.append(p)
		
		if len(t) < 2:
			# TODO:1個だけの場合の処理を追加
			if len(t) == 1:
				print("!!! Exception !!!")
			#print("No cross point")
			self._has_failed = True
			return self._flatten(current_line.midpoint[0])
		if len(t) > 2:
			t = [min(t), max(t)]

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

		if np.abs(current_line.length - next_line.length) < 1e-6:
			# 交点が複数存在する
			rate = next_line.calc_rate(next_line.midpoint)
			p = self.converted_bezier.beizer_point(next_line.midpoint[0])
			nb1, nb2 = next_bezier.split_bezier(rate, p)
			return self.clipping(nb1, next_line, limit=limit, times=times), self.clipping(nb2, next_line, limit=limit, times=times)

		self.last_clipped_bezier = next_bezier

		if next_line.length <= limit:
			self._result = True
			return self._flatten(next_line.midpoint[0])
		if not times is None:
			if times == 0:
				self._result = True
				return self._flatten(next_line.midpoint[0])
			else:
				times -= 1
		return self._flatten(self.clipping(next_bezier, next_line, limit=limit, times = times))

def main():
	print("Hello World")
	parent_bp = Bezier4((0, -1), (1.0/3.0, 3), (1.0/3.0, -4), (1.0, 3))
	#parent_bp = Bezier3((0, 2), (1.0/3.0, 4), (1.0, -3))

	parent_line = LineSegment((0, 0), (1, 0))

	
	ax = parent_bp.plot_bezier(color="darkblue")
	parent_bp.plot_control_point(ax, color="gray")
	parent_line.plot_line(ax)
	
	bc = BezierClipping(parent_bp, parent_line, ax)
	res = bc.clipping(limit=1e-3)
	print(res)

	bc.converted_bezier.plot_bezier(ax)
	for l in bc.converted_bezier.getConvexLineSegment():
		l.plot_line(ax)

	"""
	ts, r = zip(*res) 
	print(ts)
	print(r)

	
	
	bc.last_clipped_bezier.plot_bezier(ax)
	for l in bc.last_clipped_bezier.getConvexLineSegment():
		l.plot_line(ax)

	for t in ts:
		point = parent_bp.beizer_point(t)
		if parent_line.is_point_on_line(point):
			ax.plot(point[0], point[1], 'o', color="red")
		else:
			print("Out of Range")
	"""
	plt.grid()
	plt.show()

	
	

if __name__ == "__main__":
	main()
