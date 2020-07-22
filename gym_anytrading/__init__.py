from gym.envs.registration import register
from copy import deepcopy
from . import datasets
import datetime

register(
    id='forex-v0',
    entry_point='gym_anytrading.envs:ForexEnv',
    kwargs={
        'df': deepcopy(datasets.FOREX_EURUSD_1H_ASK),
        'window_size': 24,
        'frame_bound': (24, len(datasets.FOREX_EURUSD_1H_ASK))
    }
)

register(
    id='stocks-v0',
    entry_point='gym_anytrading.envs:StocksEnv',
    kwargs={
        'df': deepcopy(datasets.STOCKS_GOOGL),
        'window_size': 30,
        'frame_bound': (30, len(datasets.STOCKS_GOOGL))
    }
)

def register_new(
        stock_code,
        start_date='2017-01-01',
        end_date=datetime.datetime.now().strftime("%Y-%m-%d")
):
    dataset = datasets.load_dataset_online(stock_code,start_date=start_date,end_date=end_date)
    # env_id = 'stocks-v1'.format(stock_code)
    env_id = 'stocks-v1'
    print(env_id)
    register(
        id=env_id,
        entry_point='gym_anytrading.envs:StocksEnv',
        kwargs={
            'df': deepcopy(dataset),
            'window_size': 30,
            'frame_bound': (30, len(dataset)),
            # 'main_column': main_column,
        }
    )



def register_new_kzz(
        stock_code,
        start_date='2017-01-01',
        end_date=datetime.datetime.now().strftime("%Y-%m-%d")
):
    dataset = datasets.get_kzz_miniute(stock_code)
    # env_id = 'stocks-v1'.format(stock_code)
    env_id = 'kzz-v1'
    print(env_id)
    register(
        id=env_id,
        entry_point='gym_anytrading.envs:StocksEnv',
        kwargs={
            'df': deepcopy(dataset),
            'window_size': 30,
            'frame_bound': (30, len(dataset)),
            # 'main_column': main_column,
        }
    )
