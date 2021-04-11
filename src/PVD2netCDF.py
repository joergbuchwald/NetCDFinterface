import vtuIO
import NetCDFIO

def pvd2netcdf(folder, pvdfile, ncdffile, responsevar=None, pts=None, dim=3):
    if responsevar is None:
        responsevar = []
    if pts is None:
        pts = {"pt0":(0.0,0.0,0.0)}
    fin = vtuIO.PVDIO(folder, pvdfile, dim=dim)
    time = fin.timesteps
    resp = fin.readTimeSeries(responsevar, pts)
    fout = NetCDFIO.NETCDFIO(folder, ncdffile)
    fout.writeData(resp, time, pts=pts)
