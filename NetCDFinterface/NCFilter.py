import NetCDFInterpolate
import NetCDFIO

def netcdffilter(inputfile, outputfile, responsevar=None, pts=None, dim=3):
    if responsevar is None:
        responsevar = []
    if pts is None:
        pts = {"pt0":(0.0,0.0,0.0)}
    fin = NetCDFInterpolate.NetCDFInterpolate(inputfile, dim=dim)
    time = fin.times
    resp = fin.read_time_series(responsevar, pts)
    fout = NetCDFIO.NetCDFIO(outputfile)
    fout.write_data(resp, time, pts=pts)
