import os
from PIL import Image

import matplotlib.pyplot as plt
import numpy as np

import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord

from astroplan import Observer
from astroplan import FixedTarget
from astroplan.plots import plot_sky


def plot_stars(df, bin_stars, star_map, altaz_coords, obs_time, az_bin, alt_bin):
    """plot the selected stars"""

    img_dir = "tel_analysis_gif"
    os.makedirs(img_dir, exist_ok=True)
    salt = Observer.at_site("SALT")

    targets = [FixedTarget(coord=SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg))) for ra, dec in zip(df.ra, df.dec)]

    plt.figure(figsize=(6, 6))
    selected_star = bin_stars.nlargest(1, "ra").iloc[0]
    coords_for_plot = SkyCoord(ra=selected_star['ra']*u.deg, dec=selected_star['dec']*u.deg, frame='icrs')
    plot_sky(coords_for_plot, salt, obs_time, style_kwargs={'marker': 'o', 'color': 'C0'}) # selected star
    # plot_sky(targets, salt, obs_time, style_kwargs={'marker': '.', 'alpha': 0.3, 'color': 'gray'}) # all stars

    low, upper = 22, 88
    theta = np.arange(0, 360)
    low_limit = [90-low] * len(theta)
    upper_limit = [90-upper] * len(theta)
    plt.plot(theta, low_limit, '.', color='C1', markersize=4, label=f'limit : {low}°, {upper}°')
    plt.plot(theta, upper_limit, '.', color='C1', markersize=2)

    plt.title(f"UTC {obs_time}", fontsize=14)
    plt.savefig(f"./tel_analysis_gif/selected_star_{az_bin}{alt_bin}.png", dpi=200)
    plt.close()

def make_gif(time_str, nbins_alt, nbins_azi):
    """make gif image showing the order of target stars"""

    image_list=[]
    obs_time = Time(time_str, format='isot', scale='utc')
    start_alt_bin, start_az_bin = 0, 0
    for az_bin in range(start_az_bin, nbins_azi):
        for alt_bin in range(start_alt_bin, nbins_alt):
            file_path = f'./tel_analysis_gif/selected_star_{az_bin}{alt_bin}.png'
            if os.path.exists(file_path):
                img = Image.open(file_path)
                image_list.append(img)
    image_list[0].save('./tel_analysis_gif/selected_star.gif',save_all=True, append_images=image_list[1:],optimize=True, duration=350, loop=0)

def plot_all_stars(df, time_str):
    """plot all selected stars"""

    salt = Observer.at_site("SALT")
    targets = [FixedTarget(coord=SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg))) for ra, dec in zip(df.ra, df.dec)]
    fig = plt.figure(figsize=(6, 6))
    plot_sky(targets, salt, time_str, style_kwargs={'marker': 'o', 'color': 'gray'})
    plt.savefig(f"./tel_analysis_gif/all_selected_star.png", dpi=150)
