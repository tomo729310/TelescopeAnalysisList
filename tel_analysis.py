import argparse
from astropy.time import Time
from astropy.coordinates import EarthLocation
import astropy.units as u

from src.tel_analysis.plot.plot import *
from src.tel_analysis.utils.utils import *

def main(time_str, interval=30, mag=6, nbins_alt=5, nbins_azi=20):
    """selected observable stars & make the script for MakeScript.py
        Args:
            time_str: observation start time. yyyy-mm-ddThh:mm:ss
            interval: time required per area. [sec] (default: 30)
            mag: catalog mag from 6 to 8 magnitude (default: 6)
            nbins_alt: number of altitude bins (default: 5)
            nbins_azi: number of azimuth bins (default: 20)

        Returns:
            Number of areas with stars and "*.txt" file for MakeScript.py
    """
    # setting
    obs_loc = EarthLocation(lat=-32.3763*u.deg, lon=20.8107*u.deg, height=1798*u.m)
    obs_time = Time(time_str, format='isot', scale='utc')

    # star info, ra, dec from catalog
    df_tmp, df_ra, df_dec = load_2mass_catalog(mag)

    # make alt/azi bins & areas
    altitude_bins, azimuth_bins, star_map = make_bins(nbins_alt, nbins_azi)

    # assign stars to each area
    start_alt_bin, start_az_bin = 0, 0

    # progress bar info
    print("start searching bright stars in each area...")
    total_areas = nbins_azi * nbins_alt
    current_area = 0

    for az_bin in range(start_az_bin, nbins_azi):
        for alt_bin in range(start_alt_bin, nbins_alt):

            # progress bar
            current_area += 1
            progress_percentage = current_area / total_areas
            progress_bar_length = int(50 * progress_percentage)

            print(f"[{'#' * progress_bar_length}{' ' * (50 - progress_bar_length)}] {progress_percentage * 100:.2f}%", end='\r')

            # area(0,0)
            if alt_bin == start_alt_bin and az_bin == start_az_bin:
                start_altaz_coords = calc_altaz_coords(df_ra*u.deg, df_dec*u.deg, obs_time, obs_loc) # calc alt/azi coords @ obs start time
                df_tmp['altitude'], df_tmp['azimuth'] = start_altaz_coords.alt.degree, start_altaz_coords.az.degree

                start_bin_stars = find_star(df_tmp, altitude_bins, azimuth_bins, start_alt_bin, start_az_bin) # find stars in area(0,0)

                if not start_bin_stars.empty: # check if empty
                    star_map = add_star(start_bin_stars, star_map, start_altaz_coords, start_alt_bin, start_az_bin)

                    # plot star in this area
                    # plot_stars(df_tmp, start_bin_stars, star_map, start_altaz_coords, obs_time, az_bin, alt_bin)

            # the other areas
            else:
                obs_time += interval*u.second # advance time by "interval" seconds
                new_altaz_coords = calc_altaz_coords(df_ra*u.deg, df_dec*u.deg, obs_time, obs_loc) # re-calc alt/azi coords at the new "obs_time"
                df_tmp['altitude'], df_tmp['azimuth'] = new_altaz_coords.alt.degree, new_altaz_coords.az.degree

                other_bin_stars = find_star(df_tmp, altitude_bins, azimuth_bins, alt_bin, az_bin)

                if not other_bin_stars.empty:
                    star_map = add_star(other_bin_stars, star_map, new_altaz_coords, alt_bin, az_bin)

                    # plot star in this area
                    # plot_stars(df_tmp, other_bin_stars, star_map, start_altaz_coords, obs_time, az_bin, alt_bin)

    target_data = make_dataframe(nbins_alt, nbins_azi, star_map, altitude_bins, azimuth_bins)
    target_data.to_csv(f"./output/script_tmp.txt", index=True, header=False, index_label='id')
    print("")
    print(f"targets : {len(target_data)} in {nbins_alt*nbins_azi} fields")
    print(f"script for MakeScript.py are saved as \"./output/script_tmp.txt\" ")
    print("--------------------------")
    print("Please move \"script_tmp.txt\" to \"MakeScript-main/List/\" and check Offset file (filters, RA/ Dec offset value, etc...) ")
    print("--------------------------")

    # #make gif image or display star positions
    # make_gif(time_str, nbins_alt, nbins_azi)
    # plot_all_stars(target_data, time_str)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Star selection for telescope analysis")

    parser.add_argument("time_str", help="observation start time(UTC) in \"yyyy-mm-ddThh:mm:ss\"")
    parser.add_argument("--interval", type=int, default=30, help="time required per area [sec] (default: 30)")
    parser.add_argument("--mag", default=6, help="catalog magnitude from 6 to 8 (default: 6)")
    parser.add_argument("--nbins_alt", "--alt", type=int, default=5, help="Number of altitude bins (default: 5)")
    parser.add_argument("--nbins_azi", "--azi", type=int, default=20, help="Number of azimuth bins (default: 20)")

    args = parser.parse_args()
    main(args.time_str, args.interval, args.mag, args.nbins_alt, args.nbins_azi)
