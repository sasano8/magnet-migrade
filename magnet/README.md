
# 開発ガイドライン


## データアクセス層
１つのエンティティに対する単純な操作を提供し、データアクセスの責任を負う。
データベースレベルの制約を担保する。
データアクセス層は、アクセス制御/セキュリティトリミングを処理するべきではない。
基本的にこのレイヤーは継承されたりすることはない。

## リポジトリ層
データ操作要求に対して、アプリケーションレベルの検証を行う。
リポジトリ層はアプリケーションレベルでの整合性を担保する。

## サービス層
複数のリポジトリを組み合わせて、より複雑な操作を提供する層？？

## エンドポイント層
クライアントからのリクエストをサービスに渡す。
複数のサービスを組み合わせることもある。


# 全文検索
sqlalchemy searchableを利用する。
sqlalchemy searchableは、postgresqlがサポートする全文検索ラッパーである。

おそらく、日本語検索や大規模検索は問題があるので、ほどほどの使用に控える。

# データベース
- 理由がなければ文字列カラムは255の文字長とする。8 bit = 256 byte = 空文字1文字 + 255文字


# sqlalchemy高速化
大量に行をロードする可能性がある場合は、次のようにできる。
filterがない場合、なぜかfromが無視されてしまう。。。

result = db.query(User).filter_by(id=1).with_entities("id")
result._addict()

# これはバグっぽい挙動で動かない
``` python
str(db.query(User).filter_by(id=1).with_entities("id"))
# => SELECT id FROM users WHERE users.id = %(id_1)s

str(db.query(User).with_entities("id"))
#  => SELECT id

# 代替案
db.query().select_from(User).with_entities("id")

# これが推奨
db.query(User).options(load_only(*UserOut.__fields__))
```


# データベースの整合性検証やスコープについて
- エンドポイント層で前提チェックを行う。
- ユースケース層を直接呼び出すとチェックが完了していないため、外部キー制約などに応じて例外が発生する可能性がある。
- 自分のデータ以外の参照は不可のようなクエリは、ユースケースにクエリを実装する。
