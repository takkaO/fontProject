from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

ERROR = 1e-6

class Point:
	def __init__(self, point):
	 self.x, self.y = point

class Bezier4:
	def __init__(self, sp, cp1, cp2, ep):
		self.v1 = np.array(sp)
		self.cp1 = np.array(cp1)
		self.cp2 = np.array(cp2)
		self.v2 = np.array(ep)
		self.code = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
	
	@property
	def verts(self):
		return [self.v1, self.cp1, self.cp2, self.v2]

	@property
	def codes(self):
		return self.code
	
	@property
	def points4matplot(self):
		xs, ys = zip(*self.verts)
		return xs, ys
	
	def scaling(self, scale):
		return Bezier4(self.v1*scale, self.cp1*scale, self.cp2*scale, self.v2*scale)
	
	def translation(self, dist):
		d = np.array(dist)
		return Bezier4(self.v1-d, self.cp1-d, self.cp2-d, self.v2-d)

	def rotate(self, rad):
		rv = np.array([[np.cos(rad), -np.sin(rad)],
					   [np.sin(rad),  np.cos(rad)]])

		p = []
		for c in self.verts:
			p.append(np.dot(rv, c))
		
		return Bezier4(p[0], p[1], p[2], p[3])
	
	def h_flip(self):
		v1 = self.v1
		cp1 = self.cp1
		cp2 = self.cp2
		v2 = self.v2

		v1[1] = -v1[1]
		cp1[1] = -cp1[1]
		cp2[1] = -cp2[1]
		v2[1] = -v2[1]

		return Bezier4(v1, cp1, cp2, v2)

	def getControlPointLineSegment(self):
		l1 = LineSegment(self.v1, self.cp1)
		l2 = LineSegment(self.cp1, self.cp2)
		l3 = LineSegment(self.cp2, self.v2)
		return l1, l2, l3

	def getConvexLineSegment(self):
		if np.sign(self.cp1[1]) == np.sign(self.cp2[1]):
			l1 = LineSegment(self.v1, self.cp1)
			l2 = LineSegment(self.cp1, self.cp2)
			l3 = LineSegment(self.cp2, self.v2)
			l4 = LineSegment(self.v2, self.v1)
		else:
			l1 = LineSegment(self.v1, self.cp1)
			l2 = LineSegment(self.cp1, self.v2)
			l3 = LineSegment(self.v2, self.cp2)
			l4 = LineSegment(self.cp2, self.v1)
		return l1, l2, l3, l4
	
	def beizer_point(self, t):
		f = []
		for value in self.verts:
			f.append(Point(value))

		# 3次ベジェ曲線を解析的に展開した式
		x = (-f[0].x + 3*f[1].x - 3*f[2].x + f[3].x) * t**3 + (3*f[0].x - 6 * f[1].x + 3 * f[2].x) * t**2 + (-3*f[0].x + 3 * f[1].x) * t + f[0].x
		y = (-f[0].y + 3*f[1].y - 3*f[2].y + f[3].y) * t**3 + (3*f[0].y - 6 * f[1].y + 3 * f[2].y) * t**2 + (-3*f[0].y + 3 * f[1].y) * t + f[0].y

		return (x, y)
	
	def split_bezier(self, rate, new_anchor_point):
		l1, l2, l3 = self.getControlPointLineSegment()
		
		sp1 = l1.split_point(rate)
		sp2 = l2.split_point(rate)
		sp3 = l3.split_point(rate)

		l4 = LineSegment(sp1, sp2)
		l5 = LineSegment(sp2, sp3)

		ssp1 = l4.split_point(rate)
		ssp2 = l5.split_point(rate)

		return Bezier4(self.v1, sp1, ssp1, new_anchor_point), Bezier4(new_anchor_point, ssp2, sp3, self.v2)
	
	def plot_bezier(self, ax=None, color="black"):
		if ax is None:
			_, ax = plt.subplots()
		path = Path(self.verts, self.codes)
		patch = patches.PathPatch(path, facecolor='none', lw=2, edgecolor=color)
		ax.add_patch(patch)
		ax.plot()
		return ax
	
	def plot_control_point(self, ax = None, color='black'):
		if ax is None:
			_, ax = plt.subplots()
		# 制御点の描画
		xs, ys = self.points4matplot
		ax.plot(xs, ys, 'x--', lw=2, color=color, ms=10)
		return ax


class LineSegment:
	def __init__(self, sp, ep):
		self.v1 = np.array(sp)
		self.v2 = np.array(ep)
		self.code = [Path.MOVETO, Path.LINETO]
	
	@property
	def verts(self):
		return [self.v1, self.v2]
	
	@property
	def codes(self):
		return self.code
	
	@property
	def points4matplot(self):
		xs, ys = zip(*self.verts)
		return xs, ys
	
	@property
	def length(self):
		return np.linalg.norm(np.array(self.v1) - np.array(self.v2))

	@property
	def equation_coefficient(self):
		a = self.v2[1] - self.v1[1]
		b = self.v2[0] - self.v1[0]
		c = self.v2[0] * self.v1[1] - self.v1[0] * self.v2[1]
		return a, b, c

	def cross_point(self, ls, error=ERROR):
		a, b = self.v1
		c, d = self.v2
		v1, v2 = ls.verts
		e, f = v1
		g, h = v2

		Xp = ((f*g-e*h) * (c - a) - (b*c-a*d) * (g - e)) / ((d-b)*(g-e)-(c-a)*(h-f) + error)
		Yp = ((f*g-e*h) * (d - b) - (b*c-a*d) * (h - f)) / ((d-b)*(g-e)-(c-a)*(h-f) + error)

		res = self.is_point_on_line((Xp, Yp))
		if res:
			return Xp, Yp
		else:
			return None

	def is_point_on_line(self, point, error=ERROR):
		p1 = np.array(self.v1)
		p2 = np.array(self.v2)
		p3 = np.array(point)
		
		# 三角不等式
		ac = np.linalg.norm(p1 - p3)
		bc = np.linalg.norm(p3 - p2)
		ab = np.linalg.norm(p1 - p2)
		print(ac+bc, ab+ERROR)

		return ac + bc < ab + error
	
	def split_point(self, rate):
		x1, y1 = self.v1
		x2, y2 = self.v2

		x = ((1-rate)*x1 + rate*x2)
		y = ((1-rate)*y1 + rate*y2)

		return (x, y)

	def calc_rate(self, point):
		if not self.is_point_on_line(point):
			return None
		x = np.linalg.norm(np.array(self.v1) - np.array(self.v2))
		m = np.linalg.norm(np.array(self.v1) - np.array(point))

		return m/x
	
	def plot_line(self, ax = None, linestyle="o-", color=None):
		if ax is None:
			_, ax = plt.subplots()
		xs, ys = self.points4matplot
		ax.plot(xs, ys, linestyle, color=color)
		return ax
	
	def translation(self, point):
		p = np.array(point)
		return LineSegment(self.v1-p, self.v2-p)
	
	def scaling(self, rate):
		pass

	def calc_rad(self, ls):
		if not self.is_point_on_line(ls.v1):
			print("Need to cross!")
			exit()
		# 基準はこのインスタンスの直線
		base = np.array(self.v2)
		target = np.array(ls.v2)

		a = np.dot(base, target)
		cos = a / (self.length * ls.length)
		theta = np.arccos(cos)
		if np.sign(ls.v2[1]) < 0:
			theta *= -1

		return theta
	
	def rotate(self, rad):
		rv = np.array([[np.cos(rad), -np.sin(rad)],
                	   [np.sin(rad),  np.cos(rad)]])

		p = []
		for c in self.verts:
			p.append(np.dot(rv, c))
		
		return LineSegment(p[0], p[1])

