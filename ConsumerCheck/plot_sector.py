
import numpy as np

# Enthought library imports
from traits.api import HasTraits, Bool, Int, List, Range, Str
from chaco.api import DataRange1D, LinearMapper, PolygonPlot
from chaco.plot_factory import _create_data_sources

# Local imports
from utilities import hue_span


class SectorMixin(HasTraits):
    '''
    Pie chart, sectors, sections, arc length, quantity, circular sector,
    radii, disc, perimeter, curve

    values, variables,

    '''
    sector_plot_names = List(Str)
    sector_points_dist = List(Int)
    draw_sect = Bool(False)
    n_sectors = Range(low=4, high=12)

    def switch_sectors(self, onoff):
        self.draw_sect = onoff
        if onoff:
            self.range2d.high_setting = (1.0, 1.0)
            self.range2d.low_setting = (-1.0, -1.0)
            self.draw_sectors(self.n_sectors)
        else:
            self.remove_sectors()

    def draw_sectors(self, n_sectors):
        if self.external_mapping:
            set_id = 2
        else:
            set_id = 1
        # Typical id: ('s1pc1', 's1pc2')
        # FIXME: self.data.x_no is set in _plotPC().
        # _plotPC() is called after this
        # x_id = 's{}pc{}'.format(set_id, self.data.x_no)
        # y_id = 's{}pc{}'.format(set_id, self.data.y_no)
        x_id = 's{}pc{}'.format(set_id, 1)
        y_id = 's{}pc{}'.format(set_id, 2)
        x = self.data.get_data(x_id)
        y = self.data.get_data(y_id)
        points = np.column_stack((x, y))
        sector_angles = self._calculate_sector_angles(n_sectors)
        sector_points_dist = self._sector_sort_points(points, sector_angles)
        sector_colors = self._make_sector_color_palette(sector_points_dist)
        self._add_plot_sectors(sector_angles, sector_colors)
        self.request_redraw()

    def remove_sectors(self):
        self.delplot(*self.sector_plot_names)
        self.legend.visible = False
        self.sector_plot_names = []
        self.request_redraw()

    def _calculate_sector_angles(self, n_sectors):
        sect_angle = np.linspace(0, 2*np.pi, n_sectors+1)
        # return sect_angle[1:]
        # return sect_angle[:-1]
        return sect_angle

    def _sector_sort_points(self, points, sector_angles):
        pts_angle = np.arctan2(points[:, 1], points[:, 0])
        pts_angle[pts_angle < 0] += 2 * np.pi
        hist, _ = np.histogram(pts_angle, sector_angles)
        self.sector_points_dist = list(hist)
        return hist

    def _make_sector_color_palette(self, sector_points_dist):
        u, i = np.unique(sector_points_dist, return_inverse=True)
        nu = len(u)
        csa = np.zeros(nu, np.object_)
        csa[:] = hue_span(nu-1)
        return csa[i]

    def _add_plot_sectors(self, sector_angles, sector_colors):
        nseg = len(sector_colors)
        radii = 2
        ptx = np.cos(sector_angles) * radii
        pty = np.sin(sector_angles) * radii
        pos = np.column_stack((ptx, pty))

        for i in range(nseg):
            # c1 = pos[i]
            # c2 = pos[i+1]
            # render = create_plot_sector((c1, c2), sector_colors[i])
            # self.add(render)
            ptx1 = pos[i, 0]
            pty1 = pos[i, 1]
            ptx2 = pos[i+1, 0]
            pty2 = pos[i+1, 1]
            px = np.array([0.0, ptx1, ptx2])
            py = np.array([0.0, pty1, pty2])
            xname = "sectorx{}".format(i)
            yname = "sectory{}".format(i)
            self.data.set_data(xname, px)
            self.data.set_data(yname, py)

        pnmap = dict()
        for i in range(nseg):
            xname = "sectorx{}".format(i)
            yname = "sectory{}".format(i)
            spn = "sect{}".format(i)
            self.sector_plot_names.append(spn)
            sp = self.plot((xname, yname),
                           type='polygon',
                           name=spn,
                           face_color=sector_colors[i],
                           edge_color=(0, 0, 0),
                           alpha=0.5)
            pnmap[str(self.sector_points_dist[i])] = sp
        order = sorted(pnmap.keys(), key=int, reverse=True)
        self.legend.plots = pnmap
        self.legend.labels = order
        self.legend.line_spacing = 20
        # self.legend.icon_spacing = 20
        self.legend.visible = True


def create_plot_sector(corners, face_color="green"):
    index_bounds = None
    value_bounds = None
    # orientation = "h"
    # edge_color = "black"
    # edge_width = 1.0
    # edge_style =
    # face_color = "green"
    # color = "green"
    # marker = "square"
    # marker_size = 4
    # bgcolor = "transparent"
    # outline_color = "black"
    border_visible = True
    # add_grid = False
    # add_axis = False
    # index_sort = "none"

    """
    Creates a ScatterPlot from a single Nx2 data array or a tuple of
    two length-N 1-D arrays.  The data must be sorted on the index if any
    reverse-mapping tools are to be used.

    Pre-existing "index" and "value" datasources can be passed in.
    """
    c1, c2 = corners
    sect = _create_sect_corners(c1, c2)
    index, value = _create_data_sources(sect)

    if index_bounds is not None:
        index_range = DataRange1D(low=index_bounds[0], high=index_bounds[1])
    else:
        index_range = DataRange1D()
    index_range.add(index)
    index_mapper = LinearMapper(range=index_range)

    if value_bounds is not None:
        value_range = DataRange1D(low=value_bounds[0], high=value_bounds[1])
    else:
        value_range = DataRange1D()
    value_range.add(value)
    value_mapper = LinearMapper(range=value_range)

    plot = PolygonPlot(index=index, value=value,
                       index_mapper=index_mapper,
                       value_mapper=value_mapper,
                       # orientation=orientation,
                       # marker=marker,
                       # marker_size=marker_size,
                       # color=color,
                       # bgcolor=bgcolor,
                       # outline_color=outline_color,
                       face_color=face_color,
                       border_visible=border_visible,)

    # if add_grid:
    #     add_default_grids(plot, orientation)
    # if add_axis:
    #     add_default_axes(plot, orientation)
    return plot


def _create_sect_corners(c1, c2):
    px = np.array([0.0, c1[0], c2[0]])
    py = np.array([0.0, c1[1], c1[1]])
    p = np.vstack((px, py))
    return p
