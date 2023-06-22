import numpy as np
from shapely.geometry import Polygon
from .shape_utils import get_box_edges, sigma_shape


class Jet:
    '''
        Oject to hold the data associated with a single jet.
        Contains the start/end positions and associated extracts,
        and the box (as a `shapely.Polygon` object) and corresponding
        extracts
    '''

    def __init__(self, subject, start, end, box, cluster_values):
        self.subject = subject
        self.start = start
        self.end = end
        self.box = box

        self.cluster_values = cluster_values

        self.box_extracts = {'x': [], 'y': [], 'w': [], 'h': [], 'a': []}
        self.start_extracts = {'x': [], 'y': []}
        self.end_extracts = {'x': [], 'y': []}

        self.autorotate()

    def adding_new_attr(self, name_attr, value_attr):
        '''
            Add an additional attribute of value value_attr and name name_attr to the jet object
        '''
        setattr(self, name_attr, value_attr)

    def get_extract_starts(self):
        '''
            Get the extract coordinates associated with the
            starting base points

            Outputs
            -------
            coords : numpy.ndarray
                coordinates of the base points from the extracts
                for the start frame
        '''
        x_s = self.start_extracts['x']
        y_s = self.start_extracts['y']

        return np.transpose([x_s, y_s])

    def get_extract_ends(self):
        '''
            Get the extract coordinates associated with the
            final base points

            Outputs
            -------
            coords : numpy.ndarray
                coordinates of the base points from the extracts
                for the final frame
        '''
        x_e = self.end_extracts['x']
        y_e = self.end_extracts['y']

        return np.transpose([x_e, y_e])

    def get_extract_boxes(self):
        '''
            Get the extract shapely Polygons corresponding
            to the boxes

            Outputs
            -------
            boxes : list
                List of `shapely.Polygon` objects corresponding
                to individual boxes in the extracts
        '''
        boxes = []
        for i in range(len(self.box_extracts['x'])):
            x = self.box_extracts['x'][i]
            y = self.box_extracts['y'][i]
            w = self.box_extracts['w'][i]
            h = self.box_extracts['h'][i]
            a = np.radians(self.box_extracts['a'][i])

            # get the box
            boxes.append(Polygon(get_box_edges(x, y, w, h, a)[:4]))

        return boxes

    def plot(self, ax, plot_sigma=True):
        '''
            Plot the the data for this jet object. Plots the
            start and end clustered points, and the associated
            extracts. Also plots the clustered and extracted
            box. Also plots a vector from the base to the top of the box

            Input
            -----
            ax : `matplotlib.Axes()`
                axis object to plot onto. The general use case for this
                function is to plot onto an existing axis which already has
                the subjet image and potentially other jet plots

            Outputs
            -------
            ims : list
                list of `matplotlib.Artist` objects that was created for this plot
        '''
        boxplot, = ax.plot(*self.box.exterior.xy, 'b-',
                           linewidth=0.8, zorder=10)
        startplot, = ax.plot(*self.start, color='limegreen',
                             marker='x', markersize=2, zorder=10)
        endplot, = ax.plot(*self.end, 'rx', markersize=2, zorder=10)

        start_ext = self.get_extract_starts()
        end_ext = self.get_extract_ends()

        # plot the extracts (start, end, box)
        startextplot, = ax.plot(
            start_ext[:, 0], start_ext[:, 1], 'k.', markersize=1.)
        endextplot, = ax.plot(
            end_ext[:, 0], end_ext[:, 1], 'k.', markersize=1.)
        boxextplots = []
        for box in self.get_extract_boxes():
            iou = box.intersection(self.box).area / box.union(self.box).area
            boxextplots.append(
                ax.plot(*box.exterior.xy, 'k-', linewidth=0.5, alpha=0.65 * iou + 0.05)[0])

        # find the center of the box, so we can draw a vector through it
        center = np.mean(np.asarray(self.box.exterior.xy)[:, :4], axis=1)

        # create the rotation matrix to rotate a vector from solar north tos
        # the direction of the jet
        rotation = np.asarray([[np.cos(self.angle), -np.sin(self.angle)],
                               [np.sin(self.angle), np.cos(self.angle)]])

        # create a vector by choosing the top of the jet and base of the jet
        # as the two points
        point0 = center + np.matmul(rotation, np.asarray([0, self.height / 2.]))
        point1 = center + np.matmul(rotation, np.asarray([0, -self.height / 2.]))
        vec = point1 - point0

        base_points, height_points = self.get_width_height_pairs()

        arrowplot = ax.arrow(
            *point0, vec[0], vec[1], color='white', width=2, length_includes_head=True, head_width=10)

        if plot_sigma:
            if hasattr(self, 'sigma'):
                # calculate the bounding box for the cluster confidence
                plus_sigma, minus_sigma = sigma_shape(
                    self.cluster_values, self.sigma)

                # get the boxes edges
                plus_sigma_box = get_box_edges(*plus_sigma)
                minus_sigma_box = get_box_edges(*minus_sigma)

                # create a fill between the - and + sigma boxes
                x_p = plus_sigma_box[:, 0]
                y_p = plus_sigma_box[:, 1]
                x_m = minus_sigma_box[:, 0]
                y_m = minus_sigma_box[:, 1]
                ax.fill(
                    np.append(x_p, x_m[::-1]), np.append(y_p, y_m[::-1]), color='white', alpha=0.3)

        return [boxplot, startplot, endplot, startextplot, endextplot, *boxextplots, arrowplot]

    def autorotate(self):
        '''
            Find the rotation of the jet wrt to solar north and
            find the base width and height of the box
        '''
        box_points = np.transpose(self.box.exterior.xy)[:4, :]

        # find the distance between each point and the starting base
        dists = [np.linalg.norm((point - self.start)) for point in box_points]
        sorted_dists = np.argsort(dists)

        # the base points are the two points closest to the start
        base_points = np.array(
            [box_points[sorted_dists[0]], box_points[sorted_dists[1]]])

        # the height points are the next two
        rolled_points = np.delete(np.roll(box_points, -sorted_dists[0],
                                          axis=0), 0, axis=0)

        # we want to make sure that the order of the points
        # is in such a way that the point closest to the base
        # comes first -- this will ensure that the next point is
        # along the height line
        if np.linalg.norm(rolled_points[0, :] - base_points[1, :]) == 0:
            height_points = rolled_points[:2]
        else:
            height_points = rolled_points[::-1][:2]

        self.base_points = base_points
        self.height_points = height_points

        # also figure out the angle and additional size metadata
        # the angle is the angle between the height points and the base
        dh = self.height_points[1] - self.height_points[0]
        self.angle = np.arctan2(dh[0], -dh[1])

        self.height = np.linalg.norm(dh)
        self.width = np.linalg.norm(self.base_points[1] - self.base_points[0])

    def get_width_height_pairs(self):
        '''
            Outputs the base points and the height line segment
            points

            Outputs
            -------
            base_points : `numpy.ndarray`
                the pair of points that correspond to the base of the jet
            height_points : `numpy.ndarray`
                the pair of points that correspond to the height of the jet
        '''

        return self.base_points, self.height_points