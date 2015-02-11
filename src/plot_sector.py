
import numpy as np

# Enthought library imports
from traits.api import HasTraits

# Local imports
from utilities import hue_span


class SectorMixin(HasTraits):
    '''
    Pie chart, sectors, sections, arc length, quantity, circular sector,
    radii, disc, perimeter, curve

    values, variables,

    '''

    def draw_sectors(self, n_sectors):
        numpts = 30
        x = np.sort(np.random.random(numpts)) - 0.5
        y = np.random.random(numpts) - 0.5
        points = np.column_stack((x, y))
        sector_angles = self._calculate_sector_angles(n_sectors)
        sector_points_dist = self._sector_sort_points(points, sector_angles)
        sector_colors = self._make_sector_color_palette(sector_points_dist)
        self._add_plot_sectors(sector_angles, sector_colors)

    def _calculate_sector_angles(self, n_sectors):
        sect_angle = np.linspace(0, 2*np.pi, n_sectors+1)
        # return sect_angle[1:]
        # return sect_angle[:-1]
        return sect_angle

    def _sector_sort_points(self, points, sector_angles):
        pts_angle = np.arctan2(points[:, 0], points[:, 1])
        pts_angle[pts_angle < 0] += 2 * np.pi
        hist, _ = np.histogram(pts_angle, sector_angles)
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

        for i in range(nseg):
            xname = "sectorx{}".format(i)
            yname = "sectory{}".format(i)
            self.plot((xname, yname),
                      type='polygon',
                      face_color=sector_colors[i],
                      edge_color=(0, 0, 0),
                      alpha=0.3)
