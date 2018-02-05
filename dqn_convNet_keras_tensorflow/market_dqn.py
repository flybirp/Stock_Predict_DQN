import os
import numpy as np
import copy
from market_env import MarketEnv
from market_model_builder import MarketDeepQLearningModelBuilder
from collections import deque


class DeepQ:

    def __init__(self, env, current_discount=0.85, future_discount=0.85, model_file_name=None):
        self.env = env
        self.discount = future_discount
        self.cur_discount = current_discount
        self.model_filename = model_file_name
        self.memory = deque(maxlen=100000)
        self.epsilon = 1.  # exploration rate
        self.epsilon_decay = .98
        self.epsilon_min = 0.005


        from keras.optimizers import RMSprop
        self.model = MarketDeepQLearningModelBuilder().buildModel()

        rmsprop = RMSprop(lr=0.0001)
        self.model.compile(loss='mse', optimizer=rmsprop)


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))


    def replay(self, batch_size):
        batchs = min(batch_size, len(self.memory))
        batchs = np.random.choice(len(self.memory), batchs)
        for i in batchs:
            state, action, reward, next_state, done = self.memory[i]

            target = reward
            # print 'training log reward:', target
            if not done:
                predict_f = self.model.predict(next_state)[0]
                # print 'training log predict_f:', predict_f
                target = self.cur_discount * reward + self.discount * np.amax(predict_f)
                # print 'training log target:', target

            target_f = self.model.predict(state)
            # print 'training log target_f:', target_f
            target_f[0][action] = target
            # print 'action:',action
            # print 'training log target_f edited:',target_f
            # print

            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


    def act(self, state):
        if np.random.rand() <= self.epsilon:
            sample = self.env.action_space.sample()
            # print 'sampled', sample
            return sample

        act_values = self.model.predict(state)
        # print 'predicted', act_values
        return np.argmax(act_values[0])  # returns action


    def train(self, max_episode=1000000, verbose=0):

        history = open('./record/history.txt', 'w')

        for e in xrange(max_episode):
            env.reset()
            state = env.reset()
            game_over = False
            reward_sum = 0

            holds = 0
            buys = 0
            sells = 0
            print "----",self.env.targetCode,"----"
            while not game_over:

                action = self.act(state)


                if self.env.actions[action] == 'Hold':
                    holds += 1
                elif self.env.actions[action] == 'Buy':
                    buys += 1
                elif self.env.actions[action] == 'Sell':
                    sells += 1
                next_state, reward, game_over, info = self.env.step(action)
                # print info
                self.remember(state, action, reward, next_state, game_over)

                state = copy.deepcopy(next_state)

                reward_sum += reward

                if game_over:
                    toPrint = '----episode----', e,'   totalrewards:', round(reward_sum, 4), 'holds:', holds, 'buys:', buys, 'sells:', sells, 'mem size:', len(self.memory), '\n'
                    print toPrint
                    history.write(str(toPrint))
                    history.write('\n')
                    history.flush()

            if e % 50 == 0 and e != 0:
                self.model.save_weights(self.model_filename)
                print 'model weights saved'

            self.replay(128)

        history.close()

from os import walk

def exploreFolder(folder):
    files = []
    for (dirpath, dirnames, filenames) in walk(folder):
        for f in filenames:
            files.append(f.replace(".csv", ""))
        break
    return files


if __name__ == "__main__":

    targetCodes = exploreFolder('sample_data')
    for t in targetCodes:
        print t

    env = MarketEnv(dir_path="./sample_data/", target_codes=targetCodes, start_date="2015-03-13", scope=60, end_date="2017-08-11", sudden_death_rate=0.7)

    pg = DeepQ(env, current_discount=0.66, future_discount=0.80, model_file_name="./model/600197.model")

    pg.train(verbose=1)




























