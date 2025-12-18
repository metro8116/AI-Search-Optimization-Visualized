import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image, ImageTk

openc = []

# 可视化
def draw_node_ax(maze, ax):
    """使用填充矩形在给定的坐标轴 `ax` 上绘制障碍物。
        保持与原始代码相同的视觉映射（左上角为网格原点）。"""
    for i in range(len(maze)):
        for j in range(len(maze[0])):
            if maze[i][j] == 1:
                ax.add_patch(Rectangle((j, n-1-i), 1, 1, facecolor=(0.85, 0.2, 0.2), edgecolor='k', alpha=0.9))

def make_frame(step_index, start, end, next_list, already_list, now_grid=None, annotate_all=True):
    """为当前的 A* / Dijkstra 步骤创建一个 matplotlib 图形并返回它（不显示）。"""
    global m, n, MAZE
    fig = plt.figure(step_index, figsize=(6, 6 * (n / max(1, m))))
    ax = fig.add_subplot(111)

    # grid and axis settings
    ax.set_xlim(0, m)
    ax.set_ylim(0, n)
    ax.set_xticks(range(m + 1))
    ax.set_yticks(range(n + 1))
    ax.grid(True, linestyle='--', linewidth=0.6, color='gray', alpha=0.5)
    ax.set_aspect('equal')

    # draw obstacles
    draw_node_ax(MAZE, ax)

    # draw next_list (open set)
    for node in next_list:
        ax.scatter(node.y + 0.5, n - 0.5 - node.x, s=200, color='blue', zorder=5)
        if annotate_all:
            ax.text(node.y + 1, n - 0.5 - node.x, node.f, fontsize=12, color='red', ha='right', va='top', zorder=6)
            ax.text(node.y, n - node.x, node.g, fontsize=12, color='green', ha='left', va='top', zorder=6)
            ax.text(node.y, n - 1 - node.x, node.h, fontsize=12, color='blue', ha='left', va='bottom', zorder=6)

    # draw already_list (closed set) as dots
    for node in already_list:
        ax.scatter(node.y + 0.5, n - 0.5 - node.x, s=200, color='blue', alpha=0.9, zorder=4)
        if annotate_all:
            ax.text(node.y + 1, n - 0.5 - node.x, node.f, fontsize=12, color='red', ha='right', va='top', zorder=6)
            ax.text(node.y, n - node.x, node.g, fontsize=12, color='green', ha='left', va='top', zorder=6)
            ax.text(node.y, n - 1 - node.x, node.h, fontsize=12, color='blue', ha='left', va='bottom', zorder=6)

    # draw current node with distinct marker
    if now_grid is not None:
        ax.scatter(now_grid.y + 0.5, n - 0.5 - now_grid.x, s=260, marker='o', color='blue', edgecolor='k', zorder=7)

    # draw start and end with clear markers and f/g/h as before
    ax.text(start.y + 1, n - 0.5 - start.x, start.f, fontsize=12, color='red', ha='right', va='top')
    ax.text(start.y, n - start.x, start.g, fontsize=12, color='green', ha='left', va='top')
    ax.text(start.y, n - 1 - start.x, start.h, fontsize=12, color='blue', ha='left', va='bottom')

    ax.text(end.y + 1, n - 0.5 - end.x, end.f, fontsize=12, color='red', ha='right', va='top')
    ax.text(end.y, n - end.x, end.g, fontsize=12, color='green', ha='left', va='top')
    ax.text(end.y, n - 1 - end.x, end.h, fontsize=12, color='blue', ha='left', va='bottom')

    ax.scatter(start.y + 0.5, n - 0.5 - start.x, s=300, marker='X', color='lime', edgecolor='k', zorder=8)
    ax.text(start.y + 0.1 , n  - start.x, 'START', fontsize=9, weight='bold', zorder=9)

    ax.scatter(end.y + 0.5, n - 0.5 - end.x, s=300, marker='X', color='magenta', edgecolor='k', zorder=8)
    ax.text(end.y + 0.2, n  - end.x, 'END', fontsize=9, weight='bold', zorder=9)

    ax.set_title(f'{algorithm_label.get()} step: {step_index}', fontsize=11)

    return fig

# find_neighbors: now supports turning off heuristic (for Dijkstra)
def find_neighbors(grid, next_list, already_list, use_heuristic=True, end=None):
    grid_list = []
    # 判断八个方向是否满足要求，满足便添加
    if is_valid_grid(grid.x, grid.y-1, next_list, already_list):
        grid_list.append(Grid(grid.x, grid.y-1))
    if is_valid_grid(grid.x, grid.y+1, next_list, already_list):
        grid_list.append(Grid(grid.x, grid.y+1))
    if is_valid_grid(grid.x-1, grid.y, next_list, already_list):
        grid_list.append(Grid(grid.x-1, grid.y))
    if is_valid_grid(grid.x+1, grid.y, next_list, already_list):
        grid_list.append(Grid(grid.x+1, grid.y))

    if is_valid_grid(grid.x+1, grid.y+1, next_list, already_list):
        grid_list.append(Grid(grid.x+1, grid.y+1))
    if is_valid_grid(grid.x-1, grid.y-1, next_list, already_list):
        grid_list.append(Grid(grid.x-1, grid.y-1))
    if is_valid_grid(grid.x-1, grid.y+1, next_list, already_list):
        grid_list.append(Grid(grid.x-1, grid.y+1))
    if is_valid_grid(grid.x+1, grid.y-1, next_list, already_list):
        grid_list.append(Grid(grid.x+1, grid.y-1))

    # 更新已存在节点的 g 值（直/斜分别 +10 / +14）
    index1= [(-1,0),(1,0),(0,-1),(0,1)]
    for dx,dy in index1:
        tx, ty = grid.x+dx, grid.y+dy
        if contain_grid(next_list, tx, ty):
            for search in next_list:
                if search.x == tx and search.y == ty:
                    old_g = search.g
                    old_grid = search
                    break
            now_g = grid.g + 10
            if now_g < old_g:
                Grid_now = Grid(tx, ty)
                # 使用传入的 end（若为 None 则用全局 end_grid）
                Grid_now.init_grid(grid, end if end is not None else end_grid)
                if not use_heuristic:
                    Grid_now.h = 0
                    Grid_now.f = Grid_now.g
                next_list.remove(old_grid)
                next_list.append(Grid_now)

        if contain_grid(already_list, tx, ty):
            for search in already_list:
                if search.x == tx and search.y == ty:
                    old_g = search.g
                    old_grid = search
                    break
            now_g = grid.g + 10
            if now_g < old_g:
                Grid_now = Grid(tx, ty)
                Grid_now.init_grid(grid, end if end is not None else end_grid)
                if not use_heuristic:
                    Grid_now.h = 0
                    Grid_now.f = Grid_now.g
                already_list.remove(old_grid)
                next_list.append(Grid_now)

    index2 = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dx,dy in index2:
        tx, ty = grid.x+dx, grid.y+dy
        if contain_grid(next_list, tx, ty):
            for search in next_list:
                if search.x == tx and search.y == ty:
                    old_g = search.g
                    old_grid = search
                    break
            now_g = grid.g + 14
            if now_g < old_g:
                Grid_now = Grid(tx, ty)
                Grid_now.init_grid(grid, end if end is not None else end_grid)
                if not use_heuristic:
                    Grid_now.h = 0
                    Grid_now.f = Grid_now.g
                next_list.remove(old_grid)
                next_list.append(Grid_now)

        if contain_grid(already_list, tx, ty):
            for search in already_list:
                if search.x == tx and search.y == ty:
                    old_g = search.g
                    old_grid = search
                    break
            now_g = grid.g + 14
            if now_g < old_g:
                Grid_now = Grid(tx, ty)
                Grid_now.init_grid(grid, end if end is not None else end_grid)
                if not use_heuristic:
                    Grid_now.h = 0
                    Grid_now.f = Grid_now.g
                already_list.remove(old_grid)
                next_list.append(Grid_now)

    return grid_list

def is_valid_grid(x, y, next_list, already_list):
    # 边界
    if x<0 or x>=len(MAZE) or y<0 or y>=len(MAZE[0]):
        return False
    # 障碍
    if MAZE[x][y] == 1:
        return False
    # 是否在next和already中
    if contain_grid(next_list, x,y):
        return False
    if contain_grid(already_list, x,y):
        return False
    return True

def contain_grid(grid_list, x,y):
    for grid in grid_list:
        if (grid.x == x) and (grid.y == y):
            return True
    return False

def find_min_grid(next_list=[]):
    # 选择 f 最小的；在 Dijkstra 情况下 f==g
    temp_grid = next_list[0]
    for grid in next_list:
        if grid.f < temp_grid.f:
            temp_grid = grid
    return temp_grid

class Grid:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.f = 0
        self.g = 0
        self.h = 0
        self.parent = None
    def init_grid(self, parent, end):
        self.parent = parent
        if abs(self.x - parent.x) + abs(self.y - parent.y) == 2:
            self.g = parent.g + 14
        else:
            self.g = parent.g + 10
        # end 可能为 None（在特定调用路径），处理稳健性
        if end is not None:
            self.h = (abs(self.x - end.x) + abs(self.y - end.y))*10
        else:
            self.h = 0
        self.f = self.g + self.h

def draw_picture(m_arg, n_arg, path):
    global MAZE
    global success
    success = plt.figure(3000, figsize=(6, 6 * (n_arg / max(1, m_arg))))
    ax = success.add_subplot(111)

    ax.set_xlim(0,m_arg)
    ax.set_ylim(0,n_arg)
    ax.set_xticks(range(m_arg+1))
    ax.set_yticks(range(n_arg+1))
    ax.grid(True, linestyle='--', linewidth=0.6, color='gray', alpha=0.5)
    ax.set_aspect('equal')

    # Draw path as a connected line + nodes (use original coordinate mapping)
    ys = [p.y + 0.5 for p in path]
    xs = [n_arg - 0.5 - p.x for p in path]
    if len(xs) > 0:
        ax.plot(ys[::-1], xs[::-1], linewidth=3, linestyle='-', zorder=9)
    for i in range(len(path)):
        ax.scatter(path[i].y+0.5, n_arg-0.5-path[i].x, s=240, color='tab:blue', edgecolor='k', zorder=10)

    draw_node_ax(MAZE, ax)

# -----------------------
# A* 搜索（使用启发式 h）
# -----------------------
def a_start_search(start, end):
    global m, n, MAZE, openc
    openc = []
    next_list = []
    already_list = []

    # 初始化 start（在放入 next 之前）
    start.g = 0
    start.h = (abs(start.x-end.x) + abs(start.y-end.y))*10
    start.f = start.g + start.h
    next_list.append(start)

    step = 0
    while len(next_list) > 0:
        fig = make_frame(step, start, end, next_list, already_list)
        openc.append(fig)
        step += 1

        # 寻找最小 f 节点
        now_grid = find_min_grid(next_list)
        next_list.remove(now_grid)
        already_list.append(now_grid)

        # 寻找邻居（启发式开启）
        neighbors = find_neighbors(now_grid, next_list, already_list, use_heuristic=True, end=end)
        for grid in neighbors:
            # 斜角穿越判断（保留原逻辑）
            success11 = 0
            if 0 <= grid.x-1 < len(MAZE) and 0 <= now_grid.y + 1 < len(MAZE[0]):
                if MAZE[grid.x - 1][grid.y] == 1 and MAZE[now_grid.x][now_grid.y + 1] == 1:
                    success11 = 101
            if 0 <= grid.x+1 < len(MAZE) and 0 <= now_grid.y + 1 < len(MAZE[0]):
                if MAZE[grid.x + 1][grid.y] == 1 and MAZE[now_grid.x][now_grid.y + 1] == 1:
                    success11 = 101
            if 0 <= grid.y-1 < len(MAZE[0]) and 0 <= now_grid.x + 1 < len(MAZE):
                if MAZE[grid.x][grid.y-1] == 1 and MAZE[now_grid.x+1][now_grid.y] == 1:
                    success11 = 101
            if 0 <= grid.y-1 < len(MAZE[0]) and 0 <= now_grid.x - 1 < len(MAZE):
                if MAZE[grid.x][grid.y-1] == 1 and MAZE[now_grid.x-1][now_grid.y] == 1:
                    success11 = 101

            if success11 != 101:
                grid.init_grid(now_grid, end)
                next_list.append(grid)

        # 检查是否到达终点
        for grid in next_list:
            if (grid.x == end.x) and (grid.y == end.y):
                return grid

    return None

# -----------------------
# Dijkstra 搜索（h = 0）
# -----------------------
def dijkstra_search(start, end):
    global m, n, MAZE, openc
    openc = []
    next_list = []
    already_list = []

    # 初始化 start（h = 0）
    start.g = 0
    start.h = 0
    start.f = start.g
    next_list.append(start)

    step = 0
    while len(next_list) > 0:
        fig = make_frame(step, start, end, next_list, already_list)
        openc.append(fig)
        step += 1

        # 寻找最小 f（f==g）
        now_grid = find_min_grid(next_list)
        next_list.remove(now_grid)
        already_list.append(now_grid)

        # 寻找邻居（不使用启发式）
        neighbors = find_neighbors(now_grid, next_list, already_list, use_heuristic=False, end=end)
        for grid in neighbors:
            # 斜角穿越判断（保留原逻辑）
            success11 = 0
            if 0 <= grid.x-1 < len(MAZE) and 0 <= now_grid.y + 1 < len(MAZE[0]):
                if MAZE[grid.x - 1][grid.y] == 1 and MAZE[now_grid.x][now_grid.y + 1] == 1:
                    success11 = 101
            if 0 <= grid.x+1 < len(MAZE) and 0 <= now_grid.y + 1 < len(MAZE[0]):
                if MAZE[grid.x + 1][grid.y] == 1 and MAZE[now_grid.x][now_grid.y + 1] == 1:
                    success11 = 101
            if 0 <= grid.y-1 < len(MAZE[0]) and 0 <= now_grid.x + 1 < len(MAZE):
                if MAZE[grid.x][grid.y-1] == 1 and MAZE[now_grid.x+1][now_grid.y] == 1:
                    success11 = 101
            if 0 <= grid.y-1 < len(MAZE[0]) and 0 <= now_grid.x - 1 < len(MAZE):
                if MAZE[grid.x][grid.y-1] == 1 and MAZE[now_grid.x-1][now_grid.y] == 1:
                    success11 = 101

            if success11 != 101:
                grid.init_grid(now_grid, end)
                # Dijkstra: 丢弃启发式 h，f==g
                grid.h = 0
                grid.f = grid.g
                next_list.append(grid)

        # 检查是否到达终点
        for grid in next_list:
            if (grid.x == end.x) and (grid.y == end.y):
                return grid

    return None

# -------------------------
# Tkinter UI (with background)
# -------------------------
root = tk.Tk()
root.title("A* vs Dijkstra")
root.geometry('1000x700')

# 全局选择标签（显示当前算法）
algorithm_label = tk.StringVar(value="A*")  # 默认 A*
algorithm_choice = {"A*": "astar", "Dijkstra": "dijkstra"}

# 背景图（background.png）
try:
    bg_image = Image.open("background.png")
    bg_image = bg_image.resize((1000, 700))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_canvas = tk.Canvas(root, width=1000, height=600)
    bg_canvas.pack(fill="both", expand=True)
    bg_canvas.create_image(0, 0, image=bg_photo, anchor="nw")
except Exception:
    # 若没有背景图则使用普通 frame
    bg_canvas = tk.Canvas(root, width=1000, height=600, bg="#f0f0f0")
    bg_canvas.pack(fill="both", expand=True)

# 显示当前算法
alg_label_widget = tk.Label(root, textvariable=algorithm_label, bg="#ffffff", font=("Arial", 10, "bold"))
bg_canvas.create_window(200, 30, window=alg_label_widget)

# 算法选择按钮
def select_astar():
    algorithm_label.set("A*")
def select_dijkstra():
    algorithm_label.set("Dijkstra")

btn_astar = tk.Button(root, text="选择 A*", command=select_astar, width=12)
bg_canvas.create_window(120, 60, window=btn_astar)
btn_dijkstra = tk.Button(root, text="选择 Dijkstra", command=select_dijkstra, width=12)
bg_canvas.create_window(260, 60, window=btn_dijkstra)

# 输入与控件（放在 canvas 上）
label= tk.Label(root, text="起点的x坐标", bg="#ffffff")
bg_canvas.create_window(80, 110, window=label)
e = tk.Entry(root, show=None, width=10)
e.insert(0, "1")
bg_canvas.create_window(80, 135, window=e)

label2= tk.Label(root, text="起点的y坐标", bg="#ffffff")
bg_canvas.create_window(80, 170, window=label2)
e2 = tk.Entry(root, show=None, width=10)
e2.insert(0, "1")
bg_canvas.create_window(80, 195, window=e2)

label3= tk.Label(root, text="终点的x坐标", bg="#ffffff")
bg_canvas.create_window(80, 230, window=label3)
e3 = tk.Entry(root, show=None, width=10)
e3.insert(0, "7")
bg_canvas.create_window(80, 255, window=e3)

label4= tk.Label(root, text="终点的y坐标", bg="#ffffff")
bg_canvas.create_window(80, 290, window=label4)
e4 = tk.Entry(root, show=None, width=10)
e4.insert(0, "7")
bg_canvas.create_window(80, 315, window=e4)

# Run / Next 控件
def moveot():
    global MAZE, start_grid, end_grid, m, n, openc, count
    n1 = int(e.get())
    n2 = int(e2.get())
    n3 = int(e3.get())
    n4 = int(e4.get())

    MAZE = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    # 获取迷宫形状
    m = len(MAZE[0])
    n = len(MAZE)

    start_grid = Grid(n1, n2)
    end_grid = Grid(n3, n4)

    # 根据选择的算法执行
    alg = algorithm_label.get()
    if alg == "A*":
        result_grid = a_start_search(start_grid, end_grid)
    else:
        result_grid = dijkstra_search(start_grid, end_grid)

    # 路径回溯
    path = []
    while result_grid is not None:
        path.append(Grid(result_grid.x, result_grid.y))
        result_grid = result_grid.parent

    # 绘制最终路径图
    draw_picture(m, n, path)

    count = 0

def moveot1():
    global count, success
    # 若 openc 为空（尚未运行），直接返回
    if not openc and 'success' not in globals():
        return
    if count >= len(openc):
        canvas = FigureCanvasTkAgg(success, master=bg_canvas)
        canvas.draw()
        bg_canvas.create_window(700, 300, window=canvas.get_tk_widget())
    else:
        canvas = FigureCanvasTkAgg(openc[count], master=bg_canvas)
        canvas.draw()
        bg_canvas.create_window(700, 300, window=canvas.get_tk_widget())
        count += 1

b = tk.Button(root, text = "Run", command=moveot, width=10, height=2 )
bg_canvas.create_window(80, 360, window=b)

b1 = tk.Button(root, text = "Next", command=moveot1, width=10, height=2 )
bg_canvas.create_window(80, 430, window=b1)

root.mainloop()
