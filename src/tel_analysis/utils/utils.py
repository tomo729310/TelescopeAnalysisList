import pandas as pd
import numpy as np
from astropy.coordinates import AltAz, SkyCoord
import astropy.units as u

def load_2mass_catalog(mag):
    """load 2mass catalog

    Args:
        mag : star magnitude
    """
    catalog_file = f'./2mass_catalog/table_irsa_catalog_search_results_{mag}mag.csv'
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
    coords = SkyCoord(ra, dec, frame='icrs')
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
    min_az, max_az = 0, 360 # degree
    altitude_bins = np.linspace(min_alt, max_alt, nbins_alt + 1)
    azimuth_bins = np.linspace(min_az, max_az, nbins_az + 1)
    star_map = {(alt_bin, az_bin): None for alt_bin in range(nbins_alt) for az_bin in range(nbins_az)} # dictionary of areas
    return altitude_bins, azimuth_bins, star_map

def find_star(star_info, altitude_bins, azimuth_bins, alt_bin, az_bin):
    """find stars in each area

    Args:
        star_info : star catalog DataFarme containing such as ["altitude"] & ["azimuth"]
        altitude_bins : total bins of altitude
        azimuth_bins : total bins of azimuth
        alt_bin (_type_): _description_
        az_bin (_type_): _description_

    Returns:
        DataFrame containing stars within each area
    """
    bin_stars = star_info.loc[ (star_info["altitude"].between(altitude_bins[alt_bin], altitude_bins[alt_bin+1])) &
                            (star_info["azimuth"].between(azimuth_bins[az_bin], azimuth_bins[az_bin+1])) ]
    return bin_stars

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
    selected_star = bin_stars.nlargest(1, "ra").iloc[0]
    selected_star['altitude'], selected_star['azimuth'] = altaz_coords.alt.degree, altaz_coords.az.degree
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
