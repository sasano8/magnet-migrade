# ベンダリング


# プロジェクトクローン時

プロジェクトクローン時は次のコマンドでサブモジュールを最新化してください

```
# サブモジュールおよびにネストしたサブモジュールを最新にする（最新かバージョン固定か考える）
git submodule update --init --recursive
```

# サブモジュール追加方法

```
# サブモジュール（リポジトリ）を追加する
git submodule add https://github.com/user_name/xxx_library vendor/xxx_library
```
