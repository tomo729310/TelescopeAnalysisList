# TelescopeAnalysisList
望遠鏡解析の際に使う天体のリストを作るコード。  
ここで作成したファイルをMakeScript.pyに適用して観測スクリプトを作る。

## tel_analysis.py
指定した時刻に見える空を100領域(default)に分け、各領域に入る星をカタログから選ぶツール。  
作成されるファイルは、領域を順番に撮れるように星をリスト化したものになっている。  
保存先は"./output"。これで作った.txtファイルはそのままMakeScript.pyに適用できる。  
  
altitude(30°-80°)とazimuth(0°-360°)をいくつかに分割して撮る領域の数を決めている。
### 引数
  観測時刻は必ず指定。
  1. time_str : yyyy-mm-ddThh:mm:ss形式のUTC時刻  
  
  以下の引数の指定は任意。()はデフォルト値。
  1. interval : 1領域取る際の所要時間[sec]。(30)
  2. mag : 撮る星の等級。6から8までの等級。(6)
  3. nbins_alt or alt : altitudeのビンの数。(5)
  4. nbins_azi or azi : azimuthのビンの数。(20)

  (例1)南ア時間で2023/10/10の午前4時00分(UTCはこれの2時間前)から開始するとき、
  ```
  python tel_analysis.py 2023-10-10T02:00:00
  ```
  この場合、altとaziが小さい領域(図の上部付近)から星を撮ることができる。(UTC 2023-10-10T02:00:00~)  
  <img src="https://github.com/tomo729310/TelescopeAnalysisList/assets/95862047/dce94add-fa47-4567-b42e-8f333dd51d62" width="50%" />

  (例2)例1と同時刻に、20秒間隔で8等の星を3*10領域分だけ撮るとき、
  ```
  python tel_analysis.py 2023-10-10T02:00:00 --interval 20 --mag 8 --alt 3 --azi 10
  ```

### 出力
  指定した領域中、何個の領域に星があるかを表示する。  
  以下は、例1のコマンドを実行した時の出力例。
  ```
  targets : 90 in 100 fields
  script for MakeScript.py are saved to "./output/"
  ```

## 2mass_catalog
https://irsa.ipac.caltech.edu/applications/Gator/index.html  
ここにある2massカタログから以下の条件で天体リストを取得した3つのファイルを置いている。  
カタログの星の等級に合わせたファイル名にしている。
  - 6.000 < h_m < 6.010, prox > 10arcsec
  - 7.000 < h_m < 7.010, prox > 10arcsec
  - 8.000 < h_m < 8.010, prox > 10arcsec

## src
tel_analysis.py内で使う道具入れ

## output
tel_analysis.pyで作成した観測可能な天体リストの保存先。  
ここに作成された.txtファイルをMakeScript.pyに適用する。

## tel_analysis_gif
tel_analysis.py内の以下の部分を実行すると、tel_analysisディレクトリ下に新たに作成される画像の保存先。
```
#make gif image or display star positions
make_gif(time_str, nbins_alt, nbins_azi)
plot_all_stars(target_data, time_str)
```
- make_gif : ターゲットとなる星の順番を示すgif画像を作る。("selected_star.gif")
- plot_all_stars : 観測開始時刻における、ターゲットとなった全ての星の位置を示した画像を作る。("all_selected_star.png")

## Note

