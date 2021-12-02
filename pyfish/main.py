from tkinter import Tk, Canvas
from random import randint, random
from math import pi, cos, sin, atan2
from time import time, sleep


def dist(x1, y1, x2, y2):
    dx, dy = x1 - x2, y1 - y2
    return (dx * dx + dy * dy) ** .5

def dangle(x, y, dir, fx, fy, fen):
    if x == fx and y == fy:
        return 10
    dx, dy = x - fx, y - fy
    target = (atan2(dy, dx) + pi) % (2 * pi)
    delta = (target - dir) % (2 * pi) - pi
    return delta


class Fish:
    def __init__(self, x, y, dir):
        self.x, self.y = x, y
        self.dir = dir
        self.speed = 500

    def move(self):
        self.x += cos(self.dir) * 0.01 * self.speed
        self.y += sin(self.dir) * 0.01 * self.speed

    def update_dir(self, angle_max, target):
        if target is None:
            return
        delta_teta = (target - self.dir) % (2 * pi)
        if delta_teta < pi:
            # on augmente l'angle
            if delta_teta > angle_max:
                self.dir += angle_max
            else:
                self.dir = target
        else:
            # on diminue l'angle
            if delta_teta - 2 * pi < -angle_max:
                self.dir -= angle_max
            else:
                self.dir = target
        self.dir = self.dir % (2*pi)

    def avoid_border(self, width, height, fen):
        limit = 30
        if limit < self.x < width - limit and limit < self.y < height - limit:
            return
        angle_max = pi / 10
        self.dir = self.dir % (2*pi)
        self.dir = self.dir - ((2*pi) if self.dir > pi else 0)
        if self.x < limit and self.y < limit:
            target = -pi/4
        elif self.x < limit and self.y > height - limit:
            target = pi/4
        elif self.x > width - limit and self.y < limit:
            target = -3*pi/4
        elif self.x > width - limit and self.y > height - limit:
            target = 3*pi/4
        elif self.x < limit:
            target = 5*pi/12 if self.dir > 0 else -5*pi/12
            #fen.debug.add(fen.can.create_line(self.x, self.y, self.x + cos(target) * 30, self.y + sin(target) * 30, fill="red"))
            if abs(self.dir) < pi/2 and self.dir - target <= 0:
                return
        elif self.x > width - limit:
            target = 7*pi/12 if self.dir > 0 else -7*pi/12
            #fen.debug.add(fen.can.create_line(self.x, self.y, self.x + cos(target) * 30, self.y + sin(target) * 30, fill="red"))
            if abs(self.dir) > pi/2 and self.dir - target >= 0:
                return
        elif self.y < limit:
            target = pi/12 if abs(self.dir) < pi/2 else 11*pi/12
            #fen.debug.add(fen.can.create_line(self.x, self.y, self.x + cos(target) * 30, self.y + sin(target) * 30, fill="red"))
            if self.dir > 0 and self.dir - target >= 0:
                return
        elif self.y > height - limit:
            target = -pi/12 if abs(self.dir) < pi/2 else -11*pi/12
            #fen.debug.add(fen.can.create_line(self.x, self.y, self.x + cos(target) * 30, self.y + sin(target) * 30, fill="red"))
            if self.dir < 0 and self.dir - target <= 0:
                return
        else:
            target = None
            angle_max = None
        self.update_dir(angle_max, target)

    def avoid_col(self, fishset, fen):
        angle_max = pi / 18
        near = tuple((f.x, f.y) for f in fishset.values() if dist(f.x, f.y, self.x, self.y) < 60 and abs(
            dangle(self.x, self.y, self.dir, f.x, f.y, fen)) > pi * .2 and f != self)

        if near:
            closer = min(near, key=lambda x: dist(x[0], x[1], self.x, self.y))
            d = dist(*closer, self.x, self.y)
            prox = max((d - 30), 0) / 30
            #self.speed = 300 + 200 * prox
            dx, dy = self.x - closer[0], self.y - closer[1]
            target = (atan2(dy, dx) + pi) % (2 * pi)
            delta_teta = (target - self.dir) % (2 * pi)
            if delta_teta < pi:
                # on diminue l'angle
                self.dir -= angle_max * (1 - prox)
            else:
                # on augmente l'angle
                self.dir += angle_max * (1 - prox)
        else:
            self.speed = 500


    def dir_mean_dir(self, fishset, fen):
        angle_max = pi / 100
        near = tuple(f.dir for f in fishset.values() if dist(f.x, f.y, self.x, self.y) < 100 and abs(
            dangle(self.x, self.y, self.dir, f.x, f.y, fen)) > pi *.1)
        if len(near) > 1:
            xlist = tuple(cos(x) for x in near)
            ylist = tuple(sin(x) for x in near)
            xmoy = sum(xlist)/len(xlist)
            ymoy = sum(ylist)/len(ylist)
            target = atan2(ymoy, xmoy)
            self.update_dir(angle_max, target)


    def dir_center(self, fishset, fen):
        angle_max = pi/30
        near = tuple((f.x, f.y) for f in fishset.values() if dist(f.x, f.y, self.x, self.y) < 100 and abs(
            dangle(self.x, self.y, self.dir, f.x, f.y, fen)) > pi * .3)
        if len(near) > 1:
            s = tuple(sum(x)/len(near) for x in zip(*near))
            dx, dy = self.x - s[0], self.y - s[1]
            target = (atan2(dy, dx) + pi) % (2 * pi)
            #fen.debug.add(fen.can.create_line(self.x, self.y, self.x + cos(target) * 30, self.y + sin(target) * 30, fill="red"))
            #fen.debug.add(fen.can.create_line(self.x, self.y, self.x + cos(self.dir) * 50, self.y + sin(self.dir) * 50, fill = "green"))
            self.update_dir(angle_max, target)

    def target_food(self, food):
        if not food:
            return 100, 100
        closer = min(food, key=lambda x: dist(food[x][0], food[x][1], self.x, self.y))
        x, y = food[closer][0], food[closer][1]
        dx, dy = self.x - x, self.y - y
        target = (atan2(dy, dx) + pi) % (2 * pi)
        self.update_dir(pi/50, target)

        return dist(x, y, self.x, self.y), closer

    def get_oval_coords(self):
        long = 20
        larg = 5
        s, c = sin(self.dir), cos(self.dir)
        long_sin, long_cos = long * s, long * c
        larg_sin, larg_cos = larg * s, larg * c
        x1, y1 = self.x + long_cos, self.y + long_sin
        x2, y2 = self.x + larg_sin, self.y - larg_cos
        x4, y4 = self.x - larg_sin, self.y + larg_cos
        return x1, y1, x2, y2, x4, y4


class App(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.fen_width = 700
        self.fen_height = 700
        self.geometry(str(self.fen_width) + "x" + str(self.fen_height) + "+5+5")

        self.can = Canvas(self, width=self.fen_width, height=self.fen_height, bg="lightblue")
        self.can.pack()

        self.food = dict()
        self.fishset = dict()
        self.load_fish()

        self.keyboard = set()
        self.bind("<KeyPress-space>", self.pause)
        self.paused = False
        self.debug = set()
        self.DEBUG = False
        self.bind("<Right>", self.next)
        self.bind("<Escape>", self.clean)
        self.bind("<Configure>", self.on_resize)
        self.bind("<Delete>", self.fullscreen)
        self.bind("<Button-1>", self.clic)
        self.full = True

        self.animate()

    def clic(self, evt):
        self.food[self.can.create_oval(evt.x-5, evt.y-5, evt.x+5, evt.y+5, outline="", fill="red")] = (evt.x, evt.y)

    def fullscreen(self, evt):
        self.full = not self.full
        self.attributes("-fullscreen", self.full)
    def on_resize(self, evt):
        self.fen_width = evt.width
        self.fen_height = evt.height
        self.can.config(width=evt.width, height=evt.height)
    def clean(self, evt):
        for i in self.debug:
            self.can.delete(i)
        self.debug = set()
    def pause(self, evt):
        self.paused = not self.paused
        if not self.paused:
            self.animate()
    def next(self, evt):
        self.next_frame()

    def update_fishset(self):
        for f in self.fishset:
            self.can.coords(f, *self.fishset[f].get_oval_coords())

    def load_fish(self):
        for _ in range(50):
            self.fishset[self.can.create_polygon(0, 0, width=2, fill="black")] = Fish(randint(0, self.fen_width),
                                                                                      randint(0, self.fen_height),
                                                                                      random() * 2 * pi)
        self.update_fishset()

    def next_frame(self):
        for f in self.fishset.values():
            t0 = time()
            f.move()
            t1 = time()
            f.dir_mean_dir(self.fishset, self)
            t2 = time()
            f.dir_center(self.fishset, self)
            t3 = time()
            d, id = f.target_food(self.food)
            f.avoid_col(self.fishset, self)
            t4 = time()
            f.avoid_border(self.fen_width, self.fen_height, self)
            t5 = time()
            if d < 20:
                self.food.pop(id)
                self.can.delete(id)
        self.update_fishset()

    def animate(self):
        self.next_frame()
        if not self.paused:
            self.after(15, self.animate)


app = App()
app.mainloop()
