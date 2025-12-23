import math
import random
import matplotlib.pyplot as plt
cities = [
    ("北京", 116.46, 39.92), ("天津", 117.2, 39.13), ("上海", 121.48, 31.22), ("重庆", 106.54, 29.59),
    ("拉萨", 91.11, 29.97), ("乌鲁木齐", 87.68, 43.77), ("银川", 106.27, 38.47), ("呼和浩特", 111.65, 40.82),
    ("南宁", 108.33, 22.84), ("哈尔滨", 126.63, 45.75), ("长春", 125.35, 43.88), ("沈阳", 123.38, 41.8),
    ("石家庄", 114.48, 38.03), ("太原", 112.53, 37.87), ("西宁", 101.74, 36.56), ("济南", 117, 36.65),
    ("郑州", 113.65, 34.76), ("南京", 118.78, 32.04), ("合肥", 117.27, 31.86), ("杭州", 120.19, 30.26),
    ("福州", 119.3, 26.08), ("南昌", 115.89, 28.68), ("长沙", 113, 28.21), ("武汉", 114.31, 30.52),
    ("广州", 113.23, 23.16), ("台北", 121.5, 25.05), ("海口", 110.35, 20.02), ("兰州", 103.73, 36.03),
    ("西安", 108.95, 34.27), ("成都", 104.06, 30.67), ("贵阳", 106.71, 26.57), ("昆明", 102.73, 25.04),
    ("香港", 114.1, 22.2), ("澳门", 113.33, 22.13)
]
N = len(cities)

ANT_COUNT = 50  # 蚂蚁数量 m
MAX_ITER = 500  # 迭代次数
ALPHA = 1.0  # 信息素重要度
BETA = 2.0  # 启发因子重要度
RHO = 0.1  # 挥发系数
Q = 100.0  # 信息素总量常数

# 计算两点欧氏距离
def calc_dist(c1, c2):
    return math.hypot(c1[1] - c2[1], c1[2] - c2[2])

# 预计算距离矩阵 (二维列表)
dist_matrix = [[calc_dist(cities[i], cities[j]) for j in range(N)] for i in range(N)]

# 初始化信息素矩阵 (所有边初始为 1.0)
pheromone = [[1.0 for _ in range(N)] for _ in range(N)]

# 全局最优记录
best_path = []
best_dist = float('inf')
history_best = []

# ================= 主循环 =================
print(f"开始计算... 城市数: {N}, 蚂蚁数: {ANT_COUNT}")
for it in range(MAX_ITER):
    # 记录本轮所有蚂蚁的路径和距离，用于更新信息素
    round_paths = []

    for ant in range(ANT_COUNT):
        # 1. 随机起点
        curr = random.randint(0, N - 1)
        path = [curr]
        visited = {curr}
        path_len = 0

        # 2. 构建路径
        while len(path) < N:
            # 筛选未访问城市
            candidates = [i for i in range(N) if i not in visited]

            # 计算选择概率权重: (信息素^alpha) * ((1/距离)^beta)
            weights = []
            for next_city in candidates:
                tau = pheromone[curr][next_city]
                dist = dist_matrix[curr][next_city]
                if dist==0:
                    eta = 1.0 / (dist + 1e-10)  # 避免除0
                else:
                    eta = 1.0 / dist
                weights.append((tau ** ALPHA) * (eta ** BETA))

            # 轮盘赌选择
            next_node = random.choices(candidates, weights=weights, k=1)[0]

            path.append(next_node)
            visited.add(next_node)
            path_len += dist_matrix[curr][next_node]
            curr = next_node

        # 加上回到起点的距离
        path_len += dist_matrix[path[-1]][path[0]]
        round_paths.append((path, path_len))

        # 更新全局最优
        if path_len < best_dist:
            best_dist = path_len
            best_path = path

    history_best.append(best_dist)

    # 3. 信息素更新
    # 挥发
    for i in range(N):
        for j in range(N):
            pheromone[i][j] *= (1 - RHO)

    # 增强 - 遍历本轮所有蚂蚁
    for path, path_len in round_paths:
        delta = Q / path_len
        for i in range(N):
            u, v = path[i], path[(i + 1) % N]  # (i+1)%N 自动处理回到起点
            pheromone[u][v] += delta
            pheromone[v][u] += delta  # 无向图对称更新

    print(f"迭代 {it + 1:3d}/{MAX_ITER} | 最优距离: {best_dist:.2f}")

# ================= 结果展示 =================
print(f"\n最优路径: {' -> '.join([cities[i][0] for i in best_path])}")
print(f"总距离: {best_dist:.2f}")

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 图1: 收敛曲线
plt.figure(figsize=(12, 8))
plt.plot(history_best)
plt.title("迭代收敛曲线")
plt.xlabel("迭代次数")
plt.ylabel("距离")
plt.grid(True, linestyle='--', alpha=0.5)
    # 在最后一点标记数值
final_cost = history_best[-1]
plt.text(len(history_best) - 1, final_cost, f"{final_cost:.2f}",
         color='red', ha='right', va='bottom', fontsize=10, fontweight='bold')
plt.show()

# 图2: 路径图
plt.figure(figsize=(12, 8))
x = [cities[i][1] for i in best_path + [best_path[0]]]  # 闭环坐标X
y = [cities[i][2] for i in best_path + [best_path[0]]]  # 闭环坐标Y
plt.plot(x, y, 'o-', color='blue', alpha=0.6, linewidth=1, markersize=4)
for name, lx, ly in cities:  # 标注城市名
    plt.text(lx+0.3, ly+0.3, name, fontsize=8)
plt.title(f"规划路线 (距离: {best_dist:.2f})")
plt.xlabel("经度")
plt.ylabel("纬度")
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()