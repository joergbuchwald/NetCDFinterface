import numpy as np
import pandas as pd
import os
import netCDF4 as nc4

class NetCDFinterpolate(object):
    def __init__(self, filename, group="response_data", subgroup=None, unitsmap=None, spatialunit="m", timeunit="s"):
        self.fileobject = nc4.Dataset("filename")
        if subgroup is None:
            self.data = self.fileobject.groups[group]
        else:
             self.data = self.fileobject.groups[group].groups[subgroup]
        self.points = self.data.variables["geometry"][:][0]

    def get_neighbors(self, points_interpol, data_type="point"):
        """
        Method for obtaining neighbor points for interpolation.
        """
        points = self.points if data_type == "point" else self.cell_center_points
        df = pd.DataFrame(points)
        neighbors = {}
        if self.dim == 1:
            return neighbors
        for i, (_, val) in enumerate(points_interpol.items()):
            if self.dim == 2:
                x, y = self.plane
                df["r_"+str(i)] = (df[x]-val[x]) * (df[x]-val[x]) + (df[y]-val[y]) * (df[y]-val[y])
            elif self.dim == 3:
                df["r_"+str(i)] = ((df[0]-val[0]) * (df[0]-val[0]) + (df[1]-val[1]) * (df[1]-val[1])
                        + (df[2]-val[2]) * (df[2]-val[2]))
            neighbors[i] = df.sort_values(by=["r_" + str(i)]).head(self.nneighbors).index
        return neighbors

    def get_nearest_points(self, points_interpol):
        """
        Return a dictionary with closest mesh points
        Parameters
        ----------
        points_interpol : `dict`
        """
        nb = self.get_neighbors(points_interpol)
        nearest = {}
        for i, (key, _) in enumerate(points_interpol.items()):
            nearest[key] = self.points[nb[i][0]]
        return nearest

    def get_nearest_indices(self, points_interpol):
        """
        Return a dictionary with closest mesh point indices
        Parameters
        ----------
        points_interpol : `dict`
        """
        nb = self.get_neighbors(points_interpol)
        nearest = {}
        for i, (key, _) in enumerate(points_interpol.items()):
            nearest[key] = nb[i][0]
        return nearest

    def get_data_scipy(self, neighbors, points_interpol, fieldname, data_type="point", interpolation_method="linear"):
        """
        Get interpolated data for points_interpol using neighbor points.
        """
        field = self.get_point_field(fieldname) if data_type == "point" else self.get_cell_field(fieldname)
        points = self.points if data_type == "point" else self.cell_center_points
        resp = {}
        for i, (key, val) in enumerate(points_interpol.items()):
            if self.dim == 1:
                data = pd.DataFrame(points, columns = ['x'])
                data["y"] = field
                data.sort_values(by = ['x'], inplace=True)
                data.drop_duplicates(subset=['x'], inplace=True)
                f = interp1d(data['x'], data['y'])
                resp[key] = f(val[self.one_d_axis])
            elif self.dim == 2:
                x, y = self.plane
                grid_x, grid_y = np.array([[[val[x]]],[[val[y]]]])
                resp[key] = griddata(points[neighbors[i]], field[neighbors[i]],
                        (grid_x, grid_y), method=interpolation_method)[0][0]
            else:
                grid_x, grid_y, grid_z = np.array([[[[val[0]]]], [[[val[1]]]], [[[val[2]]]]])
                resp[key] = griddata(points[neighbors[i]], field[neighbors[i]],
                        (grid_x, grid_y, grid_z), method=interpolation_method)[0][0][0]
        return resp

    def get_point_field(self, fieldname):
        """
        Return vtu cell field as numpy array.
        Parameters
        ----------
        fieldname : `str`
        """
        field = self.data.variables[fieldname][:]
        return field

    def get_point_field_names(self):
        """
        Get names of all point fields in the vtu file.
        """
        fieldnames = [fieldname for fieldname in self.data.variables]
        return fieldnames

    def get_set_data(self, fieldname, pointsetarray=None, data_type="point", interpolation_method="linear"):
        """
        Get data specified in fieldname at all points specified in "pointsetarray".
        Parameters
        ----------
        fieldname : `str`
        pointsetarray : `list`, optional
                        default: [(0,0,0)]
        interpolation_method : `str`, optional
                               default: 'linear'
        """
        if pointsetarray is None:
            pointsetarray = [(0,0,0)]
        pts = {}
        # convert into point dictionary
        for i, entry in enumerate(pointsetarray):
            pts['pt'+str(i)] = entry
        resp = self.get_data(fieldname, pts=pts, data_type=data_type, interpolation_method=interpolation_method)
        resp_list = []
        # convert point dictionary into list
        for i, entry in enumerate(pointsetarray):
            resp_list.append(resp['pt' + str(i)])
        resp_array = np.array(resp_list)
        return resp_array
