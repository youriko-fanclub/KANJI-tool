# KANJI-tool

build用のスクリプトとか置く予定
ここに説明を書いていく

- id_manage.py
  - id.toml からID情報をロード
  - 数値を渡すとそれが属するIDを返す
  - ID名を渡すとその定義域を返す
- master_type.py
  - masterdata.toml から型情報をロード
- validate_data.py
  - 実データ (schema/master/class/) が 型定義(masterdata.toml) に適合しているかを確認
- cpp_source_generator.py
  - 与えられた方情報をもとに hpp/cpp生成を行う
- build_schema.py
  - hpp/cpp自動生成時に呼ぶ
  - master_type.py を呼び出し型情報を取得、それを cpp_source_generator.py に渡してファイルを生成
- repository_path.py
  - path.toml にて固有のパスを定義、それを読み出す

