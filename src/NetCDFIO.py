import numpy as np
import os
import netCDF4 as nc4

class NETCDFIO(object):
    def __init__(self, folder, filename, unitsmap=None, spatialunit="m", timeunit="s"):
        self.folder = folder
        self.filename = filename
        if unitsmap is None:
            self.unitsmap = {'E': 'Pa',
                    'nu': '1',
                    'a_s': '$K^{-1}$',
                    'a_w': '$K^{-1}$',
                    'Q': 'W',
                    'n': '1',
                    'rho_w': '$kg m^{-3}$',
                    'rho_s': '$kg m^{-3}$',
                    'K_w': '$W m^{-1} K^{-1}$',
                    'K_s': '$W m^{-1} K^{-1}$',
                    'mu': 'Pa s',
                    'c_w': '$J kg^{-1} K^{-1}$',
                    'c_s': '$J kg^{-1} K^{-1}$',
                    'T0': 'K',
                    'k': '$m^2$',
                    'dummy': '1',
                    'temp': 'K',
                    'press': 'Pa',
                    'ux': 'm',
                    'uy': 'm',
                    'sigmaxx': 'Pa',
                    'sigmayy': 'Pa'}
        else:
            self.unitsmap = unitsmap
        self.spatialunit = spatialunit
        self.timeunit = timeunit
    def writeData(self, data = {'pt0': {'temperature': []}}, time = [], suppldata = {'E': 0.0},
                pts = {'pt0': (0.0,0.0,0.0)}):
        numofpts = len(pts)
        try:
            assert len(data) == len(pts)
        except AssertionError:
            print("assertion error:")
            print(len(data))
            print(len(pts))
            print(data)
            print(pts)
        for ptdict in data.values():
            for i, (param, paramarray) in enumerate(ptdict.items()):
                if i == 0:
                    try:
                        assert len(paramarray) == len(time)
                    except AssertionError:
                        print("assertion error:")
                        print(len(paramarray))
                        print(len(time))
                        print(paramarray)
                        print(time)
        with nc4.Dataset(os.path.join(self.folder, self.filename), 'w', format='NETCDF4') as f:
            # suppl data first
            gr_param = f.createGroup('input_param')
            _ = gr_param.createDimension('nchars', 20)
            _ = gr_param.createDimension('nstrings',None)
            parameters = gr_param.createVariable('params', 'S1', ('nstrings','nchars'))
            paramvalues = gr_param.createVariable('values', np.float32,('nstrings'))
            paramunits = gr_param.createVariable('units','S1',('nstrings','nchars'))
            paramdata = np.array([param for param in suppldata], dtype='S20')
            parameters[:] = nc4.stringtochar(paramdata)
            parameters._Encoding = 'ascii'
            paramvaluedata = [paramvalue for paramvalue in suppldata.values()]
            paramvalues[:] = paramvaluedata
            paramunitslist = []
            for param in suppldata:
                try:
                    paramunitslist.append(self.unitsmap[param])
                except KeyError:
                    paramunitslist.append("")
            paramunitsdata = np.array(paramunitslist, dtype='S20')
            paramunits[:] = nc4.stringtochar(paramunitsdata)
            paramunits._Encoding = 'ascii'
            # real data
            gr_resp = f.createGroup('response_data')
            _ = gr_resp.createDimension('pos', numofpts)
            try:
                time_length = len(time)
            except KeyError:
                print('The key time is not in the response variable dictionary.')
            _ = gr_resp.createDimension('t',time_length)
            ix = gr_resp.createVariable('x', np.float32, ('pos',))
            ix.units = self.spatialunit
            iy = gr_resp.createVariable('y', np.float32, ('pos',))
            iy.units = self.spatialunit
            iz = gr_resp.createVariable('z', np.float32, ('pos',))
            iz.units = self.spatialunit
            t = gr_resp.createVariable('time', np.float32, ('t',))
            t.units = self.timeunit
            t[:] = np.array(time)
            var = {}
            for i, (pt, ptdict) in enumerate(data.items()):
                ix[i] = pts[pt][0]
                iy[i] = pts[pt][1]
                iz[i] = pts[pt][2]
                for param, paramarray in ptdict.items():
                    if not param == "time":
                        if i == 0:
                            var[param] = gr_resp.createVariable(param, np.float64, ('t','pos'))
                            try:
                                var[param].units = self.unitsmap[param]
                            except:
                                var[param].units = ""
                        var[param][:,i] = paramarray

    def readData(self):
        with nc4.Dataset(os.path.join(self.folder, self.filename)) as f:
            grp_resp = f.groups['response_data']
            resp = {}
            pts = {}
            skipvar = ["x", "y", "z", "time"]
            t = grp_resp.variables['time'][:]
            for ptid, x in enumerate(grp_resp.variables['x'][:]):
                y = grp_resp.variables['y'][:][ptid]
                z = grp_resp.variables['z'][:][ptid]
                pts[f"pt{ptid}"] = (x, y, z)
                resp[f"pt{ptid}"] = {}
                for var in grp_resp.variables:
                    if not (var in skipvar):
                        resp[f"pt{ptid}"][var] = grp_resp.variables[var][:,ptid]
        return (resp, t, pts)
    def readParam(self):
        params = {}
        with nc4.Dataset(os.path.join(self.folder, self.filename)) as f:
            grp_param = f.groups['input_param']
            for i, param in enumerate(grp_param.variables['params'][:]):
                params[param] = np.asscalar(grp_param.variables['values'][i])
        return params
