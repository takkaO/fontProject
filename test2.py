from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont
import matplotlib.patches as mpatches
import matplotlib.path as mpath
import time
from datetime import datetime as dt

import numpy as np

import matplotlib.pyplot as plt
#plt.rcParams['font.family'] = 'IPAGothic'


font = TTFont(r"C:\Users\csel-pc05\Desktop\FontProject\IPAfont00303\ipamp.ttf")
glyph_set = font.getGlyphSet()
cmap = font.getBestCmap()


def get_glyph(glyph_set, cmap, char):
    glyph_name = cmap[ord(char)]
    return glyph_set[glyph_name]


iroha_1 = get_glyph(glyph_set, cmap, u'て')


recording_pen = RecordingPen()

iroha_1.draw(recording_pen)
print(recording_pen.value)

pathdt = recording_pen.value  # path(bezier curve)


def pdTopd(pd, mtrx1=[[1, 0], [0, 1]]):
    tmp1 = [[]]
    tmp2 = [[]]
    i2 = 0
    for i in range(len(pd)):
        if pd[i][0] == 'closePath':
            tmp1.append([])
            tmp2.append([])
            i2 += 1

        if pd[i][0] == 'moveTo':
            tmp1[i2].append(mpath.Path.MOVETO)
            tmp2[i2].append(np.dot(mtrx1, pd[i][1][0]))

        elif pd[i][0] == 'qCurveTo':
            tmp1[i2].append(mpath.Path.CURVE3)
            tmp2[i2].append(np.dot(mtrx1, pd[i][1][0]))
            tmp1[i2].append(mpath.Path.CURVE3)
            tmp2[i2].append(np.dot(mtrx1, pd[i][1][1]))
            if pd[i+1][0] == 'qCurveTo':
                tmp1[i2].append(mpath.Path.LINETO)
                tmp2[i2].append(np.dot(mtrx1, pd[i][1][1]))

        elif pd[i][0] == 'lineTo':
            tmp1[i2].append(mpath.Path.LINETO)
            tmp2[i2].append(np.dot(mtrx1, pd[i][1][0]))

        elif pd[i][0] == 'curveTo':
            tmp1[i2].append(mpath.Path.CURVE4)
            tmp2[i2].append(np.dot(mtrx1, pd[i][1][0]))
            tmp1[i2].append(mpath.Path.CURVE4)
            tmp2[i2].append(np.dot(mtrx1, pd[i][1][1]))
            tmp1[i2].append(mpath.Path.CURVE4)
            tmp2[i2].append(np.dot(mtrx1, pd[i][1][2]))
            if pd[i+1][0] == 'qCurveTo':
                tmp1[i2].append(mpath.Path.LINETO)
                tmp2[i2].append(np.dot(mtrx1, pd[i][1][0]))
        print("%s/%s" % (i, len(pd)))

    return tmp1, tmp2


a2, b2 = pdTopd(pathdt)  # x,y(bezier)
a, b = pdTopd(pathdt, mtrx1=[[1, 2], [0, 1]])  # (x,y(translated bezier))

f, (ax1) = plt.subplots(1, 1)

for i in range(len(a)-1):
    c = mpath.Path(b[i], a[i])
    d = mpatches.PathPatch(c, facecolor='white',
                           edgecolor="gray", lw=2, clip_on=False)
    ax1.add_patch(d)
    c = mpath.Path(b2[i], a2[i])
    d = mpatches.PathPatch(c, facecolor='white', lw=2, clip_on=False)
    ax1.add_patch(d)

ax1.set_aspect('equal')
ax1.grid(which="major", color="k", linestyle="--")
ax1.hlines(0, -3000, 3000)
ax1.vlines(0, -3000, 3000)
ax1.set_xlim(-2000, 2000)
ax1.set_ylim(-2000, 2000)
ax1.set_title(u"Font", fontsize=30)
ax1.set_xlabel(u"横 [px]", fontsize=30)
ax1.set_ylabel(u"縦 [px]", fontsize=30)

tdatetime = dt.now()
itext = tdatetime.strftime('%Y%m%d' + time.ctime()
                           [11:13] + time.ctime()[14:16] + time.ctime()[17:19])
f.set_size_inches(19.2, 10.8)
f.savefig("%s.png" % (itext))
