# ベンダリング


# プロジェクトクローン時

プロジェクトクローン時は次のコマンドでサブモジュールを最新化してください

```
# サブモジュールおよびにネストしたサブモジュールを最新にする（更新してしまうので注意）
git submodule update --init --recursive
```

# サブモジュール追加方法

```
# サブモジュール（リポジトリ）を追加する
git submodule add https://github.com/user_name/xxx_library vendor/xxx_library

# poetryで依存性を追加する
poetry add ./vendor/xxx_library
```


