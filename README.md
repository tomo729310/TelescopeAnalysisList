# TelescopeAnalysisList
望遠鏡解析の際に使う天体のリストを作るコード。  
ここで作成したファイルをMakeScript.pyに適用して観測スクリプトを作る。  
(READMEは追記予定)

### 2mass_catalog
https://irsa.ipac.caltech.edu/applications/Gator/index.html  
ここにある2massカタログから以下の条件で天体リストを取得したテストファイルを置いている。  
なお、ファイルには"ra","dec","h_m"の列さえあれば2massカタログでなくても何でもいい。
  - 6.000 < h_m < 6.010
  - prox > 10arcsec

### tel_analysis.py
指定した時刻に見える空を100領域に分け、各領域に入る星をカタログから選ぶツール。  
作成されるファイルは、領域を順番に撮れるように星をリスト化したものになっている。  
保存先は"./output"。これで作った.txtファイルはそのままMakeScript.pyに適用できる。
- 使い方
  以下の引数を指定する。
  1. UTC時刻 : yyyy-mm-ddThh:mm:ss
  2. 1領域取る際の所要時間[sec]  
  (例)南ア時間で2023/10/10の午前2時00分から開始し、1領域に30秒かかるとき
  ```
  python tel_analysis.py 2023-10-10T02:00:00 30
  ```
  この場合、altとaziが小さい領域(図の上部付近)から星を撮ることができる。(UTC 2023-10-10T02:00:00~)  
  <img src="https://github.com/tomo729310/TelescopeAnalysisList/assets/95862047/dce94add-fa47-4567-b42e-8f333dd51d62" width="50%" />

- 出力
  100領域中、何個の領域に星があるかを表示させるようにしてる。以下は、上のコマンドを実行した時の出力例。
  ```
  targets : 90 in 100 fields
  script for MakeScript.py are saved to "./output/" 
  ```
  
### output
tel_analysis.pyで作成した観測可能な天体リストの保存先。
