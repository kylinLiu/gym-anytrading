import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
from enum import Enum
import matplotlib.pyplot as plt

# import queue
# from torch.multiprocessing import Queue

"""
_get_observation:pct,reward:pct episodes:50 max_score:  4.65
                                        +50             2.95

"""


class Actions(Enum):
    '''
    行为空间，增加Hold(持有)和Watch(观望)两个行为
    '''
    Sell = 0
    Buy = 1
    Hold = 2
    Watch = 3


# 废弃Position对象
# class Positions(Enum):
#     Short = 0
#     Long = 1

#     def opposite(self):
#         return Positions.Short if self == Positions.Long else Positions.Long


class TradingEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, df, window_size):
        print("_init_enviroment")
        assert df.ndim == 2
        self._max_episode_steps = 100
        self.seed()
        self.df = df
        print(df.shape)
        self.trials = 10
        self.window_size = window_size
        self.main_column = 'close'
        self.prices, self.signal_features = self._process_data()
        # print("signal_features", self.signal_features)
        # print("signal_features_shape", self.signal_features.shape)
        self.shape = (window_size, self.signal_features.shape[1])
        print("shape", self.shape)

        # spaces
        self.action_space = spaces.Discrete(len(Actions))
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self.shape, dtype=np.float32)
        print("observation_space", self.shape)

        # episode
        self._start_tick = self.window_size
        self._end_tick = len(self.prices) - 1
        print("len self._end_tick", self._end_tick)
        self._done = None
        self._current_tick = None
        # self._last_trade_tick = None
        self._position = None
        self._action = None
        self._position_history = None
        self._total_reward = None
        self._total_profit = None
        self._first_rendering = None

    def update_df(self, fn):
        '''更新df'''
        self.df = fn(self.df)
        self.prices, self.signal_features = self._process_data()
        self.shape = (self.window_size, self.signal_features.shape[1])
        print("shape", self.shape)

        # spaces
        self.action_space = spaces.Discrete(len(Actions))
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self.shape, dtype=np.float32)
        print("observation_space", self.shape)
        self._end_tick = len(self.prices) - 1

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def reset(self):

        self.pre_observation = None
        self.pre_step_reward = None
        self.pre_done = None
        self.pre_info = None
        # self.buy_queue = queue.LifoQueue()
        # self.buy_queue = Queue()
        self.buy_queue = []
        self._done = False
        # self._current_tick = self._start_tick - 1
        # self._last_trade_tick = self._current_tick
        # # self._position = Positions.Short
        # self._position_history = (self.window_size * [None])
        # + [self._position]


        self._current_tick = self._start_tick
        # self._last_trade_tick = self._current_tick - 1
        # self._position = Positions.Short
        # self._position = Positions.Long
        # self._position_history = (self.window_size * [None]) + [self._position]
        self._position_history = (self.window_size * [None])

        print("id", self)
        print("_position_history", self._position_history)

        self._total_reward = 0.
        self._total_profit = 1.  # unit
        self._first_rendering = True
        print("self._current_tick - self.window_size", self._current_tick, self.window_size)
        return self._get_observation()

    def step(self, action):
        # 争议点,如果有持仓而且action是Watch,Watch为无效行为，
        # 措施 （目前 1 ）：
        # 1.action强制转为Hold
        # 2.直接返回状态，reward怎么计算？
        if self.buy_queue and action == Actions.Watch.value:
            action = Actions.Hold.value

        # 争议点,如果无持仓而且action是Hold,Hold为无效行为，
        # 措施 （目前 1 ）：
        # 1.action强制转为Buy
        # 2.直接返回状态，reward怎么计算？
        if not self.buy_queue and action == Actions.Hold.value:
            action = Actions.Buy.value

        # 争议点,如果无持仓而且action是Sell,Sell为无效行为，
        # 措施 （目前 1 ）：
        # 1.action强制转为Watch
        # 2.直接返回状态，reward怎么计算？
        if not self.buy_queue and action == Actions.Sell.value:
            action = Actions.Watch.value

        self._action = action
        self._done = False
        # self._last_trade_tick = self._current_tick

        if self._current_tick == self._end_tick:
            self._done = True

        step_reward = self._calculate_reward(action)
        self._total_reward += step_reward

        self._update_profit(action)

        # trade = False
        if action == Actions.Buy.value:
            self.buy_queue.append(self._current_tick)
            # trade = True

        self._position_history.append(action)
        self._current_tick += 1
        observation = self._get_observation()
        info = dict(
            total_reward=self._total_reward,
            total_profit=self._total_profit,
            # position=self._position.value
        )
        self.pre_observation = observation
        self.pre_step_reward = step_reward
        self.pre_done = self._done
        self.pre_info = info

        return observation, step_reward, self._done, info

    def _get_observation(self):
        #         return self.signal_features[(self._current_tick-self.window_size):self._current_tick][:,0]
        # return self.signal_features[(self._current_tick - self.window_size):self._current_tick][:, 1]
        return self.signal_features[(self._current_tick - self.window_size):self._current_tick].reshape(-1,1)

    def render(self, mode='human'):

        def _plot_position(action, tick):
            color = None
            if action == Actions.Buy:
                color = 'red'
            elif action == Actions.Sell:
                color = 'green'
            elif action == Actions.Hold:
                color = 'blue'
            elif action == Actions.Watch:
                color = 'yellow'
            if color:
                plt.scatter(tick, self.prices[tick], color=color)

        if self._first_rendering:
            self._first_rendering = False
            plt.cla()
            plt.plot(self.prices)
            start_action = self._position_history[self._start_tick]
            _plot_position(start_action, self._start_tick)

        _plot_position(self._action, self._current_tick)

        plt.suptitle(
            "Total Reward: %.6f" % self._total_reward + ' ~ ' +
            "Total Profit: %.6f" % self._total_profit
        )

        plt.pause(0.01)

    def render_all(self, mode='human'):
        window_ticks = np.arange(len(self.prices))
        plt.plot(self.prices)
        # print(self._position_history)
        buy_ticks = []
        sell_ticks = []
        hold_ticks = []
        watch_ticks = []
        # print(len(window_ticks))
        print(self._position_history)
        print("window_ticks:_position_history", window_ticks, len(self._position_history))
        for i, tick in enumerate(window_ticks):
            # print(self._position_history[i], Actions.Hold)
            if self._position_history[i] == Actions.Buy.value:
                buy_ticks.append(tick)
            elif self._position_history[i] == Actions.Sell.value:
                sell_ticks.append(tick)
            elif self._position_history[i] == Actions.Hold.value:
                hold_ticks.append(tick)
            elif self._position_history[i] == Actions.Watch.value:
                watch_ticks.append(tick)

        plt.plot(buy_ticks, self.prices[buy_ticks], 'ro')
        plt.plot(sell_ticks, self.prices[sell_ticks], 'go')
        # plt.plot(hold_ticks, self.prices[hold_ticks], 'bo')
        # plt.plot(watch_ticks, self.prices[watch_ticks], 'yo')

        plt.suptitle(
            "Total Reward: %.6f" % self._total_reward + ' ~ ' +
            "Total Profit: %.6f" % self._total_profit
        )

    def save_rendering(self, filepath):
        plt.savefig(filepath)

    def pause_rendering(self):
        plt.show()

    def _process_data(self):
        raise NotImplementedError

    def _calculate_reward(self, action):
        raise NotImplementedError

    def _update_profit(self, action):
        raise NotImplementedError

    def max_possible_profit(self):  # trade fees are ignored
        raise NotImplementedError
