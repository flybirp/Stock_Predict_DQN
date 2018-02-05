from random import random
import numpy as np
import math

import gym
from gym import spaces


class MarketEnv(gym.Env):
    PENALTY = 0.9987

    def __init__(self, dir_path, target_codes, start_date, end_date, scope=60, sudden_death_rate=0.5, current_asset = {'cash':100000, 'stock':0}):
        self.startDate = start_date
        self.endDate = end_date
        # scope, minimum size of dates in record
        self.scope = scope
        self.sudden_death_rate = sudden_death_rate
        self.current_asset = current_asset
        self.startAssetValue = current_asset['cash']
        self.targetCodes = []
        self.dataMap = {}

        for code in (target_codes):
            fn = dir_path + "./" + code + ".csv"

            data = {}
            lastClose = 0
            lastVolume = 0
            lastDate = 0
            try:
                print fn
                f = open(fn, "r")
                for line in f:
                    if line.strip() != "":
                        dt, openPrice, high, low, close, volume = line.strip().split(",")
                        try:
                            if dt >= start_date:
                                high = float(high) if high != "" else float(close)
                                low = float(low) if low != "" else float(close)
                                openPrice = float(openPrice)
                                close = float(close)
                                volume = float(volume)
                                trading_price = (low+high+close)/3
                                date = self.convertDate(dt)

                                if lastClose > 0 and close > 0 and lastVolume > 0 and lastDate > 0:
                                    close_ = (close - lastClose) / lastClose
                                    high_ = (high - close) / close
                                    low_ = (low - close) / close
                                    volume_ = (volume - lastVolume) / lastVolume
                                    date_ = (date - lastDate) / lastDate
                                    open_ = (openPrice - close) /close
                                    data[dt] = (date_, high_, low_, close_, volume_, trading_price, open_)

                                lastClose = close
                                lastVolume = volume
                                lastDate = date

                        except Exception, e:
                            print e, line.strip().split(",")
                f.close()
            except Exception, e:
                print e

            if len(data.keys()) > scope:
                self.dataMap[code] = data
                if code in target_codes:
                    self.targetCodes.append(code)


        self.actions = [
            "Buy",
            "Sell",
            "Hold",
        ]

        self.action_space = spaces.Discrete(len(self.actions))
        self.observation_space = spaces.Box(np.ones(scope * (1)) * -1,
                                            np.ones(scope * (1)))

        self.reset()
        self._seed()

    def convertDate(self, date):
        date = date.split('-')
        date = date[1] + '.' + date[2]
        date = float(date)
        return date

    def _step(self, action):
        if self.done:
            return self.state, self.reward, self.done, {}

        last_asset_value = float(self.current_asset['stock']) * float(self.target[self.targetDates[self.currentTargetIndex]][5])\
                           + float(self.current_asset['cash'])

        current_trading_price = self.target[self.targetDates[self.currentTargetIndex]][5]


        if self.actions[action] == "Buy":
            cur_stock = self.current_asset['stock']
            self.current_asset['stock'] = round( (float(self.current_asset['cash']) / float(current_trading_price) + cur_stock), 3)
            self.current_asset['cash'] = round(float(0), 3)

        elif self.actions[action] == "Sell":
            cur_cash = float(self.current_asset['cash'])
            self.current_asset['cash'] = round( (float(self.current_asset['stock']) * float(current_trading_price) + cur_cash) , 3)
            self.current_asset['stock'] = round(float(0), 3)

        elif self.actions[action] == "Hold":
            pass
        else:
            pass

        self.defineState()
        self.currentTargetIndex += 1

        if self.current_asset['cash'] > 0:
            self.current_asset['cash'] = self.current_asset['cash'] - (10+ random() * 3)


        current_asset_value = round(((float(self.current_asset['stock']) * float(self.target[self.targetDates[self.currentTargetIndex]][5])) + float(self.current_asset['cash'])), 3)

        if self.currentTargetIndex >= len(self.targetDates)\
                or self.endDate <= self.targetDates[self.currentTargetIndex]\
                or current_asset_value < float(self.sudden_death_rate * self.startAssetValue):
            self.done = True

        self.reward = current_asset_value - last_asset_value


        return self.state, self.reward, self.done, \
               {"date": self.targetDates[self.currentTargetIndex],"code": self.targetCode,
                "current_asset_value":("%.2f" % current_asset_value), "cur_reward":("%.2f" % self.reward),
                "act":self.actions[action], "asset":self.current_asset}


    def _reset(self):
        self.current_asset = {'cash':100000, 'stock':0}
        self.startAssetValue = 100000

        self.targetCode = self.targetCodes[int(random() * len(self.targetCodes))]

        self.target = self.dataMap[self.targetCode]

        self.targetDates = sorted(self.target.keys())

        self.currentTargetIndex = self.scope

        self.done = False
        self.reward = 0

        self.defineState()

        return self.state


    def _render(self, mode='human', close=False):
        if close:
            return
        return self.state


    def _seed(self):
        return int(random() * 100)



    def defineState(self):
        tmpState = []

        current_trading_price = self.target[self.targetDates[self.currentTargetIndex]][5]

        cashProfile = 1 + (float(self.current_asset['cash']) / float(self.startAssetValue))
        stockProfile = 1 + (float(self.current_asset['stock']) * float(current_trading_price) / float(self.startAssetValue))
        tmpState.append([[cashProfile, stockProfile]])

        subjectDate = []
        subjectHigh = []
        subjectLow = []
        subjectClose = []
        subjectVolume = []
        subjectTradingPrice = []
        subjectOpen = []

        for i in xrange(self.scope):
            try:
                subjectDate.append([self.target[self.targetDates[self.currentTargetIndex - 1 - i]][0]])  # date
                subjectHigh.append([self.target[self.targetDates[self.currentTargetIndex - 1 - i]][1]]) #high
                subjectLow.append([self.target[self.targetDates[self.currentTargetIndex - 1 - i]][2]]) #low
                subjectClose.append([self.target[self.targetDates[self.currentTargetIndex - 1 - i]][3]]) #close
                subjectVolume.append([self.target[self.targetDates[self.currentTargetIndex - 1 - i]][4]]) #volume
                subjectTradingPrice.append([self.target[self.targetDates[self.currentTargetIndex - 1 - i]][5]])  # trading price
                subjectOpen.append([self.target[self.targetDates[self.currentTargetIndex - 1 - i]][6]])  # date

            except Exception, e:
                print 'error in market_env.defineState'
                print self.targetCode, self.currentTargetIndex, i, len(self.targetDates)
                self.done = True

        tmpState.append([[subjectDate, subjectHigh, subjectLow, subjectClose, subjectVolume, subjectTradingPrice, subjectOpen]])

        tmpState = [np.array(i) for i in tmpState]

        self.state = tmpState











