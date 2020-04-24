from gym.envs.registration import register
from copy import deepcopy

from . import datasets

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


def register_new(stock_code,main_column='close'):
    dataset = datasets.load_dataset_online(stock_code)
    env_id = 'stocks-v0-{}'.format(stock_code)
    print(env_id)
    register(
        id=env_id,
        entry_point='gym_anytrading.envs:StocksEnv',
        kwargs={
            'df': deepcopy(dataset),
            'window_size': 30,
            'frame_bound': (30, len(dataset)),
            'main_column': main_column,
        }
    )
