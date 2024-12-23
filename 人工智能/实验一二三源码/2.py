import numpy as np


class Maze:
    def __init__(self, size=10):
        self.size = size
        self.maze = self._generate_maze()
        # 在生成迷宫后设定起始位置和出口位置
        self.start_position = (0, 0)
        self.exit_position = (size - 1, size - 1)  # 这里是属性，不是方法
        # 确保起始位置和出口位置不是墙
        self.maze[self.start_position] = 0
        self.maze[self.exit_position] = 0

    def _generate_maze(self):
        # 创建一个简单的随机迷宫，用0表示空地，1表示墙。
        maze1 = np.random.choice([0, 1], size=(self.size, self.size), p=[0.7, 0.3])
        return maze1

    def draw_maze(self):
        print("迷宫布局:")
        for row in self.maze:
            print(' '.join(['#' if cell == 1 else ' ' for cell in row]))
        print(f"起点: {self.start_position}, 终点: {self.exit_position}")

    def sense_robot(self):
        return self.start_position

    def move_robot(self, direction):
        x, y = self.sense_robot()
        next_pos = None
        reward = -1  # 每移动一步都有一个小惩罚

        if direction == 'u' and x > 0 and self.maze[x - 1][y] == 0:
            next_pos = (x - 1, y)
        elif direction == 'r' and y < self.size - 1 and self.maze[x][y + 1] == 0:
            next_pos = (x, y + 1)
        elif direction == 'd' and x < self.size - 1 and self.maze[x + 1][y] == 0:
            next_pos = (x + 1, y)
        elif direction == 'l' and y > 0 and self.maze[x][y - 1] == 0:
            next_pos = (x, y - 1)

        if next_pos is not None:
            self.start_position = next_pos
            if next_pos == self.exit_position:
                reward = 100  # 到达出口获得大奖励
        else:
            reward = -10  # 撞墙获得惩罚

        return reward

    def can_move_actions(self, position=None):
        if position is None:
            position = self.sense_robot()
        x, y = position
        actions = []
        if x > 0 and self.maze[x - 1][y] == 0: actions.append('u')
        if y < self.size - 1 and self.maze[x][y + 1] == 0: actions.append('r')
        if x < self.size - 1 and self.maze[x + 1][y] == 0: actions.append('d')
        if y > 0 and self.maze[x][y - 1] == 0: actions.append('l')
        return actions

    @property
    def exit_position(self):
        return self._exit_position

    @exit_position.setter
    def exit_position(self, value):
        self._exit_position = value


class DFSRobot:
    def __init__(self, maze1):
        self.maze = maze1
        self.visited = set()
        self.path = []

    def dfs(self, position=None):
        if position is None:
            position = self.maze.sense_robot()
        # 修正：使用属性访问而非方法调用
        if position == self.maze.exit_position:
            return [position]
        if position not in self.visited:
            print(f"正在访问位置: {position}")
            self.visited.add(position)
            self.path.append(position)
            for direction in self.maze.can_move_actions(position):
                next_pos = self.next_position(position, direction)
                result = self.dfs(next_pos)
                if result is not None:
                    return [position] + result
            self.path.remove(position)
        return None

    def next_position(self, current, direction):
        x, y = current
        if direction == 'u':
            x -= 1
        elif direction == 'r':
            y += 1
        elif direction == 'd':
            x += 1
        elif direction == 'l':
            y -= 1
        return x, y

    def run(self):
        path = self.dfs()
        if path:
            print("找到路径:", path)
        else:
            print("没有找到路径")


if __name__ == "__main__":
    maze = Maze(size=10)  # 创建一个10x10大小的迷宫
    robot = DFSRobot(maze)
    maze.draw_maze()  # 打印迷宫
    robot.run()  # 运行机器人寻找路径
