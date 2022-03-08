import random
from tkinter import Tk, Canvas
from cmath import sin, exp, log, tan, acos
from math import pi
import time
from itertools import product


class App(Tk):
    def __init__(self, unit=100):
        Tk.__init__(self)

        self.fen_width = 1500
        self.fen_height = 900
        self.geometry(str(self.fen_width) + "x" + str(self.fen_height) + "+5+5")
        self.bind("<Motion>", self.pointer)

        self.can = Canvas(self, width=self.fen_width, height=self.fen_height, bg="#000")
        self.can.pack()

        self.unit = unit
        self.near = []
        self.near_proj = []

        self.matrix = dict()

    def hex_2(self, hexa):
        if len(hexa) == 1:
            return "0" + hexa
        return hexa

    def get_color(self, pos, xmin, xmax, ymin, ymax):
        def f(x, xmin, xmax):
            return 255 * (x - xmin) / (xmax - xmin)

        def f2(x, xmin, xmax):
            return 85 * (x - xmin) / (xmax - xmin)

        x, y = pos
        r = int(255 - f(x, xmin, xmax))
        rh = self.hex_2(str(hex(r)[2:]))
        g = int(255 - f(y, ymin, ymax))
        gh = self.hex_2(str(hex(g)[2:]))
        b1 = int(f2(x, xmin, xmax))
        b2 = int(f2(y, ymin, ymax))
        bh = self.hex_2(str((hex(b1 + b2))[2:]))
        return "#" + rh + gh + bh

    def center(self, pos):
        return pos[0] * self.unit + self.fen_width / 2, -pos[1] * self.unit + self.fen_height / 2
    def uncenter(self, pos):
        return (pos[0] - self.fen_width / 2) / self.unit, (pos[1] - self.fen_height / 2) / -self.unit

    def load_lines(self):
        for x in (k for k in range(int(-self.fen_width / 2 / self.unit), int(self.fen_width / 2 / self.unit + 1))):
            y = self.fen_height / 2 / self.unit
            xb, yb = self.center((x, y))
            self.can.create_line(xb, yb, xb, yb + self.fen_height, fill="#404040")
        for y in (k for k in range(int(-self.fen_height / 2 / self.unit), int(self.fen_height / 2 / self.unit + 1))):
            x = -self.fen_width / 2 / self.unit
            xb, yb = self.center((x, y))
            self.can.create_line(xb, yb, xb + self.fen_width, yb, fill="#404040")
        self.can.create_line(*self.center((0, -self.fen_height / 2)), *self.center((0, self.fen_height / 2)),
                             fill="white")
        self.can.create_line(*self.center((-self.fen_width, 0)), *self.center((self.fen_width, 0)), fill="white")

    def setup_points(self, xmin, xmax, ymin, ymax, density):
        x = xmin
        while x < xmax:
            y = ymin
            while y < ymax:
                xc, yc = self.center((x, y))
                color = self.get_color((x, y), xmin, xmax, ymin, ymax)
                self.matrix[(x, y)] = self.can.create_oval(xc - 3, yc - 3, xc + 3, yc + 3, fill=color, outline="")
                y += density
            x += density

    def load_targets(self):
        for point in self.matrix:
            target = self.apply(point[0], point[1])
            if target[0] is None:
                target = (1000000, 1000000)
            self.matrix[point] = (target, self.matrix[point])

    def replace(self, point):
        def getpos(x, a, b):
            return a + x * (b - a) / 500
        xa, ya = point
        xb, yb = self.matrix[point][0]
        xc, yc = self.center((getpos(self.state, xa, xb), getpos(self.state, ya, yb)))
        self.can.coords(self.matrix[point][1], xc - 3, yc - 3, xc + 3, yc + 3)

    def translate(self, new=False):
        if new:
            self.load_targets()
            self.state = 1
        for point in self.matrix:
            self.replace(point)
        if self.state < 500:
            self.state += 1
            self.after(16, self.translate)

    def pointer(self, evt):
        cx, cy = evt.x, evt.y
        if not self.near:
            # Premiere actualisation
            for tx, ty in product(range(cx-50, cx+51, 10), range(cy-50, cy+51, 10)):
                self.near.append(self.can.create_oval(tx-3, ty-3, tx+3, ty+3, outline="", fill="blue"))
        else:
            # On actualise juste les positions des points
            i = 0
            for tx, ty in product(range(cx-50, cx+51, 10), range(cy-50, cy+51, 10)):
                self.can.coords(self.near[i], tx-3, ty-3, tx+3, ty+3)
                i += 1

        if not self.near_proj:
            # Premiere actualisation
            for tx, ty in product(range(cx-50, cx+51, 10), range(cy-50, cy+51, 10)):
                x, y = self.center(self.apply(*self.uncenter((tx, ty))))
                self.near_proj.append(self.can.create_oval(x-3, y-3, x+3, y+3, outline="", fill="lightblue"))
        else:
            i = 0
            for tx, ty in product(range(cx-50, cx+51, 10), range(cy-50, cy+51, 10)):
                x, y = self.center(self.apply(*self.uncenter((tx, ty))))
                self.can.coords(self.near_proj[i], x-3, y-3, x+3, y+3)
                i += 1


    def apply(self, x, y):
        c = x + 1j * y
        try:
            r = self.funct(c)
        except:
            return None, None
        return r.real, r.imag

    def funct(self, c):
        ## REPLACE FUNCTION HERE
        return acos(c)


def enable_pointer():
    app.POINTER = True


app = App(300)
app.load_lines()
app.setup_points(-4, 4, -4, 4, 0.1)
app.translate(True)
app.mainloop()
