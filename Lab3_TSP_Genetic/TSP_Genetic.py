import random
from time import time
from math import sqrt
from matplotlib import pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
cities = [
    ("北京", 116.46, 39.92),("天津", 117.2, 39.13),("上海", 121.48, 31.22),
    ("重庆", 106.54, 29.59),("拉萨", 91.11, 29.97),("乌鲁木齐", 87.68, 43.77),
    ("银川", 106.27, 38.47),("呼和浩特", 111.65, 40.82),("南宁", 108.33, 22.84),
    ("哈尔滨", 126.63, 45.75),("长春", 125.35, 43.88),("沈阳", 123.38, 41.8),
    ("石家庄", 114.48, 38.03),("太原", 112.53, 37.87),("西宁", 101.74, 36.56),
    ("济南", 117, 36.65),("郑州", 113.65, 34.76),("南京", 118.78, 32.04),
    ("合肥", 117.27, 31.86),("杭州", 120.19, 30.26),("福州", 119.3, 26.08),
    ("南昌", 115.89, 28.68),("长沙", 113, 28.21),("武汉", 114.31, 30.52),
    ("广州", 113.23, 23.16),("台北", 121.5, 25.05),("海口", 110.35, 20.02),
    ("兰州", 103.73, 36.03),("西安", 108.95, 34.27),("成都", 104.06, 30.67),
    ("贵阳", 106.71, 26.57),("昆明", 102.73, 25.04),("香港", 114.1, 22.2),
    ("澳门", 113.33, 22.13),
]
length = len(cities)

### 路径长度（适应度）计算：路径越短，适应度越高
def path_cost(path):
    cost = 0
    for i in range(len(path)):
        n1, x1, y1 = cities[path[i]]
        if i<len(path)-1:
            n2, x2, y2 = cities[path[i+1]]
            dis = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            cost += dis
        else:
            n2, x2, y2 = cities[path[0]]
            dis = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            cost += dis
    return cost

### 锦标赛选择函数
def select(sample_size):
    new_pops, new_costs = [], []
    while len(new_pops) < popsize:
        samples = random.sample(range(popsize),sample_size)
        sample_costs = [costs[i] for i in samples]
        new_costs.append(min(sample_costs))
        best_sample_idx = samples[sample_costs.index(min(sample_costs))]
        new_pops.append(pops[best_sample_idx])
    return new_costs, new_pops

### 交叉函数
def cross(parent_pops1, parent_pops2):
    child_pops = []
    for i in range(popsize):
        child = [None]*length
        parent1 = parent_pops1[i]
        parent2 = parent_pops2[i]
        if random.random() > pcross: # 交叉概率应用
            child = parent1.copy()
        else:
            # 随机生成交叉的起点和终点
            start, end = sorted(random.sample(range(length),2))
            # 复制parent1的中间段到child
            child[start:end+1] = parent1[start:end+1].copy()
            # 从parent2中按顺序填满child剩余位置
            parent2_remain = [i for i in parent2 if i not in child[start:end+1]]
            count = 0
            for j in range(length):
                if child[j] is None:
                    child[j] = parent2_remain[count]
                    count += 1
        child_pops.append(child)
    return child_pops

### 变异函数
def mutate(pops):
    mutate_pops = []
    for i in range(popsize):
        if random.random() > pmutate:
            mutate_pop = pops[i].copy()
        else:
            point1, point2 = random.sample(range(length),2)
            mutate_pop = pops[i].copy()
            mutate_pop[point1], mutate_pop[point2] = mutate_pop[point2], mutate_pop[point1]
        mutate_pops.append(mutate_pop)
    return mutate_pops

### 最佳路径可视化
def best_path_visible(path, best_cost):
    x, y, names = [], [], []
    # 提取坐标
    for i in path:
        names.append(cities[i][0])
        x.append(cities[i][1])
        y.append(cities[i][2])
    # 闭环：添加起点到终点
    x.append(x[0])
    y.append(y[0])
    plt.figure(figsize=(12, 8))
    # 1. 画路径线
    plt.plot(x, y, 'o-', color='blue', alpha=0.6, linewidth=1, markersize=4)
    # 2. 画起点（标红）
    plt.plot(x[0], y[0], 'o', color='red', markersize=8, label='起点/终点')
    # 3. 标注城市名
    for i in range(len(names)):
        plt.text(x[i] + 0.3, y[i] + 0.3, names[i], fontsize=9)
    plt.title(f"TSP 遗传算法最终优化路径 (总距离: {best_cost:.2f})")
    plt.xlabel("经度")
    plt.ylabel("纬度")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.show()

### 迭代过程可视化
def plot_cost_history(cost_history):
    plt.figure(figsize=(10, 6))
    plt.plot(cost_history, color='green', linewidth=1.5)
    plt.title("遗传算法收敛过程 (最优路径长度变化)")
    plt.xlabel("迭代次数 (Generation)")
    plt.ylabel("路径长度 (Best Cost)")
    plt.grid(True, linestyle='--', alpha=0.5)

    # 在最后一点标记数值
    final_cost = cost_history[-1]
    plt.text(len(cost_history) - 1, final_cost, f"{final_cost:.2f}",
             color='red', ha='right', va='bottom', fontsize=10, fontweight='bold')

    plt.show()

generation = 500 # 迭代次数
popsize = 300 # 种群大小
pcross = 0.9 # 交叉概率
pmutate = 0.1 # 变异概率

if __name__ == '__main__':
    start_time = time()
    pops = [random.sample(range(len(cities)),len(cities))
            for _ in range(popsize)] # 初始化种群
    ### 计算初代种群最优值
    costs = [None]*popsize
    for i in range(popsize):
        costs[i] = path_cost(pops[i])
    best_cost = min(costs)
    best_pop = pops[costs.index(best_cost)]
    print(f"初代最优路径长度: {best_cost:.2f}")
    best_cost_list = []
    best_cost_list.append(best_cost)
    ### 主循环
    for gen in range(generation):
        # 1、选择
        _, selected_pops = select(sample_size=5)
        # 2、交叉
        pops1 = selected_pops.copy()
        pops2 = selected_pops.copy()
        random.shuffle(pops2)
        child_pops = cross(pops1, pops2)
        # 3、变异
        child_pops = mutate(child_pops)
        # 4、计算子代路径距离
        child_costs = [None]*popsize
        for i in range(popsize):
            child_costs[i] = path_cost(child_pops[i])
        best_child_cost = min(child_costs)
        # 5、与父种群一一对比筛选出最好的
        for i in range(popsize):
            if child_costs[i] < costs[i]:
                costs[i] = child_costs[i]
                pops[i] = child_pops[i]
        if best_cost > best_child_cost:
            best_cost = best_child_cost
            best_pop = pops[costs.index(best_cost)]

        best_cost_list.append(best_cost)
        if gen % 50 == 0:
            print(f"第{gen}代最优路径长度: {best_cost:.2f}")

    end_time = time()
    print(f"最终最优路径长度: {best_cost:.2f}")
    print(f"最终最优路径：{best_pop}")
    print(f"运行时间为：{end_time-start_time:.4f}秒")
    plot_cost_history(best_cost_list)
    best_path_visible(best_pop, best_cost)