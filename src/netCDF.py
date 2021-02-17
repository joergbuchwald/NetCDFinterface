import numpy as np
import os
import netCDF4 as nc4

class netCDF(object):
    def __init__(self, project_name='./', initunits={}, responseunits={}, accuracy=1.e-6):
        self.project_name = project_name
        self.accuracy = accuracy
        if len(initunits) == 0:
            self.initunits = {'E': 'Pa',
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
                    'dummy': '1'}
        else:
            self.initunits = initunits
        if len(responseunits) == 0:
            self.responseunits = {'temp': 'K',
                    'press': 'Pa',
                    'ux': 'm',
                    'uy': 'm',
                    'sigmaxx': 'Pa',
                    'sigmayy': 'Pa'}
        else:
            self.responseunits = responseunits

    def checkParam(self, initparam):
        for param in initparam:
            try:
                self.initunits[param]
            except KeyError:
                self.initunits[param] = " "
    def saveData(self, filename, initparam, outdata, x=0.0, y=0.0, z=0.0, numobspts=1):
        datafile = nc4.Dataset(os.path.join(self.project_name, filename),'w',format='NETCDF4')
        gr_param = datafile.createGroup('input_param')
        gr_resp = datafile.createGroup('response_data')
        _ = gr_param.createDimension('nchars', 20)
        _ = gr_param.createDimension('nstrings',None)
        parameters = gr_param.createVariable('params', 'S1', ('nstrings','nchars'))
        paramvalues = gr_param.createVariable('values', np.float32,('nstrings'))
        paramunits = gr_param.createVariable('units','S1',('nstrings','nchars'))
        paramdata = np.array([param for param in initparam], dtype='S20')
        parameters[:] = nc4.stringtochar(paramdata)
        parameters._Encoding = 'ascii'
        paramvaluedata = [initparam[param] for param in initparam]
        paramvalues[:] = paramvaluedata
        self.checkParam(initparam)
        paramunitsdata = np.array([self.initunits[param] for param in initparam], dtype='S20')
        paramunits[:] = nc4.stringtochar(paramunitsdata)
        paramunits._Encoding = 'ascii'
        _ = gr_resp.createDimension('pos', numobspts)
        try:
            time_length = len(outdata['time'])
        except KeyError:
            print('The key time is not in the response variable dictionary.')
        _ = gr_resp.createDimension('t',time_length)
        ix = gr_resp.createVariable('x', np.float32, ('pos',))
        ix.units = 'm'
        iy = gr_resp.createVariable('y', np.float32, ('pos',))
        iy.units = 'm'
        iz = gr_resp.createVariable('z', np.float32, ('pos',))
        iz.units = 'm'
        t = gr_resp.createVariable('time', np.float32, ('t',))
        t.units = 's'
        t[:] = outdata['time']
        for param in outdata:
            if not param=='time': 
                var = gr_resp.createVariable(param, np.float64, ('t','pos'))
                var[:,0] = outdata[param]
                var.units = self.responseunits[param]
        ix[0] = x
        iy[0] = y
        iz[0] = z
        for i in np.arange(1,numobspts):
            ix[i] = np.nan
            iy[i] = np.nan
            iz[i] = np.nan
        datafile.close()
    def appendData(self, filename, initparam, outdata, x=0.0, y=0.0, z=0.0):
        datafile = nc4.Dataset(os.path.join(self.project_name, filename),'r+',format='NETCDF4')
        try:
            grp_param = datafile.groups['input_param']
            grp_resp = datafile.groups['response_data']
        except KeyError:
            print("this is not a valid appendable file, please use saveData() instead")
        for i, param in enumerate(grp_param.variables['params'][:]):
            if ((np.asscalar(grp_param.variables['values'][i]) 
                    - initparam[param])/initparam[param]) > self.accuracy:
                print("WARNING: Parameters don't coincide with saved parameter set.")
                print(np.asscalar(grp_param.variables['values'][i]),initparam[param])
        ix = []
        iy = []
        iz = []
        q = grp_resp.variables['x'][:]
        index = 0
        for i, entry in enumerate(grp_resp.variables['x'][:]):
            if np.isnan(entry) == True and index == 0:
                ix.append(x)
                iy.append(y)
                iz.append(z)
                index = i
            else:
                ix.append(np.asscalar(grp_resp.variables['x'][i]))
                iy.append(np.asscalar(grp_resp.variables['y'][i]))
                iz.append(np.asscalar(grp_resp.variables['z'][i]))
        grp_resp.variables['x'][:] = ix
        grp_resp.variables['y'][:] = iy
        grp_resp.variables['z'][:] = iz
        for param in outdata:
            if not param == "time":
                grp_resp.variables[param][:, index] = outdata[param]
        datafile.close()
    def readColumn(self,filename,responsevars,x=0.0,y=0.0,z=0.0):
        response_column={}
        datafile = nc4.Dataset(os.path.join(self.project_name, filename))
        grp_resp = datafile.groups['response_data']
        for i, vx in enumerate(grp_resp.variables['x'][:]):
            vy = grp_resp.variables['y'][:][i]
            vz = grp_resp.variables['z'][:][i]
            if ((x - vx)**2 + (y - vy)**2 + (z - vz)**2) < self.accuracy:
                for var in responsevars:
                    if var == "time":
                        response_column[var] = grp_resp.variables[var][:]
                    else:
#                        print(var,i)
#                        print(grp_resp.variables[var])
                        response_column[var] = grp_resp.variables[var][:,i]
        datafile.close()
        return response_column
    def readParam(self, filename):
        params={}
        datafile = nc4.Dataset(os.path.join(self.project_name, filename))
        grp_param = datafile.groups['input_param']
        for i, param in enumerate(grp_param.variables['params'][:]):
            params[param] = np.asscalar(grp_param.variables['values'][i])
        datafile.close()
        return params
