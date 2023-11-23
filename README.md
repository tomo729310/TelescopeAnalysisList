# TelescopeAnalysisList
望遠鏡解析の際に使う天体のリストを作るコード。  
ここで作成したファイルをMakeScript.pyに適用して観測スクリプトを作る。

## tel_analysis.py
指定した時刻に見える空を100領域(default)に分け、各領域に入る星をカタログから選ぶツール。  
作成されるファイルは、領域を北から順番に撮れるように星をリスト化したものになっている。  
保存先は"./output"。これで作った.txtファイルはそのままMakeScript.pyに適用できる。  
  
altitude(30°-80°)とazimuth(0°-360°)をいくつかに分割して撮る領域の数を決めている。(調整可)
### 使い方
  観測時刻は必ず指定。
  1. time_str : yyyy-mm-ddThh:mm:ss形式のUTC時刻  
  
  以下の引数の指定は任意。()はデフォルト値。
  1. interval : 1領域取る際の所要時間[sec]。(30)
  2. mag : 撮る星の2massでのHband等級。9から12までの等級。(10)
  3. nbins_alt or alt : altitudeのビンの数。(5)
  4. nbins_azi or azi : azimuthのビンの数。(20)

  (例1)南ア時間で2023/11/25の午前0時00分(UTCはこれの2時間前)から開始するとき、
  ```
  python tel_analysis.py 2023-11-24T22:00:00
  ```

  (例2)例1と同時刻に、10分(600秒)間隔で9等の星を3*10領域分だけ撮るとき、
  ```
  python tel_analysis.py 2023-11-24T22:00:00 --interval 600 --mag 9 --alt 3 --azi 10
  ```

### 出力
  指定した領域中、何個の領域に星があるかを表示する。  
  以下は、例1のコマンドを実行した時の出力例。
  ```
start searching bright stars in each area...
[##################################################] 100.0%
targets : 88 in 100 fields
script for MakeScript.py are saved as "./output/script_tmp.txt" 
--------------------------
Please move "script_tmp.txt" to "MakeScript-main/List/" and check Offset file (filters, RA/ Dec offset value, etc...) 
--------------------------
  ```

## 2mass_catalog
https://irsa.ipac.caltech.edu/applications/Gator/index.html  
ここにある2massカタログから以下の条件で天体リストを取得した3つのファイルを置いている。()内は条件を満たすおおよその星の数。  
カタログの星の等級に合わせたファイル名にしている。(proxとは、近くの星までの距離[arcsec]を表す。)
  - 9.00 < h_m < 9.50, prox > 50arcsec (~7000)
  - 10.00 < h_m < 10.30, prox > 50arcsec (~8000)
  - 11.00 < h_m < 11.13, prox > 50arcsec (~7600)
  - 12.00 < h_m < 12.16, prox > 50arcsec (~7000)  
また、等級のラベルのついていないファイルは以下の条件で天体リストを取得しており、プログラム内ではこのファイルを読んでいる。  
  - h_m < 12.00, prox > 75

## src
tel_analysis.py内で使う道具入れ

## output
tel_analysis.pyで作成した観測可能な天体リストの保存先。  
ここに作成された.txtファイルをMakeScript.pyに適用する。

## tel_analysis_gif
tel_analysis.py内の以下の部分を実行すると、tel_analysisディレクトリ下に新たに作成されるディレクトリ。  
選んだ星の位置や取る順番を示す画像がここに保存される。
```
#make gif image or display star positions
make_gif(time_str, nbins_alt, nbins_azi)
plot_all_stars(target_data, time_str)
```
- make_gif : ターゲットとなる星の順番を示すgif画像を作る。例1にあるようなgif画像が作成される(ファイル名:"selected_star.gif")
- plot_all_stars : 観測開始時刻における、ターゲットとなった全ての星の位置を示した画像を作る。(ファイル名:"all_selected_star.png")

## Note
v2.1:星選びには特に必要ないので、tel_analysis.py内のplot_stars関数をコメントアウト。2mass_catalogに4等、5等のカタログを追加。  
v2.2:プログレスバーを追加。出力ファイルの移動を促すコメントを追加。
v3.0:孤立した星を選べるようにカタログファイルやtel_analysis.pyを調整。不要なファイルを削除。

