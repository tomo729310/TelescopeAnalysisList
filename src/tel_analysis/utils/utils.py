import pandas as pd
import numpy as np
from astropy.coordinates import AltAz, SkyCoord
import astropy.units as u

import os
import glob

def extract_magnitude(file_name):
    """get magnitude info from a specified file name.

    Args:
        file_name : file name in a specified format containing magnitude information.
    """

    # Extract only the number part and convert to float
    magnitude_part = file_name.split('_')[-1]
    magnitude_value = float(''.join(filter(str.isdigit, magnitude_part)))
    return magnitude_value

def read_and_combine_files(folder_path, catalog_base_name):
    file_list = glob.glob(os.path.join(folder_path, f'{catalog_base_name}*mag.csv'))
    df_list = []

    for file_path in file_list:
        df = pd.read_csv(file_path)
        magnitude = extract_magnitude(os.path.basename(file_path))
        df.insert(0, 'order', magnitude)
        df_list.append(df)

    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df.sort_values(by='order')

def create_or_update_catalog_star_list(folder_path, catalog_star_list_path, catalog_base_name):

    # Check if "catalog_star_list.csv" does not exist. If not, create a new one.
    if not os.path.exists(catalog_star_list_path):
        combined_df = read_and_combine_files(folder_path, catalog_base_name)
        combined_df.to_csv(catalog_star_list_path, index=False)
    # If "catalog_star_list.csv" already exists, add a new magnitude list (if any)
    else:
        catalog_star_list_df = pd.read_csv(catalog_star_list_path)
        existing_magnitudes = set(catalog_star_list_df['order'])

        for file_path in glob.glob(os.path.join(folder_path, f'{catalog_base_name}*mag.csv')):
            magnitude = extract_magnitude(os.path.basename(file_path))

            # Add catalog files for any magnitude not in "catalog_star_list.csv"
            if magnitude not in existing_magnitudes:
                new_df = pd.read_csv(file_path)
                new_df.insert(0, 'order', magnitude)
                catalog_star_list_df = pd.concat([catalog_star_list_df, new_df], ignore_index=True)
                existing_magnitudes.add(magnitude)

        catalog_star_list_df = catalog_star_list_df.sort_values(by='order')
        catalog_star_list_df.to_csv(catalog_star_list_path, index=False)

def load_2mass_catalog():
    """load 2mass catalog

    Returns:
        catalog all data, H-mag, ra, dec, prox (type:DataFrame)
        Note: prox(=proximity)...distance in arcsec to nearest catalog point source
    """
    catalog_file = './2mass_catalog/table_irsa_catalog_search_results.csv'
    # catalog_file = f'./2mass_catalog/table_irsa_catalog_search_results_10mag.csv'
    df = pd.read_csv(catalog_file)
    return df, df["ra"], df["dec"]

def calc_altaz_coords(ra, dec, obs_time, obs_loc):
    """calc ra/dec and convert to alt/az at "obs_loc" & "obs_time"

    Args:
        ra : ra of catalog star
        dec : dec of catalog star
        obs_time : UTC, yyyy-mm-ddThh:mm:ss
        obs_loc : location

    Returns:
        alt/az coords of stars at "obs_loc" & "obs_time"
    """
    coords = SkyCoord(ra, dec, frame='icrs', unit="deg")
    altaz_frame = AltAz(obstime=obs_time, location=obs_loc)
    altaz_coords = coords.transform_to(altaz_frame)
    return altaz_coords

def make_bins(nbins_alt, nbins_az):
    """make bins & areas

    Args:
        nbins_alt : number of altitude bins (default: 5)
        nbins_az : number of azmuth bins (default: 20)

    Returns:
        total bins of alt/az & dictionary representing areas for star map
    """
    min_alt, max_alt = 30, 80 # degree
    # min_az, max_az = 0, 360 # degree
    min_az, max_az = -180, 180
    altitude_bins = np.linspace(min_alt, max_alt, nbins_alt + 1)
    azimuth_bins = np.linspace(min_az, max_az, nbins_az + 1)
    print(azimuth_bins)
    # azimuth_bins = np.concatenate([azimuth_bins[int(nbins_az/2):], azimuth_bins[:int(nbins_az/2)]])
    # print(azimuth_bins)

    star_map = {(alt_bin, az_bin): None for alt_bin in range(nbins_alt) for az_bin in range(nbins_az)} # dictionary of areas
    print(star_map)
    return altitude_bins, azimuth_bins, star_map

def find_star(mag, star_info, altitude_bins, azimuth_bins, alt_bin, az_bin):
    """find stars in each area

    Args:
        mag : Magnitude of the star you want to observe
        star_info : star catalog DataFarme containing such as ["altitude"] & ["azimuth"]
        altitude_bins : total bins of altitude
        azimuth_bins : total bins of azimuth

    Returns:
        DataFrame containing stars within each area
    """

    star_info["azimuth"] = ((star_info["azimuth"] + 180) % 360) - 180 # (0,360)deg -> (-180,180)deg

    matched_stars = star_info.loc[
        (star_info["altitude"].between(altitude_bins[alt_bin], altitude_bins[alt_bin+1])) &
        (star_info["azimuth"].between(azimuth_bins[az_bin], azimuth_bins[az_bin+1])) &
        ((star_info["h_m"] >= mag) & (star_info["h_m"] < mag + 0.5)) &
        (star_info["prox"] >= 75)
    ]
    # print(f"matched_stars:{len(matched_stars)}, {np.shape(matched_stars)}")
    filtered_stars_df = pd.DataFrame(matched_stars)

    return filtered_stars_df

def add_star(bin_stars, star_map, altaz_coords, alt_bin, az_bin):
    """add the star with the largest RA to star map

    Args:
        bin_stars : DataFrame containing stars within each area
        star_map : dictionary representing areas for star map
        altaz_coords : alt/az coords of stars at "obs_loc" & "obs_time"
        alt_bin : index of the altitude bin
        az_bin : index of the azimuth bin

    Returns:
        updated star map after adding the selected star
    """
    # Sort the DataFrame by "ra" and get the first row
    selected_star = bin_stars.sort_values("ra", ascending=False).iloc[0]

    # Update altitude and azimuth of the selected star
    selected_star.at['altitude'] = altaz_coords.alt.degree[0]  # または適切な行を選択
    selected_star.at['azimuth'] = altaz_coords.az.degree[0]

    # Add the selected star to the star map
    star_map[(alt_bin, az_bin)] = selected_star

    return star_map

def make_dataframe(nbins_alt, nbins_az, star_map, altitude_bins, azimuth_bins):
    data = []
    for az_bin in range(nbins_az):
        for alt_bin in range(nbins_alt):
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
    return df_script
