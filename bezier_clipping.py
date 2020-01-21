from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from bezier_module import Bezier4, LineSegment

def beizer_clipping(self, bezier, base_line):
	pass

def main():
	print("Hello World")
	parent_bp = Bezier4((0, 2), (1.0/3.0, 6), (2.0/3.0, 4), (1, -3))
	path = Path(parent_bp.verts, parent_bp.codes)

	_, ax = plt.subplots()
	patch = patches.PathPatch(path, facecolor='none', lw=2, edgecolor="darkblue")
	ax.add_patch(patch)

	# ベースラインの描画(t軸)
	parent_line = LineSegment((0,0), (1, 3))
	xs, ys = parent_line.points4matplot 
	ax.plot(xs, ys, 'o-')
	
	# 制御点の描画
	xs, ys = parent_bp.points4matplot
	ax.plot(xs, ys, 'x--', lw=2, color='black', ms=10)
	
	# 凸包の4線分を取得
	convex = parent_bp.getConvexLineSegment()
	for line in convex:
		xs, ys = line.points4matplot
		ax.plot(xs, ys, "--", color="gray")

	t = []
	for i in range(len(convex)):
		p = convex[i].cross_point(parent_line)
		if not p is None:
			t.append(p)
			xs, ys = p
			ax.plot(xs, ys, 'o-', color="red")

	# tmin, tmax
	t = sorted(t)
	print("t:", t)

	p = []
	for i in range(len(t)):
		# ベジェ曲線上のポイントを取得
		z = parent_bp.beizer_point(t[i][0])
		p.append(z)
		ax.plot(z[0], z[1], 'o-', color="blue")
		ax.plot([t[i][0], z[0]], [t[i][1], z[1]], ":", color="green")

	_, b1 = parent_bp.split_bezier(t[0][0], p[0])

	nl = LineSegment(t[0], parent_line.v2)

	
	b2, _ = b1.split_bezier(nl.calc_rate(t[1]), p[1])
	path = Path(b2.verts, b2.codes)
	patch = patches.PathPatch(path, facecolor='none', lw=2)
	ax.add_patch(patch)

	xs, ys = b2.points4matplot
	ax.plot(xs, ys, "o")
	

	"""
	pl = cross_point(verts[0], verts[2], [0, 0], [1, 0])
	ax.plot(pl[0], pl[1], 'o', color="blue")
	bp1 = bezier_point(verts, pl[0])
	ax.plot(bp1[0], bp1[1], 'o', color="red")
	print(pl, bp1)
	ax.plot([pl[0], bp1[0]], [pl[1], bp1[1]], ':')

	pr = cross_point(verts[1], verts[3], [0, 0], [1, 0])
	ax.plot(pr[0], pr[1], 'o', color="blue")
	bp2 = bezier_point(verts, pr[0])
	ax.plot(bp2[0], bp2[1], 'o', color="red")
	print(pr, bp2)
	ax.plot([pr[0], bp2[0]], [pr[1], bp2[1]], ':')
	"""
	# pl
	"""
	sp1 = split_point(verts[0], verts[1], pl[0])
	sp2 = split_point(verts[1], verts[2], pl[0])
	sp3 = split_point(verts[2], verts[3], pl[0])
	ax.plot(sp1[0], sp1[1], "o")
	ax.plot(sp2[0], sp2[1], "o")
	ax.plot(sp3[0], sp3[1], "o") #
	ax.plot([sp1[0], sp2[0]], [sp1[1], sp2[1]], '-')
	ax.plot([sp2[0], sp3[0]], [sp2[1], sp3[1]], '-')
	ssp1 = split_point(sp1, sp2, pl[0])
	ssp2 = split_point(sp2, sp3, pl[0]) #
	ax.plot(ssp1[0], ssp1[1], "o")
	ax.plot(ssp2[0], ssp2[1], "o")
	"""

	"""
	_, v1 = split_bezier(verts, pl[0], bp1)
	v2, _ = split_bezier(verts, pr[0], bp2)

	ax.plot(v1[1][0], v1[1][1], 'o')
	ax.plot(v2[2][0], v2[2][1], 'o')

	ax.plot([v1[1][0], bp1[0]], [v1[1][1], bp1[1]])
	
	#new_verts = [bp1, ssp2, sp3, verts[3]]
	path = Path(v2, codes)
	patch = patches.PathPatch(path, facecolor='none', lw=2)
	ax.add_patch(patch)
	"""

	ax.grid()

	plt.show()

if __name__ == "__main__":
	main()
