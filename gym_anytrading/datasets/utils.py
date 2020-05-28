import os
import baostock as bs
import pandas as pd
import datetime
import numpy as np


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
