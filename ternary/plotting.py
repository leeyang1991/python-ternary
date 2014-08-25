import math

import matplotlib
import matplotlib.pyplot as pyplot

"""Matplotlib Ternary plotting utility."""

## Constants ##

SQRT3OVER2 = math.sqrt(3) / 2.

## Default colormap, other options here: http://www.scipy.org/Cookbook/Matplotlib/Show_colormaps
DEFAULT_COLOR_MAP = pyplot.get_cmap('jet')
#DEFAULT_COLOR_MAP = pyplot.get_cmap('gist_stern')

## Helpers ##
def unzip(l):
    #return [x for (x,y) in l], [y for (x,y) in l]
    return zip(*l)

def normalize(xs):
    s = float(sum(xs))
    return [x / s for x in xs]

## Boundary ##

def draw_boundary(scale=1.0, linewidth=2.0, color='black', ax=None):
    # Plot boundary of 3-simplex.
    if not ax:
        ax = pyplot
    scale = float(scale)
    # Note that the math.sqrt term is such to prevent noticable roundoff on the top corner point.
    ax.plot([0, scale, scale / 2, 0], [0, 0, math.sqrt(scale * scale * 3.) / 2, 0], color, linewidth=linewidth)
    ax.ylim([-0.05 * scale, .90 * scale])
    ax.xlim([-0.05 * scale, 1.05 * scale])

## Curve Plotting ##
def project_point(p):
    """Maps (x,y,z) coordinates to planar-simplex."""
    a = p[0]
    b = p[1]
    c = p[2]
    x = 0.5 * (2 * b + c)
    y = SQRT3OVER2 * c
    return (x, y)

def project(s):
    """Maps (x,y,z) coordinates to planar-simplex."""
    # Is s an appropriate sequence or just a single point?
    try:
        return unzip(map(project_point, s))
    except TypeError:
        return project_point(s)
    except IndexError: # for numpy arrays
        return project_point(s)

def plot(t, color=None, linewidth=1.0):
    """Plots trajectory points where each point satisfies x + y + z = 1."""
    xs, ys = project(t)
    if color:
        pyplot.plot(xs, ys, c=color, linewidth=linewidth)
    else:
        pyplot.plot(xs, ys, linewidth=linewidth)

## Heatmaps##

def simplex_points(steps=100, boundary=True):
    """Systematically iterate through a lattice of points on the simplex."""
    steps = steps - 1
    start = 0
    if not boundary:
        start = 1
    for x1 in range(start, steps + (1-start)):
        for x2 in range(start, steps + (1-start) - x1):
            x3 = steps - x1 - x2
            yield (x1, x2, x3)

def colormapper(x, a=0, b=1, cmap=None):
    """Maps color values to [0,1] and obtains rgba from the given color map for triangle coloring."""
    if b - a == 0:
        rgba = cmap(0)
    else:
        rgba = cmap((x - a) / float(b - a))
    hex_ = matplotlib.colors.rgb2hex(rgba)
    return hex_

def triangle_coordinates(i, j, alt=False):
    """Returns the ordered coordinates of the triangle vertices for i + j + k = N. Alt refers to the averaged triangles; the ordinary triangles are those with base parallel to the axis on the lower end (rather than the upper end)"""
    # N = i + j + k
    if not alt:
        return [(i/2. + j, i * SQRT3OVER2), (i/2. + j + 1, i * SQRT3OVER2), (i/2. + j + 0.5, (i + 1) * SQRT3OVER2)]
    else:
        # Alt refers to the inner triangles not covered by the default case
        return [(i/2. + j + 1, i * SQRT3OVER2), (i/2. + j + 1.5, (i + 1) * SQRT3OVER2), (i/2. + j + 0.5, (i + 1) * SQRT3OVER2)]

def heatmap(d, steps, cmap_name=None, boundary=True, ax=None, scientific=False):
    """Plots counts in the dictionary d as a heatmap. d is a dictionary of (i,j) --> c pairs where N = i + j + k."""
    if not ax:
        ax = pyplot.subplot()
    if not cmap_name:
        cmap = DEFAULT_COLOR_MAP
    else:
        cmap = pyplot.get_cmap(cmap_name)
    a = min(d.values())
    b = max(d.values())
    # Color data triangles.
    for k, v in d.items():
        i, j = k
        vertices = triangle_coordinates(i,j)
        x,y = unzip(vertices)
        color = colormapper(d[i,j],a,b,cmap=cmap)
        ax.fill(x, y, facecolor=color, edgecolor=color)
    # Color smoothing triangles.
    offset = 0
    if not boundary:
        offset = 1
    for i in range(offset, steps+1-offset):
        for j in range(offset, steps -i -offset):
            try:
                alt_color = (d[i,j] + d[i, j + 1] + d[i + 1, j])/3.
                color = colormapper(alt_color, a, b, cmap=cmap)
                vertices = triangle_coordinates(i,j, alt=True)
                x,y = unzip(vertices)
                pyplot.fill(x, y, facecolor=color, edgecolor=color)
            except KeyError:
                # Allow for some portions to have no color, such as the boundary
                pass
    # Colorbar hack
    sm = pyplot.cm.ScalarMappable(cmap=cmap, norm=pyplot.Normalize(vmin=a, vmax=b))
    # fake up the array of the scalar mappable. Urgh...
    sm._A = []
    cb = pyplot.colorbar(sm, ax=ax, format='%.3f')
    if scientific:
        cb.formatter = matplotlib.ticker.ScalarFormatter()
        cb.formatter.set_powerlimits((0, 0))
        cb.update_ticks()

## Convenience Functions ##
    
def plot_heatmap(func, steps=40, boundary=True, cmap_name=None):
    """Computes func on heatmap coordinates and plots heatmap."""
    d = dict()
    for x1, x2, x3 in simplex_points(steps=steps, boundary=boundary):
        d[(x1, x2)] = func(normalize([x1, x2, x3]))
    heatmap(d, steps, cmap_name=cmap_name)
    
def plot_multiple(trajectories, linewidth=2.0):
    """Plots multiple trajectories and the boundary."""
    for t in trajectories:
        plot(t, linewidth=linewidth)
    draw_boundary()
