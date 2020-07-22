import os
import baostock as bs
import pandas as pd
import datetime
import numpy as np
import requests
import json


def load_dataset(name, index_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, 'data', name + '.csv')
    return pd.read_csv(path, index_col=index_name)


def load_dataset_online(
        stock_code,
        csv_filename='',
        index_name='date',
        file_first=False,
        start_date='2017-01-01',
        end_date=datetime.datetime.now().strftime("%Y-%m-%d")
):
    '''

    :param stock_code: eg:'sz.000001'
    :param csv_filename: eg: 'xxx',''
    :param index_name: eg:'Date','Time','Date Tiime'
    :return:
    '''

    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = ''
    if csv_filename:
        path = os.path.join(base_dir, 'data', csv_filename + '.csv')
    if path and os.path.isfile(path) and file_first:
        return pd.read_csv(path, index_col=index_name)

    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    rs = bs.query_history_k_data_plus(
        stock_code,
        "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
        start_date=start_date, end_date=end_date,
        frequency="d", adjustflag="3"
    )
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    result.set_index([index_name, ], inplace=True)

    if path:
        #### 结果集输出到csv文件 ####
        result.to_csv(path, index_label=True)
    print(result)

    #### 登出系统 ####
    bs.logout()
    return result




def get_kzz_miniute(symbol):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        "Cookie": "xq_a_token=ad923af9f68bb6a13ada0962232589cea11925c4; xqat=ad923af9f68bb6a13ada0962232589cea11925c4; xq_r_token=cf0e6f767c2318f1f1779fcee9323365f02e1b4b; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTU5NjE2MjgxNSwiY3RtIjoxNTk1MDYyOTQ2ODk2LCJjaWQiOiJkOWQwbjRBWnVwIn0.FjdGzZN_iktMuEHXI7FSPvC5AJsPLU7B9el4df2viDkynNkefJILViljyWyjjWDY3TAzh0TAE2ZjcWFax43B5-CG_XewUULyle5ipYZDUyehY84keDH0FY-RaEzmkcJ-aJsV0is8n5IeOBxEbRND3x7NNNDjdqHepPOwxcfYAWI2KwcuSsx9NLQzGGB8iqE-GtEn7M0S3RlHAZHxpIh50vJlsjAMmUzhrd5IwxcgwfBLhpI_O2tHTKtUyBgNDCHqh_GUdYDSk-_S6FcjkfB_xD1mSJzclU1QFzsJHdjt3xwoK9N5XHwK5cRu2fat4W4EqRjAqjJa8m_2-HEefVI42g; u=811595062999370; Hm_lvt_1db88642e346389874251b5a1eded6e3=1595060107; device_id=3d677af1cbb51499f019102e60235e10; is_overseas=0; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1595063449",
        'Origin': 'https://xueqiu.com',
        'Referer': 'https://xueqiu.com/S/{}'.format(symbol),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
    }

    url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={}&begin=1595252465764&period=1m&type=before&count=-284&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance".format(
        symbol, '1594949400000')

    # coding:utf-8
    # import requests

    #
    # for url in ["https://xueqiu.com", "https://xueqiu.com/S/SH113566"]:
    #     r = requests.get(url)
    #     headers = r.headers
    #     for k, v in headers.items():
    #         print(k, v)
    #
    # """
    # aliyungf_tc=AQAAAIH/+2ygvwAA9sn43s3aKjALArSJ;
    # acw_tc=2760824b15950629200605825eb999f3e4f540d36fab5ff5d4e5e321f62866;
    #
    # """
    r = requests.get(url, headers=headers)
    datas = r.text
    datas = json.loads(datas)
    datas = datas.get("data", {}).get("item", [])
    data_list = []
    for index, row in enumerate(datas):
        close_diff = 0
        volumn_diff = 0
        volumn_chng = 0
        if index:
            close_diff = row[5] - datas[index - 1][5]
            volumn_diff = row[1] - datas[index - 1][1]
            if datas[index - 1][1]:
                volumn_chng = (row[1] - datas[index - 1][1]) / datas[index - 1][1]
        data_list.append(
            {
                "volume": row[1],
                "close_diff": close_diff,
                "volumn_diff": volumn_diff,
                "volumn_chng": volumn_chng,
                "close": row[5],
                "volumne": row[1],
                "chg": row[6],
                "date": datetime.datetime.fromtimestamp(row[0] / 1000).strftime("%H:%M"),
            }
        )

    pre_ema_12 = None
    pre_ema_26 = None
    pre_dif = None
    pre_dea = None
    pre_macd = None
    pre_macd_chng_pct = None

    def calcute_rsi(data_list):
        a = sum([i["close_diff"] for i in data_list if i["close_diff"] > 0])
        b = abs(sum([i["close_diff"] for i in data_list if i["close_diff"] < 0]))

        rsi = a / (a + b) * 100
        return rsi

    # data_list = data_list[-263:]
    print(len(data_list))
    for index, row in enumerate(data_list):
        rsi6 = None
        rsi12 = None
        rsi24 = None
        if index >= 5:
            rsi6_list = data_list[(index + 1) - 6:index + 1]
            rsi6 = calcute_rsi(rsi6_list)
        if index >= 11:
            rsi12_list = data_list[(index + 1) - 12:index + 1]
            rsi12 = calcute_rsi(rsi12_list)
        if index >= 23:
            rsi24_list = data_list[(index + 1) - 24:index + 1]
            rsi24 = calcute_rsi(rsi24_list)

        tclose = row["close"]
        if pre_ema_12 is None:
            ema_12 = tclose
        else:
            ema_12 = pre_ema_12 * (11.0 / 13) + tclose * (2.0 / 13)
        if pre_ema_26 is None:
            ema_26 = row["close"]
        else:
            ema_26 = pre_ema_26 * (25.0 / 27) + tclose * (2.0 / 27)
        dif = ema_12 - ema_26
        if pre_dea is None:
            dea = 0
        else:
            dea = pre_dea * (8.0 / 10) + (2.0 / 10) * dif
        macd = 2 * (dif - dea)
        dif_cross_dea_above = False
        dif_cross_dea_below = False
        if pre_dif is not None and pre_dea is not None \
                and dif is not None and dea is not None:
            if pre_dif < pre_dea and dif > dea:
                dif_cross_dea_above = True
            if pre_dif > pre_dea and dif < dea:
                dif_cross_dea_below = True
        macd_chng_pct = 0
        if pre_macd:
            macd_chng_pct = 1.0 * (macd - pre_macd) / abs(pre_macd)
        dea_chng_pct = 0
        if pre_dea:
            dea_chng_pct = (dea - pre_dea) / abs(pre_dea)
        dif_chng_pct = 0
        if pre_dif:
            dif_chng_pct = (dif - pre_dif) / abs(pre_dif)

        row.update({
            "dif": dif,
            "pre_dif": pre_dif,
            "dea": dea,
            "pre_dea": pre_dea,
            "ema_12": ema_12,
            "ema_26": ema_26,
            "macd": macd,
            "pre_macd": pre_macd,
            "dif_cross_dea_above": dif_cross_dea_above,
            "dif_cross_dea_below": dif_cross_dea_below,
            "pre_macd_chng_pct": pre_macd_chng_pct,
            "macd_chng_pct": macd_chng_pct,
            "dea_chng_pct": dea_chng_pct,
            "dif_chng_pct": dif_chng_pct,
            "rsi6": rsi6,
            "rsi12": rsi12,
            "rsi24": rsi24,
        })
        pre_ema_12 = ema_12
        pre_ema_26 = ema_26
        pre_dif = dif
        pre_dea = dea
        pre_macd = macd
        pre_macd_chng_pct = macd_chng_pct
    # print(len(buy_list))
    # raise Exception(22)
    buy_list = {'x': [], 'y': []}
    data_list = data_list[24:]
    # print(data_list[0])
    for index, row in enumerate(data_list):
        pre_macd_chng_pct = row["pre_macd_chng_pct"]
        macd_chng_pct = row["macd_chng_pct"]
        macd = row["macd"]
        dea = row["dea"]
        dif = row["dif"]
        dea_chng_pct = row["dea_chng_pct"]
        dif_chng_pct = row["dif_chng_pct"]
        rsi6 = row["rsi6"]
        rsi12 = row["rsi12"]
        rsi24 = row["rsi24"]
        chg = row["chg"]
        volumn_chng = row["volumn_chng"]
        # print(row["date"], pre_macd_chng_pct, macd_chng_pct)
        if (pre_macd_chng_pct < 0 and macd_chng_pct > 0 and macd < 0
            and dea < 0 and dif < 0
            and dea_chng_pct < 0
            and rsi6 < 50 and rsi12 < 50 and rsi24 < 50
            and dea > dif
            and chg > 0
            and dea - dif > 0.1
            and volumn_chng > 0.1
            and rsi24 > rsi12 and rsi24 > rsi6
            ):
            # and rsi6 < rsi12 and rsi12 < rsi24:
            #  and dif_chng_pct < 0:
            # and dif_chng_pct > dea_chng_pct:
            # and dif_chng_pct > 0 and dea_chng_pct < 0:
            # and macd < -0.1:
            buy_list["y"].append(row["close"])
            buy_list["x"].append(index)
    df = pd.DataFrame(data_list)
    print(df.columns)
    print(df)
    return df


if __name__ == "__main__":
    result = load_dataset_online("sz.000002")
    a = result.loc[:, "close"].to_numpy(dtype='float')
    # b = result.loc[:, ["close"]].to_numpy(dtype='float')
    b = result.loc[:, ["close", "pctChg"]].apply(pd.to_numeric, errors='coerce').fillna(0.0).to_numpy(
        dtype='float').reshape(-1)
    # print(.convert_objects(convert_numeric=True))
    # xx = result.loc[:, ["pctChg", "turn"]]
    # xx = pd.DataFrame(xx, dtype=np.float)
    # print(xx.info())
    # print(result["pctChg"].dtype)
    # print(result.loc[:, "turn"].dtype)
    # print(result.info())
    print(a.shape, b.shape)
