import glob
from pathlib import Path

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pyart
from cartopy.feature import ShapelyFeature
from cartopy.io.shapereader import Reader
from matplotlib import animation

ROOT_PATH = Path(__file__).parent
files = sorted(glob.glob(f"{ROOT_PATH}/data/*"))
county_file = ROOT_PATH / "shapefiles/counties/countyl010g.shp"
roads_file = ROOT_PATH / "shapefiles/roads/ne_10m_roads.shp"

fig = plt.figure(figsize=(18, 10))
plt.subplots_adjust(0, 0, 1, 1)
# load and draw counties shapefile
county_feature = ShapelyFeature(
    Reader(county_file).geometries(),
    ccrs.PlateCarree(),
    facecolor="none",
    edgecolor="black",
    linewidth=1,
)
# load and draw roads shapefile
roads_feature = ShapelyFeature(
    Reader(roads_file).geometries(),
    ccrs.PlateCarree(),
    facecolor="none",
    edgecolor="blue",
    linewidth=1,
)


def animate(nframe):
    plt.clf()
    ax = plt.axes(projection=ccrs.PlateCarree())
    radar = pyart.io.read_nexrad_archive(files[nframe], station="KTLX")
    # filter data
    gate_filter = pyart.filters.GateFilter(radar)
    gate_filter.exclude_below("reflectivity", 0)
    # graph radar for animation
    display = pyart.graph.RadarMapDisplay(radar)
    display.plot_ppi_map(
        "reflectivity",
        sweep=0,
        vmin=-32,
        vmax=70,
        ax=ax,
        cmap="pyart_NWSRef",
        colorbar_flag=False,
        # lat_0=radar.latitude['data'][0],
        # lon_0=radar.longitude['data'][0],
        min_lon=radar.longitude["data"][0] - 1,
        max_lon=radar.longitude["data"][0] + 1,
        min_lat=radar.latitude["data"][0] - 1,
        max_lat=radar.latitude["data"][0] + 1,
        add_grid_lines=False,
        edges=False,
        embellish=False,
    )
    ax.add_feature(county_feature)
    ax.add_feature(roads_feature)


anim = animation.FuncAnimation(fig, animate, frames=len(files))

# anim.save('tdwr_animation.gif', fps=1)
plt.show()
# print('Done')
