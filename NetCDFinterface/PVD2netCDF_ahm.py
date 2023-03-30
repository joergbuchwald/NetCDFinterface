import vtuIO
import NetCDFIO

def pvd_to_netcdf(pvdfile, ncdffile, responsevar=None, pts=None, suppldata=None):
    respvarmapping = {'temperature': ['temp'], 'pressure': ['press']}
    def convert_response(response):
            response_converted = {}
            for pt in response:
                response_converted[pt] = {}
                for var in responsevar:
                    if len(respvarmapping[var]) == 1:
                        response_converted[pt][respvarmapping[var][0]] = response[pt][var]
                    else:
                        for i, newvar in enumerate(respvarmapping[var]):
                            response_converted[pt][newvar] = []
                            for timestep in response[pt][var]:
                                response_converted[pt][newvar].append(timestep[i])
            return response_converted
    if responsevar is None:
        responsevar = []
    if pts is None:
        pts = {"pt0":(0.0,0.0,0.0)}
    fin = vtuIO.PVDIO(pvdfile)
    fin.clear_pvd_path()
    time = fin.timesteps
    resp = fin.read_time_series(responsevar, pts)
    resp_converted = convert_response(resp)
    fout = NetCDFIO.NetCDFIO(ncdffile)
    fout.write_data(resp_converted, time, suppldata=suppldata, pts=pts)
