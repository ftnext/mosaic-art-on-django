# このリポジトリについて
Djangoでモザイクアートが作れるアプリケーションを作成します。

モザイクアート作成のソースコードのリポジトリ：
ftnext/[mosaic-art-python](https://github.com/ftnext/mosaic-art-python)

# 開発環境
* Python 3.6.3
* Python 3.5.1

2台の端末で開発を進めています。

# 動作させるまで
* このリポジトリをクローン
* 必要なモジュールをpip install
  * `pip install django==1.11`
  * `pip install pillow`
* manage.py関連のコマンド
  * `python manage.py migrate` (`python manage.py runserver`すると実行を促すメッセージが出た)
  * `python manage.py migrate gallery` (MosaicArtモデルのテーブルを作成)
  * `python manage.py createsuperuser` (スーパーユーザの作成)

# 参考
* [Django Girls Tutorial](https://djangogirlsjapan.gitbooks.io/workshop_tutorialjp/)
* Django Girls Tutorialを適宜読み替えながら進めています。
