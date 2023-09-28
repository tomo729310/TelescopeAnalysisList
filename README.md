## TelescopeAnalysisList
望遠鏡解析の際に使う天体のリストを作るツール。

### 2mass_catalog
https://irsa.ipac.caltech.edu/applications/Gator/index.html  
ここにある2massカタログから以下の条件で天体リストを取得したテストファイルを置いている。  
なお、ファイルには"ra","dec","h_m"の列さえあれば2massカタログでなくても何でもいい。
  - 6.000 < h_m < 6.010
  - prox > 10arcsec  
  
### tel_analysis.ipynb
指定した時刻に観測所から見える天体を選ぶ。  
2種類のファイルを作成するようにしている。ファイルの保存先は"./output"。
  - tpoint_20230811T0100.txt
      [id,ra,dec,h_m]の列がある。(取った天体の等級を確認する用とかに使えるかも)
  - tpointscript_20230811T0100.txt
      [id,ra,dec]の列があるが、headerは付けていない。  
      観測ソフトに流すスクリプトを作るように使うファイル。

### tel_analysis.py
指定した時刻に見える空を100領域に分け、各領域に入る星をカタログから選ぶツール。  
ファイルの保存先は"./output"。
- 使い方
  時刻を以下の形式で引数にする。ただし、入力するのはUTCで。
  ```
  python tel_analysis.py yyyy-mm-ddThh:mm:00
  ```
- 出力
  100領域中、何個の領域に星があるかを表示させるようにしてる。以下は、上のコマンドを実行した時の出力例。
  ```
  targets : 91 in 100fields
  script for MakeScript.py are saved to "./output/*" 
  ```
  
### output
tel_analysis.ipynbで作成した観測可能な天体リストの保存先。
