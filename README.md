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

### output
tel_analysis.ipynbで作成した観測可能な天体リストの保存先。
