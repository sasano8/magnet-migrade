# ui

## Build Setup

```bash
# install dependencies
$ yarn install

# serve with hot reload at localhost:3000
$ yarn dev

# build for production and launch server
$ yarn build
$ yarn start

# generate static project
$ yarn generate
```

For detailed explanation on how things work, check out [Nuxt.js docs](https://nuxtjs.org).

# Format

## eslint

コードフォーマッタ

## prettier

eslint でできないフォーマットを補う

# なんか上手く行かない

## typescript として認識しない

script タグで ts を指定する

```typescript
<script lang="ts"></script>
```

# エディタ環境動作確認

`sample.ts`などのファイルを作成し次のコードをコピーし、ソースを保存すると自動フォーマットが行われるはずです。

動作しない場合は、`esbenp.prettier-vscode`を導入してみてください。

```
function test(){
    console.log("test");;;;;;;
        console.log("test");;;;;;;
}
```
