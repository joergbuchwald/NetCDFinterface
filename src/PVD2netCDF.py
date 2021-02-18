import vtuIO
import NetCDFIO

def pvd2netcdf(folder, pvdfile, ncdffile, responsevar=[], pts={"pt0":(0.0,0.0,0.0)},dim=3):
    fin = vtuIO.PVDIO(folder, pvdfile, dim=dim)
    time = fin.timesteps
    resp = fin.readTimeSeries(responsevar, pts)
    fout = NetCDFIO.NETCDFIO(folder, ncdffile)
    fout.writeData(resp, time, pts=pts)
