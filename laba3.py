import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk
import math
import re


canvas_img = None       
svg_segments = []       

BG_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)


def dda_line(img, x1, y1, x2, y2, color=LINE_COLOR):
    x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        if 0 <= x1 < img.width and 0 <= y1 < img.height:
            img.putpixel((x1, y1), color)
        return
    x_inc = dx / steps
    y_inc = dy / steps
    x, y = float(x1), float(y1)
    for _ in range(steps + 1):
        px, py = int(round(x)), int(round(y))
        if 0 <= px < img.width and 0 <= py < img.height:
            img.putpixel((px, py), color)
        x += x_inc
        y += y_inc


def bresenham_real(img, x0, y0, x1, y1, color=LINE_COLOR):
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx = x1 - x0
    dy = y1 - y0
    steep = abs(dy) > abs(dx)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
    dx = x1 - x0
    dy = y1 - y0
    if dx == 0:
        px, py = (y0, x0) if steep else (x0, y0)
        if 0 <= px < img.width and 0 <= py < img.height:
            img.putpixel((px, py), color)
        return
    step_y = 1 if dy >= 0 else -1
    dy = abs(dy)
    error = dy / dx - 0.5
    y = y0
    for x in range(x0, x1 + 1):
        px, py = (y, x) if steep else (x, y)
        if 0 <= px < img.width and 0 <= py < img.height:
            img.putpixel((px, py), color)
        if error >= 0:
            y += step_y
            error -= 1
        error += dy / dx


def bresenham_int(img, x0, y0, x1, y1, color=LINE_COLOR):
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx = x1 - x0
    dy = y1 - y0
    steep = abs(dy) > abs(dx)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
    dx = x1 - x0
    dy = y1 - y0
    if dx == 0:
        px, py = (y0, x0) if steep else (x0, y0)
        if 0 <= px < img.width and 0 <= py < img.height:
            img.putpixel((px, py), color)
        return
    step_y = 1 if dy >= 0 else -1
    dy = abs(dy)
    error = 2 * dy - dx
    y = y0
    for x in range(x0, x1 + 1):
        px, py = (y, x) if steep else (x, y)
        if 0 <= px < img.width and 0 <= py < img.height:
            img.putpixel((px, py), color)
        if error > 0:
            y += step_y
            error -= 2 * dx
        error += 2 * dy


def builtin_line(img, x1, y1, x2, y2, color=LINE_COLOR):
    draw = ImageDraw.Draw(img)
    draw.line([(x1, y1), (x2, y2)], fill=color, width=1)



def pentagram_edges(cx, cy, radius, angle_deg):
    points = []
    for i in range(5):
        a = math.radians(angle_deg + i * 72)
        x = cx + radius * math.cos(a)
        y = cy - radius * math.sin(a)
        points.append((x, y))

    order = [0, 2, 4, 1, 3, 0]
    edges = []
    for i in range(5):
        p1 = points[order[i]]
        p2 = points[order[i + 1]]
        edges.append((p1, p2))
    return edges




def create_canvas():
    global canvas_img
    try:
        w = int(canvas_w_entry.get())
        h = int(canvas_h_entry.get())
    except ValueError:
        return
    canvas_img = Image.new("RGB", (w, h), BG_COLOR)
    update_preview()


def clear_canvas():
    global canvas_img
    if canvas_img is None:
        return
    canvas_img = Image.new("RGB", canvas_img.size, BG_COLOR)
    update_preview()


def get_pentagram_params():
    cx = canvas_img.width / 2
    cy = canvas_img.height / 2
    radius = float(radius_entry.get())
    angle = float(angle_entry.get())
    return pentagram_edges(cx, cy, radius, angle)


def draw_with(algorithm_fn):
    if canvas_img is None:
        return
    clear_canvas()
    edges = get_pentagram_params()
    for (x1, y1), (x2, y2) in edges:
        algorithm_fn(canvas_img, x1, y1, x2, y2)
    update_preview()


def draw_dda():
    draw_with(dda_line)


def draw_bresenham_real():
    draw_with(bresenham_real)


def draw_bresenham_int():
    draw_with(bresenham_int)


def draw_builtin():
    draw_with(builtin_line)


def update_preview():
    display_img = canvas_img.copy()
    display_img.thumbnail((600, 600))
    tk_img = ImageTk.PhotoImage(display_img)
    preview_label.configure(image=tk_img)
    preview_label.image = tk_img


def save_bmp():
    if canvas_img is None:
        return
    path = filedialog.asksaveasfilename(defaultextension=".bmp")
    if not path:
        return
    canvas_img.save(path)


def save_pbm():
    if canvas_img is None:
        return
    path = filedialog.asksaveasfilename(defaultextension=".pbm")
    if not path:
        return
    width, height = canvas_img.size
    with open(path, "w") as f:
        f.write(f"P3\n{width} {height}\n255\n")
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b = canvas_img.getpixel((x, y))
                row.append(f"{r} {g} {b}")
            f.write(" ".join(row) + "\n")


def load_svg():
    global svg_segments
    path = filedialog.askopenfilename(filetypes=[("SVG files", "*.svg")])
    if not path:
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    segments = []
    for m in re.finditer(
        r'<line[^>]*x1="([\d.\-]+)"[^>]*y1="([\d.\-]+)"[^>]*x2="([\d.\-]+)"[^>]*y2="([\d.\-]+)"',
        content
    ):
        x1, y1, x2, y2 = map(float, m.groups())
        segments.append((x1, y1, x2, y2))

    svg_segments = segments
    if segments:
        svg_status_label.configure(text=f"SVG загружен ({len(segments)} отрезков)", fg="green")
    else:
        svg_status_label.configure(text="Отрезки не найдены", fg="red")


def draw_svg():
    if canvas_img is None or not svg_segments:
        return
    clear_canvas()
    for x1, y1, x2, y2 in svg_segments:
        builtin_line(canvas_img, x1, y1, x2, y2)
    update_preview()




root = tk.Tk()
root.title("Лабораторная работа №3 — Растеризация отрезков (пентаграмма)")
root.geometry("1300x800")
root.state('zoomed')

top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)


canvas_group = tk.LabelFrame(top_frame, text="Параметры холста", padx=10, pady=10)
canvas_group.pack(side=tk.LEFT, padx=5, fill=tk.Y)

tk.Label(canvas_group, text="Ширина:").grid(row=0, column=0, sticky="e")
canvas_w_entry = tk.Entry(canvas_group, width=8)
canvas_w_entry.insert(0, "600")
canvas_w_entry.grid(row=0, column=1, padx=5)

tk.Label(canvas_group, text="Высота:").grid(row=0, column=2, sticky="e")
canvas_h_entry = tk.Entry(canvas_group, width=8)
canvas_h_entry.insert(0, "600")
canvas_h_entry.grid(row=0, column=3, padx=5)

tk.Button(canvas_group, text="Создать холст", command=create_canvas).grid(row=0, column=4, padx=10)



svg_group = tk.LabelFrame(top_frame, text="Загрузка SVG", padx=10, pady=10)
svg_group.pack(side=tk.LEFT, padx=5, fill=tk.Y)

svg_status_label = tk.Label(svg_group, text="SVG не загружен", fg="red")

tk.Button(svg_group, text="Загрузить SVG", command=load_svg).pack(side=tk.LEFT)
svg_status_label.pack(side=tk.LEFT, padx=10)



shape_group = tk.LabelFrame(root, text="Параметры пентаграммы", padx=10, pady=10)
shape_group.pack(side=tk.TOP, fill=tk.X, padx=10)

tk.Label(shape_group, text="Радиус R:").grid(row=0, column=0, sticky="e")
radius_entry = tk.Entry(shape_group, width=8)
radius_entry.insert(0, "250")
radius_entry.grid(row=0, column=1, padx=5)

tk.Label(shape_group, text="Угол вершины (°):").grid(row=0, column=2, sticky="e")
angle_entry = tk.Entry(shape_group, width=8)
angle_entry.insert(0, "90")
angle_entry.grid(row=0, column=3, padx=5)



algo_group = tk.LabelFrame(root, text="Алгоритмы растеризации", padx=10, pady=10)
algo_group.pack(side=tk.TOP, fill=tk.X, padx=10)

tk.Button(algo_group, text="ЦДА", command=draw_dda, width=20).pack(side=tk.LEFT, padx=5)
tk.Button(algo_group, text="Брезенхем (вещ.)", command=draw_bresenham_real, width=20).pack(side=tk.LEFT, padx=5)
tk.Button(algo_group, text="Брезенхем (цел.)", command=draw_bresenham_int, width=20).pack(side=tk.LEFT, padx=5)
tk.Button(algo_group, text="Встроенные средства", command=draw_builtin, width=20).pack(side=tk.LEFT, padx=5)



control_group = tk.LabelFrame(root, text="Управление", padx=10, pady=10)
control_group.pack(side=tk.TOP, fill=tk.X, padx=10)

tk.Button(control_group, text="Сохранить BMP", command=save_bmp, width=20).pack(side=tk.LEFT, padx=5)
tk.Button(control_group, text="Сохранить PBM", command=save_pbm, width=20).pack(side=tk.LEFT, padx=5)
tk.Button(control_group, text="Очистить холст", command=clear_canvas, width=20).pack(side=tk.LEFT, padx=5)
tk.Button(control_group, text="Нарисовать SVG", command=draw_svg, width=20).pack(side=tk.LEFT, padx=5)

preview_label = tk.Label(root, bg="gray")
preview_label.pack(pady=10)

root.mainloop()