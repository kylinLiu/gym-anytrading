import pandas as pd
import numpy as np

# from .trading_env import TradingEnv, Actions, Positions
from .trading_env import TradingEnv, Actions


class StocksEnv(TradingEnv):
    def __init__(self, df, window_size, frame_bound):
        assert len(frame_bound) == 2

        self.frame_bound = frame_bound
        super().__init__(df, window_size)

        # self.trade_fee_bid_percent = 0.01  # unit
        # self.trade_fee_ask_percent = 0.005  # unit
        self.trade_fee_percent = 0.0005

        # def _process_data(self):
        #     prices = self.df.loc[:, self.main_column].to_numpy(dtype = 'float')
        #
        #     prices[self.frame_bound[0] - self.window_size]  # validate index (TODO: Improve validation)

        #     prices = prices[self.frame_bound[0] - self.window_size:self.frame_bound[1]]
        #
        #     #         diff = np.insert(np.diff(prices), 0, 0)
        #     #         signal_features = np.column_stack((prices, diff))
        #
        #     #         return prices, signal_features
        #     # 把计算差值改成计算涨跌幅
        #     # 或者可以考虑对价格做正态分布np.log(prices)
        #     pct = (prices[1:] - prices[:-1]) / prices[:-1]
        #     pct = np.insert(pct, 0, 0)
        #     signal_features = np.column_stack((prices, pct))
        #     return prices, signal_features
        # return prices

    def _process_data(self, column_list = None):
        prices = self.df.loc[:, self.main_column].to_numpy(dtype='float')

        # prices[self.frame_bound[0] - self.window_size]  # validate index (TODO: Improve validation)
        prices = prices[self.frame_bound[0] - self.window_size:self.frame_bound[1]]

        #         diff = np.insert(np.diff(prices), 0, 0)
        #         signal_features = np.column_stack((prices, diff))

        #         return prices, signal_features
        # 把计算差值改成计算涨跌幅
        # 或者可以考虑对价格做正态分布np.log(prices)
        # pct = (prices[1:] - prices[:-1]) / prices[:-1]
        # pct = np.insert(pct, 0, 0)
        # signal_features = np.column_stack((prices, pct))
        if column_list:
            signal_features = self.df.loc[:, column_list].apply(pd.to_numeric, errors='coerce').fillna(0.0).to_numpy(
                dtype='float')
        else:
            self.df.apply(pd.to_numeric, errors='coerce').fillna(0.0).to_numpy(
                dtype='float')
        # signal_features = pd.DataFrame(signal_features, dtype=np.float)
        signal_features = signal_features[self.frame_bound[0] - self.window_size:self.frame_bound[1]]
        return prices, signal_features
        # return prices

    def _calculate_reward_old(self, action):
        step_reward = 0

        # trade = False
        # if ((action == Actions.Buy.value) or
        #         (action == Actions.Sell.value) or
        #         (action == Actions.Hold.value)):
        #     trade = True
        # print("action", action)

        current_price = self.prices[self._current_tick]
        # profile = ((self.max_price + self.min_price) - 2.0) / current_price
        # loss = (2.0 - (self.max_price + self.min_price)) / current_price
        # 如果是买入，取前取10期，获取最低价，计算损失（应该在最低价买入）A
        # 往取后取60期，取最小值、最大值，分别算最大回测B和最大收益C（）
        # 总收益 =  (C - B - A)/current_price

        # 如果是卖出，获取取10期，获取最高价，计算损失（应该在最低价买入）A
        # 往取后取60期，取最小值、最大值，分别算最大回测B和最大收益C（）
        # 总收益 =  (C - B - A)/current_price

        # 如果是买入，取前取10期，获取最低价，计算损失（应该在最低价买入）A
        # 往取后取60期，取最小值、最大值，分别算最大回测B和最大收益C（）
        # 总收益 =  (C - B - A)/current_price
        if action == Actions.Sell.value:
            current_price = self.prices[self._current_tick]
            _last_buy_tick = self.buy_queue[-1]
            self.buy_queue = self.buy_queue[:-1]
            last_trade_price = self.prices[_last_buy_tick]
            price_diff = current_price - last_trade_price
            # 修改收益为涨跌幅，而不是用差价
            price_pct = (current_price - last_trade_price) / last_trade_price

            # if self._position == Positions.Long:
            step_reward = (price_pct - 2 * self.trade_fee_percent)
            # print("step_reward XXXXXXXXXXXXXXXX", step_reward)

            # print("calcu step_reward ", self._current_tick, self._last_trade_tick, step_reward)
        return step_reward

    def _calculate_reward(self, action):
        step_reward = 0

        # trade = False
        # if ((action == Actions.Buy.value) or
        #         (action == Actions.Sell.value) or
        #         (action == Actions.Hold.value)):
        #     trade = True
        # print("action", action)
        start = self._current_tick - 30
        start = start if start >= 0 else 0
        end = start + 60
        current_price = self.prices[self._current_tick]
        prices = self.prices[start:end]
        max_price, min_price = prices.max(), prices.min()

        profile = ((max_price + min_price) - 2.0) / current_price
        loss = (2.0 - (max_price + min_price)) / current_price
        # 如果是买入，取前取10期，获取最低价，计算损失（应该在最低价买入）A
        # 往取后取60期，取最小值、最大值，分别算最大回测B和最大收益C（）
        # 总收益 =  (C - B - A)/current_price

        # 如果是卖出，获取取10期，获取最高价，计算损失（应该在最低价买入）A
        # 往取后取60期，取最小值、最大值，分别算最大回测B和最大收益C（）
        # 总收益 =  (C - B - A)/current_price

        # 如果是买入，取前取10期，获取最低价，计算损失（应该在最低价买入）A
        # 往取后取60期，取最小值、最大值，分别算最大回测B和最大收益C（）
        # 总收益 =  (C - B - A)/current_price
        if (
                        action == Actions.Buy.value
                or
                        action == Actions.Hold.value
        ):
            step_reward = profile

        if action == Actions.Sell.value:
            self.buy_queue = self.buy_queue[:-1]
            step_reward = loss
        if action == Actions.Watch.value:
            step_reward = loss
            # current_price = self.prices[self._current_tick]
            # _last_buy_tick = self.buy_queue[-1]
            # self.buy_queue = self.buy_queue[:-1]
            # last_trade_price = self.prices[_last_buy_tick]
            # price_diff = current_price - last_trade_price
            # # 修改收益为涨跌幅，而不是用差价
            # price_pct = (current_price - last_trade_price) / last_trade_price
            #
            # # if self._position == Positions.Long:
            # step_reward = (price_pct - 2 * self.trade_fee_percent)
            # print("step_reward XXXXXXXXXXXXXXXX", step_reward)

            # print("calcu step_reward ", self._current_tick, self._last_trade_tick, step_reward)
        return step_reward

    def _update_profit(self, action):
        trade = False
        # if ((action == Actions.Buy.value) or
        #         (action == Actions.Sell.value) or
        #         (action == Actions.Hold.value)):
        #     trade = True

        # if trade or self._done:
        # print(len(self.prices), self._current_tick)

        current_price = self.prices[self._current_tick]
        self.prices[self._current_tick]
        if (action == Actions.Sell.value) or (action == Actions.Buy.value):
            self._total_profit += current_price * self.trade_fee_percent
            # current_price = self.prices[self._current_tick]
            # last_trade_price = self.prices[self._last_trade_tick]
            #
            # # if self._position == Positions.Long:
            # shares = (self._total_profit * (1 - self.trade_fee_ask_percent)) / last_trade_price
            # self._total_profit = (shares * (1 - self.trade_fee_bid_percent)) * current_price

    def max_possible_profit(self):
        current_tick = self._start_tick
        last_trade_tick = current_tick - 1
        profit = 1.

        while current_tick <= self._end_tick:
            # position = None
            if self.prices[current_tick] < self.prices[current_tick - 1]:
                while (current_tick <= self._end_tick and
                               self.prices[current_tick] < self.prices[current_tick - 1]):
                    current_tick += 1
                    # position = Positions.Short
            else:
                while (current_tick <= self._end_tick and
                               self.prices[current_tick] >= self.prices[current_tick - 1]):
                    current_tick += 1
                    # position = Positions.Long

            # if position == Positions.Long:
            current_price = self.prices[current_tick - 1]
            last_trade_price = self.prices[last_trade_tick]
            shares = profit / last_trade_price
            profit = shares * current_price
            last_trade_tick = current_tick - 1

        return profit
