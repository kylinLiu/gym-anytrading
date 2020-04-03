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

    def _process_data(self):
        prices = self.df.loc[:, 'Close'].to_numpy()

        prices[self.frame_bound[0] - self.window_size]  # validate index (TODO: Improve validation)
        prices = prices[self.frame_bound[0] - self.window_size:self.frame_bound[1]]

        #         diff = np.insert(np.diff(prices), 0, 0)
        #         signal_features = np.column_stack((prices, diff))

        #         return prices, signal_features
        # 把计算差值改成计算涨跌幅
        # 或者可以考虑对价格做正态分布np.log(prices)
        pct = (prices[1:] - prices[:-1]) / prices[:-1]
        pct = np.insert(pct, 0, 0)
        signal_features = np.column_stack((prices, pct))
        return prices, signal_features
        # return prices

    def _calculate_reward(self, action):
        step_reward = 0

        # trade = False
        # if ((action == Actions.Buy.value) or
        #         (action == Actions.Sell.value) or
        #         (action == Actions.Hold.value)):
        #     trade = True

        if action == Actions.Sell.value:
            current_price = self.prices[self._current_tick]
            _last_buy_tick = self.buy_queue.get(timeout=1)
            last_trade_price = self.prices[_last_buy_tick]
            price_diff = current_price - last_trade_price
            # 修改收益为涨跌幅，而不是用差价
            # price_pct = (current_price - last_trade_price) / last_trade_price

            # if self._position == Positions.Long:
            step_reward += price_diff

            # print("calcu step_reward ", self._current_tick, self._last_trade_tick, step_reward)
        return step_reward

    def _update_profit(self, action):
        trade = False
        # if ((action == Actions.Buy.value) or
        #         (action == Actions.Sell.value) or
        #         (action == Actions.Hold.value)):
        #     trade = True

        # if trade or self._done:
        current_price = self.prices[self._current_tick]
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
