# 仮想通貨の損益計算スクリプト   

CoinCheckとGMOコインの仮想通貨履歴より，損益計算をします。   

## 使い方:
1. 適当な名前のフォルダ内にCoinCheck/GMOコインからダウンロードした購入ログを全部置く。
    - 同じ内容のファイルが複数あった場合には，重複して計算されるので要注意
2. スクリプト`crypt2csv.py`の先頭部分にある以下の行を，自分の管理したい仮想通貨リストに変更。出力ファイル`crypt-symmary`内の出力順はこのリスト順になる。
```
crypts = ["BTC","ETH","BTC","LTC","XEM"]
```
3. スクリプト実行
```
$crypt2csv.py <上記フォルダ名>
```

## 損益計算方法

確定申告の計算基準にしたがって，売却時点までの全取引所での取引履歴に従った平均購入単価を計算(移動平均法)し，以下で計算
> 売却価格-平均購入単価×売却数

注意) 手元の購入履歴では購入時手数料が0なので，上記売却価格に手数料が含まれるか否かは未確認。税務上の手数料は以下の通り。
- 購入時の手数料: 購入単価に組み入れ(対応済みのつもり)
- 売却時の手数料: 必要経費として別途計上(手数料込みの購入ログの取得時にプログラム要確認)
- 参考: [暗号資産に関する税務上の取扱い及び計算書について（令和2年12月）](https://www.nta.go.jp/publication/pamph/shotoku/kakuteishinkokukankei/kasoutuka/index.htm)


## 出力ファイル
1. crypt-history.csv
  - 各通貨ごとに購入履歴とともに，売却時の損益を計算した結果
2. crypt-summary.csv
  - 追加ごとの保有状況のサマリ
3. crypt-shop-summary.csv
  - 各取引所毎の通貨の保有状況の計算結果
  - 表示項目
    - 「約定数」: 保有数
    - 「平均単価」: 該当の取引所での購入価額ではなく，全取引所での取引履歴に基づく平均購入単価
    - 「購入額」: 上記2項目の積

## 使用上の注意

- もしかしたら**計算方法の間違いがあるかも**しれません。ご利用は自己責任でよろしくおねがいします。
- バグのご報告は歓迎です。


