import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
from astropy import units as u
from astroplan import Observer
import sys

def main(time_str):
    csv_file = './2mass_catalog/table_irsa_catalog_search_results_tmp.csv' ## カタログ読み込み
    df_tmp = pd.read_csv(csv_file)

    obs_loc = EarthLocation(lat=-32.3763*u.deg, lon=20.8107*u.deg, height=1798*u.m) ## 観測地点
    obs_time = Time(time_str, format='isot', scale='utc') ## 観測時刻
    coords = SkyCoord(ra=df_tmp['ra']*u.deg, dec=df_tmp['dec']*u.deg, frame='icrs')

    altaz_frame = AltAz(obstime=obs_time, location=obs_loc) ## 地平座標に変換
    altaz_coords = coords.transform_to(altaz_frame)
    df_tmp['altitude'] = altaz_coords.alt.degree
    df_tmp['azimuth'] = altaz_coords.az.degree

    # alt/azi 分割数 (alt*azi=領域数)
    num_altitude_bins = 5
    num_azimuth_bins = 20

    ## alt/azi 角度範囲
    altitude_bins = np.linspace(30, 80, num_altitude_bins + 1)
    azimuth_bins = np.linspace(0, 360, num_azimuth_bins + 1)

    ## 領域ごとの星を格納する箱
    star_map = {(alt_bin, az_bin): None for alt_bin in range(num_altitude_bins) for az_bin in range(num_azimuth_bins)}

    ## カタログ内の星を分割した領域に追加
    for star in df_tmp.itertuples():
        altitude, azimuth = star.altitude, star.azimuth
        alt_bin = np.digitize(altitude, altitude_bins) -1
        az_bin = np.digitize(azimuth, azimuth_bins) -1
        if 0 <= alt_bin < num_altitude_bins and 0 <= az_bin < num_azimuth_bins:
            if star_map[(alt_bin, az_bin)] is None: ## その領域に既に星が割り振られているかどうか
                star_map[(alt_bin, az_bin)] = star
            else:
                existing_star = star_map[(alt_bin, az_bin)] ## 既に星があったら何かの基準で1つに絞る
                if star.ra > existing_star.ra:
                    # 新しい星のraが既存の星より大きい場合にのみ置き換える(全領域で同じ基準で星決めた方がいいかと思ってとりあえず追加した)
                    star_map[(alt_bin, az_bin)] = star

    data = []
    for alt_bin in range(num_altitude_bins):
        for az_bin in range(num_azimuth_bins):
            star = star_map[(alt_bin, az_bin)]
            if star is not None:
                star_data = {
                    'ra': star.ra,
                    'dec': star.dec,
                    'altitude': altitude_bins[alt_bin],
                    'azimuth': azimuth_bins[az_bin]
                }
                data.append(star_data)

    df = pd.DataFrame(data)
    df.sort_values(by=['azimuth', 'altitude'], inplace=True)
    df_script = df.reset_index(drop=True)
    df_script = df_script.drop(['azimuth', 'altitude'], axis=1)
    df_script.to_csv(f"./output/script_tmp.txt", index=True, header=False, index_label='id')
    print(f"targets : {len(df)} in {num_altitude_bins*num_azimuth_bins}fields") ## 全領域中、何領域に星が割り振られたか
    print("script for MakeScript.py are saved to \"./output/*\" ")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tel_analysis.py yyyy-mm-ddThh:mm:00")
    else:
        time_str = sys.argv[1]
        main(time_str)
