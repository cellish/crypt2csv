#!/usr/bin/env python3

import sys
import pandas as pd
from IPython.display import display
import pytz
from pathlib import Path

def GMO_data(df):
    GMO_label={
    #'日時':'',
    '注文ID':'ID',
    '銘柄名':'銘柄',
    '売買区分':'売買',
    '約定数量':'約定数',
    '日本円受渡金額':'売買価格',
    '約定レート':'レート'
    }
    # 授受区分    数量  送付手数料   送付先/送付元 トランザクションID
    df["取引所"]="GMO"
#    df["日時"]=pd.to_datetime(df['time'], format='%Y/%m/%d %H:%M', utc=False)
    df["日時"]=pd.to_datetime(df['日時'], format='%Y/%m/%d %H:%M:%S')\
        .dt.tz_localize(pytz.timezone('ASIA/Tokyo'))

    df.rename(columns=GMO_label, inplace=True)
    df.drop(columns=['約定ID','建玉ID','精算区分','取引区分','執行条件','注文タイプ','約定金額','注文手数料','レバレッジ手数料','入出金区分','入出金金額'], 
        errors='ignore', inplace=True)
    df["売買"] = df["売買"].str.replace("売", "Sell")
    df["売買"] = df["売買"].str.replace("買", "Buy")
    df['約定数'] = df['約定数'].where(df['売買価格'] < 0, -df['約定数'])


def CC_data(df):
    CC_label={
    'id':'ID',
#    'time':'日時',
    'trading_currency':'銘柄',
    'operation':'売買',
    'amount':'約定数',
    'price':'売買価格'
    }

    df["取引所"]="CoinCheck"
    df["日時"]=pd.to_datetime(df['time'],utc=True)\
        .dt.tz_convert(pytz.timezone('ASIA/Tokyo'))

    df.rename(columns=CC_label, inplace=True)
    df['売買価格'] = df['売買価格'].where(df['銘柄'] != 'JPY', df["約定数"])
    df['約定数'] = df['約定数'].mask(df['銘柄'] == 'JPY')
    display(df.head())

    df.drop(columns=['original_currency','fee','comment'], 
        errors='ignore', inplace=True)

# https://stackoverflow.com/questions/16698415/reference-previous-row-when-iterating-through-dataframe/38155257#38155257
def apply_func_decorator(func):
    prev_row = {}

    def wrapper(curr_row, **kwargs):
        if not prev_row.get("銘柄") == curr_row["銘柄"]:
            prev_row["平均単価"] = 0
            prev_row["保有数"] = 0

        val = func(curr_row, prev_row)
        prev_row.update(curr_row)
        prev_row["平均単価"] = val
        return val

    return wrapper

@apply_func_decorator
def running_mean(curr, prev):
    if curr["売買"] == "Sell":
        ret = prev.get("平均単価", 0.0)
    else:
        ret = (prev.get("平均単価", 0) * prev.get("保有数", 0) - curr["売買価格"]) / curr["保有数"]

    return ret

def get_profit(df):
    ##### for all #####
    df["単価"] = -df["売買価格"] / df["約定数"]
    df["買付価格"] = -df[df["売買価格"] < 0]["売買価格"]
    df["売却価格"] = df[df["売買価格"] > 0]["売買価格"]

    df = df.sort_values(by=["銘柄", "日時"])
    df["保有数"] = df.groupby("銘柄")["約定数"].cumsum()

    ##### 平均単価計算
    df["平均単価"] = df.apply(running_mean, axis=1) # should be fixed for each=True
    df["実現損益"] = df["売却価格"]+df["平均単価"]*df["約定数"]

    ##### formatting data
    columns = ["銘柄", "取引所", "ID", "日時", "売買", "売買価格", "単価", "約定数", "保有数", "買付価格", "売却価格", "平均単価", "実現損益"]
    df = df.reindex(columns=columns).reset_index()
    return(df)

def get_each_profit(df):
    df_group = df.sort_values(by=["取引所", "銘柄", "日時"]).groupby(["取引所","銘柄"])
    df2=df_group[["売買価格","約定数","実現損益"]].sum()

#    df2.drop(index='JPY')
    df2["平均単価"]=df_group.last()["平均単価"]
    df2["購入額"]=df2["約定数"]*df2["平均単価"]
    return df2

####### main routing #######
pd.set_option('display.max_columns', 50)


# if (sys.argv[-1]==sys.argv[0]):
#     print('Usage: {} <file name>'.format(sys.argv[0]))

# try:
#     df = pd.read_csv(sys.argv[-1],encoding="UTF-8")
# except FileNotFoundError:
#     print('Error: File not found.')

if (sys.argv[-1]==sys.argv[0]):
    print('Usage: {} <dir name>'.format(sys.argv[0]))

dir = Path(sys.argv[-1])

df = pd.DataFrame()
#df = (pd.read_csv(f) for f in dir.glob("*.csv"))
for f in dir.glob("*.csv"):
    newdf=pd.read_csv(f)

    if '注文ID' in newdf.columns:
        GMO_data(newdf)
    else:
        CC_data(newdf)

    df=df.append(newdf, ignore_index=True)

df=get_profit(df)
#display(df.head())
df.to_csv("crypt-history.csv")

# print some results
#pd.options.display.float_format = '{:,.0f}'.format
print("===実現損益=================")
print(df.groupby("銘柄")[["実現損益","約定数"]].sum().drop(index='JPY') )

print("===実現損益(合計)============")
print("合計: {:,.0f} JPY ".format(df["実現損益"].sum()))

df2=get_profit_each(df)
print("===残金====================")
print(df2.groupby("取引所")[["売買価格"]].sum())

df2.to_csv("crypt-summary.csv")


