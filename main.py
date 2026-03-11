import tkinter as tk
from tkinter import ttk, messagebox

class CowPuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("牛位置解谜工具（交互式求解，颜色唯一）")
        self.root.geometry("1200x800")
        self.root.minsize(900, 700)

        # 颜色配置（20种可见颜色）
        self.COLORS = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD",
            "#D4A5A5", "#9B59B6", "#3498DB", "#E67E22", "#2ECC71",
            "#E74C3C", "#1ABC9C", "#F1C40F", "#E67E22", "#9B59B6",
            "#34495E", "#16A085", "#27AE60", "#2980B9", "#8E44AD"
        ]
        self.COLOR_NAMES = [
            "柔和红", "浅海绿", "天湖蓝", "薄荷绿", "奶油黄",
            "玫瑰棕", "紫罗兰", "亮蓝", "橙", "鲜绿",
            "朱红", "青绿", "金黄", "橙", "紫",
            "深灰蓝", "翡翠绿", "草绿", "深海蓝", "紫罗兰"
        ]

        # 状态变量
        self.stage = "size"                # size -> color -> params -> solve
        self.rows = 4
        self.cols = 4
        self.board = []                     # 二维列表，存储每个格子的颜色索引
        self.current_color = 0               # 当前选中的颜色索引
        self.initial_cow = None               # (r, c)，可能为None
        self.placed_cows = []                 # 所有已放置的牛（包括初始牛和手动/自动添加的）
        self.extra_cows = []                  # 所有额外放置的牛（手动或自动，不包括初始牛）
        self.total_cows = 0                    # 总牛数（包括初始牛）

        # 界面元素
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 左侧：棋盘 + 控制区
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 右侧：日志区（固定宽度）
        self.right_frame = ttk.Frame(self.main_frame, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.right_frame.pack_propagate(False)

        # 日志组件
        ttk.Label(self.right_frame, text="操作日志", font=("黑体", 12, "bold")).pack(pady=5)
        self.log_text = tk.Text(self.right_frame, height=35, width=32, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 重启按钮（始终可用）
        ttk.Button(self.right_frame, text="重启", command=self.restart).pack(pady=10)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("当前阶段：设置棋盘尺寸")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 启动第一个阶段
        self.show_size_stage()

    # ---------- 日志工具 ----------
    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{self.stage.upper()}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    # ---------- 通用界面清理 ----------
    def clear_left_frame(self):
        for widget in self.left_frame.winfo_children():
            widget.destroy()

    # ---------- 阶段1：设置棋盘尺寸 ----------
    def show_size_stage(self):
        self.stage = "size"
        self.status_var.set("当前阶段：设置棋盘尺寸")
        self.clear_left_frame()
        self.log("进入尺寸设置阶段")

        ttk.Label(self.left_frame, text="设置棋盘尺寸", font=("黑体", 16, "bold")).pack(pady=20)

        size_frame = ttk.Frame(self.left_frame)
        size_frame.pack(pady=20)

        ttk.Label(size_frame, text="行数:").grid(row=0, column=0, padx=5, pady=5)
        self.row_entry = ttk.Entry(size_frame, width=5, font=("Arial", 14))
        self.row_entry.insert(0, str(self.rows))
        self.row_entry.grid(row=0, column=1, padx=5)

        ttk.Label(size_frame, text="列数:").grid(row=0, column=2, padx=5, pady=5)
        self.col_entry = ttk.Entry(size_frame, width=5, font=("Arial", 14))
        self.col_entry.insert(0, str(self.cols))
        self.col_entry.grid(row=0, column=3, padx=5)

        ttk.Button(self.left_frame, text="生成棋盘", command=self.generate_board, width=20).pack(pady=30)

    def generate_board(self):
        try:
            rows = int(self.row_entry.get())
            cols = int(self.col_entry.get())
            if rows < 1 or cols < 1 or rows * cols > 400:   # 最大20x20
                raise ValueError
            self.rows, self.cols = rows, cols
            self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
            self.current_color = 0
            self.initial_cow = None
            self.placed_cows = []
            self.extra_cows = []
            self.total_cows = 0
            self.log(f"生成 {self.rows} x {self.cols} 棋盘")
            self.show_color_stage()
        except:
            messagebox.showerror("错误", "请输入有效的正整数（1~20），且格子数不超过400")

    # ---------- 阶段2：颜色绘制 ----------
    def show_color_stage(self):
        self.stage = "color"
        self.status_var.set("当前阶段：颜色绘制")
        self.clear_left_frame()

        canvas_frame = ttk.Frame(self.left_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定事件：单击、拖动、窗口大小变化
        self.canvas.bind("<Button-1>", self.paint_cell)
        self.canvas.bind("<B1-Motion>", self.paint_cell_drag)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # 颜色选择区域（两行，每行10个按钮）
        color_frame = ttk.Frame(self.left_frame)
        color_frame.pack(pady=10, fill=tk.X)

        self.color_buttons = []
        for i in range(20):
            row = i // 10
            col = i % 10
            btn = tk.Button(color_frame, bg=self.COLORS[i], width=3, relief=tk.RAISED,
                            command=lambda c=i: self.select_color(c))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.color_buttons.append(btn)

        self.select_color(0)

        # 按钮框架
        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(pady=10)

        self.next_btn = ttk.Button(btn_frame, text="下一步", command=self.check_color_complete)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        self.back_btn = ttk.Button(btn_frame, text="上一步", command=self.back_to_size)
        self.back_btn.pack(side=tk.LEFT, padx=5)

        self.redraw_board()

    def on_canvas_resize(self, event):
        self.redraw_board()

    def redraw_board(self):
        """绘制棋盘，格子保持正方形，棋盘居中"""
        if not hasattr(self, 'canvas'):
            return
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        cell_size = min(w / self.cols, h / self.rows)
        offset_x = (w - cell_size * self.cols) / 2
        offset_y = (h - cell_size * self.rows) / 2

        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y

        for r in range(self.rows):
            for c in range(self.cols):
                x1 = offset_x + c * cell_size
                y1 = offset_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                color_idx = self.board[r][c]
                fill = self.COLORS[color_idx] if color_idx is not None else "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=fill,
                                              tags=f"cell_{r}_{c}")

        # 绘制所有已放置的牛
        for pos in self.placed_cows:
            if pos == self.initial_cow:
                color = "black"
            else:
                color = "red"
            self.draw_cow_marker(pos, color)

    def select_color(self, color_idx):
        self.current_color = color_idx
        for i, btn in enumerate(self.color_buttons):
            btn.config(relief=tk.SUNKEN if i == color_idx else tk.RAISED)
        self.log(f"选择颜色: {self.COLOR_NAMES[color_idx]}")

    def paint_cell(self, event):
        self._paint_at_event(event)

    def paint_cell_drag(self, event):
        self._paint_at_event(event)

    def _paint_at_event(self, event):
        if self.stage != "color":
            return
        x, y = event.x, event.y
        dx = x - self.offset_x
        dy = y - self.offset_y
        if dx < 0 or dy < 0:
            return
        c = int(dx // self.cell_size)
        r = int(dy // self.cell_size)
        if 0 <= r < self.rows and 0 <= c < self.cols:
            if self.board[r][c] != self.current_color:
                self.board[r][c] = self.current_color
                self.canvas.itemconfig(f"cell_{r}_{c}", fill=self.COLORS[self.current_color])
                self.log(f"染色 ({r+1},{c+1}) → {self.COLOR_NAMES[self.current_color]}")

                # 检查是否所有格子染色
                if all(cell is not None for row in self.board for cell in row):
                    self.next_btn.config(state=tk.NORMAL)
                else:
                    self.next_btn.config(state=tk.DISABLED)

    def back_to_size(self):
        self.log("返回尺寸设置")
        self.show_size_stage()

    def check_color_complete(self):
        if all(cell is not None for row in self.board for cell in row):
            self.show_params_stage()
        else:
            messagebox.showwarning("警告", "请先完成所有格子的染色")

    # ---------- 阶段3：参数设置（总牛数、可选初始牛） ----------
    def show_params_stage(self):
        self.stage = "params"
        self.status_var.set("当前阶段：设置总牛数和初始牛")
        self.log("进入参数设置阶段")

        self.clear_left_frame()

        canvas_frame = ttk.Frame(self.left_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Button-1>", self.place_initial_cow)

        ttk.Label(self.left_frame, text="点击棋盘上的格子可放置初始牛（黑色圆圈，可选）",
                  foreground="blue").pack(pady=5)

        count_frame = ttk.Frame(self.left_frame)
        count_frame.pack(pady=5)
        ttk.Label(count_frame, text="总牛数（包含初始牛）:").pack(side=tk.LEFT)
        self.total_cow_var = tk.StringVar()
        self.total_cow_entry = ttk.Entry(count_frame, textvariable=self.total_cow_var, width=5)
        self.total_cow_entry.pack(side=tk.LEFT, padx=5)
        color_count = len(set(cell for row in self.board for cell in row))
        self.total_cow_var.set(str(color_count))

        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(pady=10)

        self.enter_solve_btn = ttk.Button(btn_frame, text="进入求解", command=self.enter_solve_stage)
        self.enter_solve_btn.pack(side=tk.LEFT, padx=5)

        self.back_btn = ttk.Button(btn_frame, text="上一步", command=self.back_to_color)
        self.back_btn.pack(side=tk.LEFT, padx=5)

        self.reset_initial_btn = ttk.Button(btn_frame, text="清除初始牛", command=self.clear_initial_cow)
        self.reset_initial_btn.pack(side=tk.LEFT, padx=5)

        self.redraw_board()

    def place_initial_cow(self, event):
        if self.stage != "params":
            return
        x, y = event.x, event.y
        dx = x - self.offset_x
        dy = y - self.offset_y
        if dx < 0 or dy < 0:
            return
        c = int(dx // self.cell_size)
        r = int(dy // self.cell_size)
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        pos = (r, c)
        if self.initial_cow is not None:
            if self.initial_cow in self.placed_cows:
                self.placed_cows.remove(self.initial_cow)
            self.initial_cow = None
        self.initial_cow = pos
        self.placed_cows = [self.initial_cow]
        self.log(f"设置初始牛位置: ({r+1},{c+1})")
        self.redraw_board()

    def clear_initial_cow(self):
        if self.initial_cow is not None:
            self.initial_cow = None
            self.placed_cows = []
            self.redraw_board()
            self.log("已清除初始牛")

    def back_to_color(self):
        self.log("返回颜色绘制")
        self.show_color_stage()

    # ---------- 阶段4：交互式求解（优化版，按颜色分组回溯）----------
    def enter_solve_stage(self):
        try:
            total = int(self.total_cow_var.get())
            if total < 1 or total > self.rows * self.cols:
                raise ValueError
        except:
            messagebox.showerror("错误", f"请输入有效的总牛数（1 ~ {self.rows*self.cols}）")
            return

        # 检查总牛数是否超过颜色种类数
        color_count = len(set(cell for row in self.board for cell in row))
        if total > color_count:
            messagebox.showerror("错误", f"总牛数不能超过颜色种类数（{color_count}）")
            return

        self.total_cows = total

        self.stage = "solve"
        self.status_var.set("当前阶段：交互式求解")
        self.log(f"进入求解阶段，总牛数 {self.total_cows}，当前已放置 {len(self.placed_cows)} 头牛")

        self.clear_left_frame()

        canvas_frame = ttk.Frame(self.left_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Button-1>", self.manual_place)

        self.remaining_var = tk.StringVar()
        self.remaining_var.set(f"剩余需放置牛数: {self.total_cows - len(self.placed_cows)}")
        ttk.Label(self.left_frame, textvariable=self.remaining_var, font=("Arial", 12)).pack(pady=5)

        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(pady=10)

        self.auto_btn = ttk.Button(btn_frame, text="自动求解剩余", command=self.auto_solve_remaining)
        self.auto_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(btn_frame, text="重置手动牛", command=self.reset_manual)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        self.back_btn = ttk.Button(btn_frame, text="上一步", command=self.back_to_params)
        self.back_btn.pack(side=tk.LEFT, padx=5)

        self.redraw_board()
        self.update_remaining()

    def back_to_params(self):
        self.log("返回参数设置")
        self.show_params_stage()

    # ---------- 求解核心方法（按颜色分组）----------
    def check_position(self, pos, cows_list=None):
        """检查位置与给定牛列表是否冲突（同行、同列、相邻）"""
        if cows_list is None:
            cows_list = self.placed_cows
        r, c = pos
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return False, "位置超出棋盘"
        if pos in cows_list:
            return False, "该格子已有牛"
        for (rr, cc) in cows_list:
            if rr == r or cc == c:
                return False, f"与 ({rr+1},{cc+1}) 的牛同行/同列"
            if abs(rr - r) <= 1 and abs(cc - c) <= 1:
                return False, f"与 ({rr+1},{cc+1}) 的牛相邻"
        return True, ""

    def is_position_valid_with_list(self, pos, cows_list):
        """仅返回布尔值，用于回溯"""
        r, c = pos
        for (rr, cc) in cows_list:
            if rr == r or cc == c:
                return False
            if abs(rr - r) <= 1 and abs(cc - c) <= 1:
                return False
        return True

    def manual_place(self, event):
        if self.stage != "solve":
            return
        x, y = event.x, event.y
        dx = x - self.offset_x
        dy = y - self.offset_y
        if dx < 0 or dy < 0:
            return
        c = int(dx // self.cell_size)
        r = int(dy // self.cell_size)
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        pos = (r, c)
        valid, reason = self.check_position(pos)
        if not valid:
            self.log(f"格子 ({r+1},{c+1}) 放置失败：{reason}")
            return
        if len(self.placed_cows) >= self.total_cows:
            self.log("已放置所有牛，不能再添加")
            return

        self.placed_cows.append(pos)
        self.extra_cows.append(pos)
        self.draw_cow_marker(pos, "red")
        self.log(f"手动放置牛: ({r+1},{c+1})")
        self.update_remaining()

    def draw_cow_marker(self, pos, color):
        r, c = pos
        cx = self.offset_x + c * self.cell_size + self.cell_size / 2
        cy = self.offset_y + r * self.cell_size + self.cell_size / 2
        radius = self.cell_size * 0.3
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                fill=color, outline=color)

    def update_remaining(self):
        remaining = self.total_cows - len(self.placed_cows)
        self.remaining_var.set(f"剩余需放置牛数: {remaining}")
        if remaining <= 0:
            self.auto_btn.config(state=tk.DISABLED)
        else:
            self.auto_btn.config(state=tk.NORMAL)

    def auto_solve_remaining(self):
        remaining = self.total_cows - len(self.placed_cows)
        if remaining <= 0:
            return

        self.log(f"开始自动求解剩余 {remaining} 头牛...")

        # 构建已使用颜色集合
        used_colors = set(self.board[r][c] for (r,c) in self.placed_cows)
        all_colors = set(cell for row in self.board for cell in row)
        available_colors = list(all_colors - used_colors)

        if len(available_colors) < remaining:
            self.log("剩余颜色不足，无法放置")
            messagebox.showinfo("结果", "剩余颜色种类不足，无法放置")
            return

        # 为每个颜色收集可用格子（未被占用的）
        color_positions = {}
        for color in available_colors:
            positions = []
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.board[r][c] == color and (r,c) not in self.placed_cows:
                        positions.append((r,c))
            color_positions[color] = positions

        # 过滤掉没有格子的颜色
        available_colors = [c for c in available_colors if color_positions[c]]
        if len(available_colors) < remaining:
            self.log("部分颜色无可用格子，无法放置")
            messagebox.showinfo("结果", "部分颜色无可用格子，无法放置")
            return

        # 按可选格子数升序排序（优先尝试约束大的颜色）
        available_colors.sort(key=lambda c: len(color_positions[c]))

        # 开始回溯
        solution = self.backtrack_by_color(available_colors, color_positions, remaining, [])
        if solution is None:
            self.log("自动求解失败：无法找到合法位置")
            messagebox.showinfo("结果", "无法放置剩余牛，请尝试手动调整")
            return

        for pos in solution:
            self.placed_cows.append(pos)
            self.extra_cows.append(pos)
            self.draw_cow_marker(pos, "red")
        self.log(f"自动求解成功，添加了 {len(solution)} 头牛")
        self.update_remaining()

    def backtrack_by_color(self, colors, color_positions, needed, current_solution):
        if needed == 0:
            return []

        for i, color in enumerate(colors):
            candidates = color_positions[color]
            # 过滤与已放置牛（全局+当前分支）冲突的格子
            all_placed = self.placed_cows + current_solution
            valid_candidates = [p for p in candidates if self.is_position_valid_with_list(p, all_placed)]

            if not valid_candidates:
                continue

            # 按某种顺序尝试（例如按行坐标排序）
            valid_candidates.sort()
            for pos in valid_candidates:
                current_solution.append(pos)
                remaining_colors = colors[:i] + colors[i+1:]
                result = self.backtrack_by_color(remaining_colors, color_positions, needed-1, current_solution)
                if result is not None:
                    return [pos] + result
                current_solution.pop()
        return None

    def reset_manual(self):
        if self.initial_cow:
            self.placed_cows = [self.initial_cow]
        else:
            self.placed_cows = []
        self.extra_cows = []
        self.redraw_board()
        self.log("已重置所有手动放置的牛")
        self.update_remaining()

    # ---------- 重启 ----------
    def restart(self):
        self.log("重启程序...")
        self.clear_log()
        self.rows, self.cols = 4, 4
        self.board = []
        self.current_color = 0
        self.initial_cow = None
        self.placed_cows = []
        self.extra_cows = []
        self.total_cows = 0
        self.show_size_stage()

if __name__ == "__main__":
    root = tk.Tk()
    app = CowPuzzleGUI(root)
    root.mainloop()