import pandas as pd
from surprise import Dataset
from surprise import Reader
from surprise import KNNBasic
from surprise.model_selection import cross_validate

# 加载数据
ratings = pd.read_csv('ratings.csv')
movies = pd.read_csv('movies.csv')

# 查看数据
print(ratings.head())
print(movies.head())

# 检查缺失值
print(ratings.isnull().sum())
print(movies.isnull().sum())

# 合并数据集
data = pd.merge(ratings, movies, on='movieId')
print(data.head())

# 定义数据读取器
reader = Reader(rating_scale=(0.5, 5))

# 加载数据
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)

# 使用基于用户的协同过滤
sim_options = {'name': 'cosine', 'user_based': True}
algo = KNNBasic(sim_options=sim_options)

# 交叉验证
results = cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)

# 尝试不同的相似度度量
sim_options = {'name': ['msd', 'cosine', 'pearson']}
for sim_name in sim_options['name']:
    sim_options['name'] = sim_name
    algo = KNNBasic(sim_options=sim_options)
    results = cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)

# 打印交叉验证结果
print(results)