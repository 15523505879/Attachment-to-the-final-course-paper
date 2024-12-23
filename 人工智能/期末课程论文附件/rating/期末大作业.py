import pandas as pd
from collections import defaultdict, deque
from itertools import combinations

def load_ratings_in_chunks(file_path, chunk_size=10**6, nrows=None):
    """分块从文件中加载评分数据."""
    for chunk in pd.read_csv(file_path, sep='\t', header=None, usecols=[0, 1, 2, 3],
                             names=['user_id', 'item_id', 'rating', 'weight'], chunksize=chunk_size, encoding='utf-8',
                             nrows=nrows):
        yield chunk

def build_trust_network_from_file(file_path, chunk_size=10 ** 6, nrows=None):
    """基于共同评价直接从文件流式构建信任网络."""
    trust_graph = defaultdict(set)  # 使用集合避免重复边

    item_to_users = defaultdict(set)
    for chunk in load_ratings_in_chunks(file_path, chunk_size, nrows):
        # 构建物品到用户的映射
        for _, row in chunk.iterrows():
            user_id = row['user_id']
            item_id = row['item_id']
            item_to_users[item_id].add(user_id)

        # 对于每个物品，找出所有评价过它的用户组合，并建立这些用户间的信任关系
        for users in item_to_users.values():
            if len(users) > 1:
                for user_pair in combinations(users, 2):
                    u1, u2 = sorted(user_pair)
                    trust_graph[u1].add(u2)
                    trust_graph[u2].add(u1)

        # 清空已经处理过的物品到用户的映射，以便下一批次的数据处理
        item_to_users.clear()

    # 将 set 转换回 list，如果后续操作需要的话
    return {k: list(v) for k, v in trust_graph.items()}

def bfs(graph, start_node, max_depth=2, max_nodes=None):
    """执行广度优先搜索，返回指定深度内的所有可达节点."""
    visited = set([start_node])
    queue = deque([(start_node, 0)])
    reachable_nodes = []

    while queue and (max_nodes is None or len(reachable_nodes) < max_nodes):
        node, depth = queue.popleft()

        if depth <= max_depth:
            reachable_nodes.append((node, depth))

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

    return reachable_nodes

if __name__ == "__main__":
    rating_file = "rating.txt"  # 请根据实际情况调整为正确的文件路径

    # 假设每行平均大小约为100字节，3MB ≈ 30720 行
    nrows = 30720

    # 直接使用文件路径来构建信任网络
    trust_graph = build_trust_network_from_file(rating_file, nrows=nrows)

    # 加载数据只是为了展示前几行，实际构建信任网络不需要再加载一次数据
    ratings_data = next(load_ratings_in_chunks(rating_file, nrows=nrows))

    # 打印一些基本信息
    print("Ratings Data Overview:")
    print(ratings_data.head())

    # 挑选一个用户ID作为起点进行BFS实验
    if not ratings_data.empty:
        start_user_id = int(ratings_data['user_id'].iloc[0])  # 确保选择的是一个整数类型的用户ID
        print(f"\nPerforming BFS starting from user {start_user_id}...")

        # 使用BFS算法查找从选定用户开始的最大深度为2的所有可达节点
        reachable_users = bfs(trust_graph, start_user_id, max_depth=2)

        # 输出结果
        for user, depth in reachable_users:
            print(f"User ID: {user}, Depth: {depth}")
    else:
        print("No valid user found in the ratings data.")
