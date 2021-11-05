import vtuIO
import NetCDFIO

def pvd_to_netcdf(pvdfile, ncdffile, responsevar=None, pts=None, dim=3):
    if responsevar is None:
        responsevar = []
    if pts is None:
        pts = {"pt0":(0.0,0.0,0.0)}
    fin = vtuIO.PVDIO(pvdfile, dim=dim)
    time = fin.timesteps
    resp = fin.read_time_series(responsevar, pts)
    fout = NetCDFIO.NetCDFIO(ncdffile)
    fout.write_data(resp, time, pts=pts)
