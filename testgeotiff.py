import os
import pyart

# open radar data
filename = os.getcwd() + '/Data/data (5).gz'
# radar = pyart.io.read_nexrad_archive(filename, station='KTLX')

radar = pyart.io.read_nexrad_archive(filename)
gatefilter = pyart.filters.GateFilter(radar)
gatefilter.exclude_below('reflectivity', 0)
gatefilter.exclude_transition()
print('Gridding started.')
grid = pyart.map.grid_from_radars(
    radar,
    gatefilters=(gatefilter,),
    grid_shape=(1, 2500, 2500),
    grid_limits=(
        (2000, 2000,),
        (-123000.0, 123000.0),
        (-123000.0, 123000.0),
    ),
    constant_roi=350,
    # roi_func='dist',
    weighting_function='nearest',
)
print('Gridding completed.')
pyart.io.write_grid_geotiff(
    grid,
    'geotest',
    'reflectivity',
    rgb=True,
    warp=True,
    cmap='pyart_NWSRef',
)
print('Finished.')
