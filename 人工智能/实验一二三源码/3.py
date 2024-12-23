# coding: utf-8
import sys
import time
import random

import _tkinter
import numpy as np
from collections import deque

import pandas as pd

if sys.version_info.major == 2:
    import Tkinter as tk
else:
    import tkinter as tk


class Maze(tk.Tk, object):
    UNIT = 80# 像素
    MAZE_H = 6  # 网格高度
    MAZE_W = 6  # 网格宽度

    def _draw_wall(self, x, y):
        center = self.UNIT / 2
        x_ = self.UNIT * x + center
        y_ = self.UNIT * y + center
        w = 2  # 墙壁宽度
        self.canvas.create_rectangle(x_ - w, y_ - w, x_ + w, y_ + w, fill='black')

    def __init__(self):
        super(Maze, self).__init__()
        self.action_space = ['U', 'D', 'L', 'R']
        self.n_actions = len(self.action_space)
        self.title('迷宫')
        self.geometry('{0}x{1}'.format(self.MAZE_H * self.UNIT,
                                       self.MAZE_W * self.UNIT))
        self._build_maze()
        self.running = True  # 添加一个标志位来跟踪游戏状态
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # 绑定关闭事件

    def on_closing(self):
        self.running = False  # 设置标志位为False
        self.destroy()  # 销毁窗口

    def _draw_rect(self, x, y, color):
        center = self.UNIT / 2
        w = center - 5
        x_ = self.UNIT * x + center
        y_ = self.UNIT * y + center
        return self.canvas.create_rectangle(x_ - w,
                                            y_ - w,
                                            x_ + w,
                                            y_ + w,
                                            fill=color)

    def _build_maze(self):
        h = self.MAZE_H * self.UNIT
        w = self.MAZE_W * self.UNIT
        self.canvas = tk.Canvas(self, bg='white', height=h, width=w)
        self.hells = []
        self.hell_coords = []

        # 手动定义迷宫结构，并将其存储为实例属性
        self.walls = [
            [False, True, True, True, True, False],
            [False, True, False, True, True, False],
            [False, True, False, True, True, False],
            [False, True, False, False, False, False],
            [False, False, False, True, True, False],
            [True, True, True, True, True, False],

        ]

        # 创建墙壁
        for y in range(self.MAZE_H):
            for x in range(self.MAZE_W):
                if  self.walls[y][x]:  # 如果当前位置是墙，则绘制
                    self._draw_wall(x, y)

        # 绘制网格线
        for c in range(0, w, self.UNIT):
            self.canvas.create_line(c, 0, c, h, fill='gray')  # 使用灰色网格线
        for r in range(0, h, self.UNIT):
            self.canvas.create_line(0, r, w, r, fill='gray')

        # 奖励（终点），使用不同的颜色或形状来表示
        self.oval = self._draw_rect(self.MAZE_W - 1, self.MAZE_H - 1, 'green')  # 使用绿色和黑色边框
        # 玩家对象，使用不同的颜色或形状来表示
        self.rect = self._draw_rect(0, 0, 'blue')  # 使用蓝色和黑色边框

        self.canvas.pack()

    def reset(self):
        self.update()
        time.sleep(0.1)
        self.canvas.delete(self.rect)
        self.rect = self._draw_rect(0, 0, 'red')
        self.old_s = None
        return self._get_grid_coords(self.canvas.coords(self.rect))

    def step(self, action):
        s = self.canvas.coords(self.rect)
        base_action = np.array([0, 0])

        actions_to_coords = {
            0: (0, -self.UNIT),  # up
            1: (0, self.UNIT),  # down
            2: (self.UNIT, 0),  # right
            3: (-self.UNIT, 0)  # left
        }

        if action in actions_to_coords:
            base_action = actions_to_coords[action]

        new_position = [s[0] + base_action[0], s[1] + base_action[1]]

        # 检查新位置是否超出边界或撞到墙壁
        grid_x_new = int(new_position[0] // self.UNIT)
        grid_y_new = int(new_position[1] // self.UNIT)

        if 0 <= grid_x_new < self.MAZE_W and 0 <= grid_y_new < self.MAZE_H and not self.walls[grid_y_new][grid_x_new]:
            self.canvas.move(self.rect, base_action[0], base_action[1])
            s_ = self.canvas.coords(self.rect)
        else:
            s_ = s  # 如果撞墙了，位置不变
            print("Hit the wall!")

        done = False
        if s_ == self.canvas.coords(self.oval):
            reward = 1
            done = True
        elif s_ in self.hell_coords:
            reward = -1
            done = True
        else:
            reward = 0

        self.old_s = s
        return self._get_grid_coords(s_), reward, done

    def _get_grid_coords(self, canvas_coords):
        """根据画布坐标计算网格坐标"""
        grid_x = int(canvas_coords[0] // self.UNIT)
        grid_y = int(canvas_coords[1] // self.UNIT)
        return grid_x, grid_y

    def render(self):
        time.sleep(0.1)  # Increase sleep time to slow down the robot
        self.update()


class q_learning_model_maze:
    def __init__(self,
                 actions,
                 learning_rate=0.1,
                 reward_decay=0.9,
                 e_greedy=0.99):
        self.actions = actions
        self.learning_rate = learning_rate
        self.reward_decay = reward_decay
        self.e_greedy = e_greedy
        self.q_table = pd.DataFrame(columns=actions, dtype=np.float32)

    def check_state_exist(self, state):
        if state not in self.q_table.index:
            new_row = pd.DataFrame(
                [[0] * len(self.actions)],  # 初始化所有动作为0
                columns=self.q_table.columns,
                index=[state]
            )
            self.q_table = pd.concat([self.q_table, new_row], axis=0)
            self.q_table.index = self.q_table.index.astype(str)

    def choose_action(self, s):
        self.check_state_exist(s)
        if np.random.uniform() < self.e_greedy:
            state_action = self.q_table.loc[s, :]
            state_action = state_action.reindex(np.random.permutation(state_action.index))
            action = state_action.idxmax()
        else:
            action = np.random.choice(self.actions)
        return action

    def rl(self, s, a, r, s_):
        self.check_state_exist(s_)
        q_predict = self.q_table.loc[s, a]  # q估计
        if s_ != 'terminal':
            q_target = r + self.reward_decay * self.q_table.loc[s_, :].max()  # q现实
        else:
            q_target = r

        self.q_table.loc[s, a] += self.learning_rate * (q_target - q_predict)


def update():
    def run_episode(episode):
        if not env.running:
            return

        s = env.reset()
        while True:
            if not env.running:
                return

            env.render()

            action = RL.choose_action(str(s))

            try:
                s_, r, done = env.step(action)
            except _tkinter.TclError:
                return

            RL.rl(str(s), action, r, str(s_))

            s = s_

            if done:
                print(f"Episode finished after {episode + 1} games")
                break

        if episode < 1 and env.running:
            env.after(10, lambda: run_episode(episode + 1))

    run_episode(0)


if __name__ == "__main__":
    env = Maze()
    RL = q_learning_model_maze(actions=list(range(env.n_actions)))
    env.after(10, lambda: update())
    env.mainloop()
