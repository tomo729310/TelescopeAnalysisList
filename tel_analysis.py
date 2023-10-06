import pandas as pd
import numpy as np
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
import astropy.units as u

def main(time_str, interval):
    
    """selected observable stars & make the script for MakeScript.py
        Args:
            time_str: observation start time. yyyy-mm-ddThh:mm:ss
            interval: time required per area. [sec]

        Returns:
            Number of areas with stars and "*.txt" file for MakeScript.py
    """

    # load 2mass catalog
    csv_file = './2mass_catalog/table_irsa_catalog_search_results_tmp.csv'
    df_tmp = pd.read_csv(csv_file)

    # setting
    obs_loc = EarthLocation(lat=-32.3763*u.deg, lon=20.8107*u.deg, height=1798*u.m) # location
    obs_time = Time(time_str, format='isot', scale='utc') # UTC, yyyy-mm-ddThh:mm:ss

    # calc ra/dec and convert to alt/azi at "obs_loc" & "obs_time"
    coords = SkyCoord(ra=df_tmp['ra']*u.deg, dec=df_tmp['dec']*u.deg, frame='icrs')
    altaz_frame = AltAz(obstime=obs_time, location=obs_loc)
    altaz_coords = coords.transform_to(altaz_frame)
    df_tmp['altitude'], df_tmp['azimuth'] = altaz_coords.alt.degree, altaz_coords.az.degree

    # make bins & areas
    num_altitude_bins, num_azimuth_bins = 5, 20
    altitude_bins = np.linspace(30, 80, num_altitude_bins + 1)
    azimuth_bins = np.linspace(0, 360, num_azimuth_bins + 1)
    star_map = {(alt_bin, az_bin): None for alt_bin in range(num_altitude_bins) for az_bin in range(num_azimuth_bins)} # dictionary of areas

    # assign stars to each area
    start_alt_bin, start_az_bin = 0, 0
    for az_bin in range(start_az_bin, num_azimuth_bins):
        for alt_bin in range(start_alt_bin, num_altitude_bins):
            
            # area(0,0)
            if alt_bin == start_alt_bin and az_bin == start_az_bin:
                bin_stars = df_tmp.loc[(df_tmp['altitude'].between(altitude_bins[start_alt_bin], altitude_bins[start_alt_bin + 1])) &
                            (df_tmp['azimuth'].between(azimuth_bins[start_az_bin], azimuth_bins[start_az_bin + 1]))] # find stars in area(0,0)

                if not bin_stars.empty: # check if "bin_stars" is empty
                    start_star = bin_stars.nlargest(1, 'ra').iloc[0] # select the star with the largest RA
                    start_star['altitude'], start_star['azimuth'] = altaz_coords.alt.degree, altaz_coords.az.degree
                    star_map[(start_alt_bin % num_altitude_bins, start_az_bin % num_azimuth_bins)] = start_star

                    """ plot the selected stars
                    import matplotlib.pyplot as plt
                    from astroplan import Observer
                    from astroplan.plots import plot_sky
                    import os
                    gif_dir = "tel_analysis_gif"
                    os.makedirs(gif_dir, exist_ok=True)
                    salt = Observer.at_site("SALT")
                    fig = plt.figure(figsize=(6, 6))
                    selected_coords = SkyCoord(ra=start_star['ra']*u.deg, dec=start_star['dec']*u.deg, frame='icrs')
                    plot_sky(selected_coords, salt, obs_time, style_kwargs={'marker': 'o', 'color': 'gray'})
                    plt.title(f"UTC {obs_time}", fontsize=14)
                    #plt.savefig(f"./tel_analysis_gif/selected_star_{az_bin}{alt_bin}.png", dpi=200)
                    plt.close()
                    """

            # the other areas
            else:
                obs_time += interval*u.second # advance time by "interval" seconds
                altaz_frame = AltAz(obstime=obs_time, location=obs_loc) # re-calc at the new "obs_time"
                altaz_coords = coords.transform_to(altaz_frame)
                df_tmp['altitude'], df_tmp['azimuth'] = altaz_coords.alt.degree, altaz_coords.az.degree

                bin_stars = df_tmp[(df_tmp['altitude'].between(altitude_bins[alt_bin], altitude_bins[alt_bin + 1])) &
                                   (df_tmp['azimuth'].between(azimuth_bins[az_bin], azimuth_bins[az_bin + 1]))]

                if not bin_stars.empty:
                    selected_star = bin_stars.nlargest(1, 'ra').iloc[0]
                    selected_star['altitude'], selected_star['azimuth'] = altaz_coords.alt.degree, altaz_coords.az.degree
                    star_map[(alt_bin, az_bin)] = selected_star

                    """ plot the selected stars
                    fig = plt.figure(figsize=(6, 6))
                    selected_coords = SkyCoord(ra=start_star['ra']*u.deg, dec=start_star['dec']*u.deg, frame='icrs')
                    plot_sky(selected_coords, salt, obs_time, style_kwargs={'marker': 'o', 'color': 'gray'})
                    plt.title(f"UTC {obs_time}", fontsize=14)
                    #plt.savefig(f"./tel_analysis_gif/selected_star_{az_bin}{alt_bin}.png", dpi=200)
                    plt.close()
                    """

    # make Dataframe
    data = []
    for az_bin in range(num_azimuth_bins):
        for alt_bin in range(num_altitude_bins):
            star = star_map[(alt_bin, az_bin)]
            if star is not None:
                star_data = {
                    'ra': star['ra'],
                    'dec': star['dec'],
                    'altitude': altitude_bins[alt_bin],
                    'azimuth': azimuth_bins[az_bin]
                }
                data.append(star_data)

    df = pd.DataFrame(data)
    df.sort_values(by=['azimuth', 'altitude'], inplace=True)
    df_script = df.reset_index(drop=True)
    df_script = df_script.drop(['azimuth', 'altitude'], axis=1)
    df_script.to_csv(f"./output/script_tmp.txt", index=True, header=False, index_label='id')
    print(f"targets : {len(df)} in {num_altitude_bins*num_azimuth_bins} fields")
    print(f"script for MakeScript.py are saved to \"./output\" ")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python tel_analysis.py <yyyy-mm-ddThh:mm:ss> <interval>")
        sys.exit(1)

    time_str, interval = sys.argv[1], int(sys.argv[2])
    main(time_str, interval)


""" make gif
from PIL import Image
import os
image_list=[]
#time_str = "2023-10-10T02:00:00"
obs_time = Time(time_str, format='isot', scale='utc')
start_alt_bin, start_az_bin = 0, 0
for az_bin in range(start_az_bin, num_azimuth_bins): 
    for alt_bin in range(start_alt_bin, num_altitude_bins):
        file_path = f'./tel_analysis_gif/selected_star_{az_bin}{alt_bin}.png'
        if os.path.exists(file_path):
            img = Image.open(file_path)
            image_list.append(img)

#image_list[0].save('./tel_analysis_gif/selected_star.gif',save_all=True, append_images=image_list[1:],optimize=True, duration=300, loop=0)
"""

""" plot all selected stars
salt = Observer.at_site("SALT")
targets = [FixedTarget(coord=SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg))) for ra, dec in zip(df.ra, df.dec)]
fig = plt.figure(figsize=(6, 6))
plot_sky(targets, salt, time_str, style_kwargs={'marker': 'o', 'color': 'gray'})
"""