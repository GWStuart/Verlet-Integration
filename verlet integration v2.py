import pygame
import sys
import math
import copy

pygame.init()

WIDTH, HEIGHT = (1280, 720)
win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Verlet Integration")
clock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 15)

bounce = True  # You can change this
stiffness = 10  # 1 is kinda like soft body physics if you make a box or something
physics = False
show_points = True
show_options = False
line_spacing = 20


class Point:
    BOUNCE = 0.9
    GRAVITY = 0.5
    FRICTION = 0.999

    def __init__(self, pos, old_pos, pinned=False):
        self.x, self.y = pos
        self.old_x, self.old_y = old_pos
        self.pinned = pinned
        self.radius = 5
        self.colour = (255, 255, 255)

    def draw(self):
        if not self.pinned:
            pygame.draw.circle(win, self.colour, (self.x, self.y), self.radius)
        else:
            pygame.draw.circle(win, (255, 0, 0), (self.x, self.y), self.radius)


class Stick:
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
        self.length = math.dist((self.p0.x, self.p0.y), (self.p1.x, self.p1.y))
        self.width = 3

    def draw(self):
        pygame.draw.line(win, (0, 0, 0), (self.p0.x, self.p0.y), (self.p1.x, self.p1.y), self.width)

    def touching_line(self, p0, p1):
        if p0[0] == p1[0] or self.p0.x == self.p1.x:
            return False
        m1 = (p0[1] - p1[1]) / (p0[0] - p1[0])
        m2 = (self.p0.y - self.p1.y) / (self.p0.x - self.p1.x)
        c1 = p0[1] - (m1 * p0[0])
        c2 = self.p0.y - (m2 * self.p0.x)
        if m1 == m2:
            return False
        x = (c2 - c1) / (m1 - m2)
        if max(p0[0], p1[0]) >= x >= min(p0[0], p1[0]) and max(self.p0.x, self.p1.x) >= x >= min(self.p0.x, self.p1.x):
            return True


def update_points():
    for p in points:
        if not p.pinned:
            vx = (p.x - p.old_x) * Point.FRICTION
            vy = (p.y - p.old_y) * Point.FRICTION

            p.old_x = p.x
            p.old_y = p.y
            p.x += vx
            p.y += vy
            p.y += Point.GRAVITY


def constrain_points():
    for p in points:
        if not p.pinned:
            vx = (p.x - p.old_x) * Point.FRICTION
            vy = (p.y - p.old_y) * Point.FRICTION

            if p.x > WIDTH:
                p.x = WIDTH
                p.old_x = p.x + (vx * Point.BOUNCE)
            elif p.x < 0:
                p.x = 0
                p.old_x = p.x + (vx * Point.BOUNCE)
            elif p.y > HEIGHT:
                p.y = HEIGHT
                p.old_y = p.y + (vy * Point.BOUNCE)
            elif p.y < 0:
                p.y = 0
                p.old_y = p.y + (vy * Point.BOUNCE)


def update_sticks():
    for s in sticks:
        dx = s.p1.x - s.p0.x
        dy = s.p1.y - s.p0.y
        distance = math.sqrt(dx * dx + dy * dy)
        difference = s.length - distance
        percent = difference / distance / 2
        offset_x = dx * percent
        offset_y = dy * percent

        if not s.p0.pinned:
            s.p0.x -= offset_x
            s.p0.y -= offset_y
        if not s.p1.pinned:
            s.p1.x += offset_x
            s.p1.y += offset_y


def update(stiffness=3):
    update_points()

    for i in range(stiffness):
        update_sticks()
        if bounce:
            constrain_points()

    for s in sticks:
        s.draw()
        if min(s.p0.y, s.p1.y) > 2000:
            sticks.remove(s)
    if show_points:
        for p in points:
            p.draw()


def create_grid(start, rows, columns, spacing, pin=False, pin_spacing=4):
    row_list = []
    for y in range(rows):
        row = []
        for x in range(columns):
            if y == 0 and pin and (x % pin_spacing == 0 or x == columns - 1):
                row.append(Point((start[0] + x * spacing, start[1] + y * spacing),
                                 (start[0] + x * spacing, start[1] + y * spacing), pinned=pin))
            else:
                row.append(Point((start[0] + x * spacing, start[1] + y * spacing),
                                 (start[0] + x * spacing, start[1] + y * spacing)))
            points.append(row[-1])
        row_list.append(row)
        for i in range(len(row) - 1):
            sticks.append(Stick(row[i], row[i+1]))
    for a in range(len(row_list[0])):
        [sticks.append(Stick(row_list[b][a], row_list[b+1][a])) for b in range(len(row_list) - 1)]


points = []
sticks = []

line_start = None
line_last_point = None
previous_pos = pygame.mouse.get_pos()

# create_grid((20, 20), 24, 50, 25, pin=True)  # big cloth
# create_grid((500, 10), 40, 50, 5, pin=True)  # cool compact cloth

run = True
while run:
    pressed = pygame.mouse.get_pressed(3)
    mouse = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                for p in points:
                    if math.dist(mouse, (p.x, p.y)) < p.radius:
                        points.remove(p)
            if event.key == pygame.K_2:
                if stiffness < 25:
                    stiffness += 1
            if event.key == pygame.K_1:
                if stiffness > 1:
                    stiffness -= 1
            if event.key == pygame.K_f or event.key == pygame.K_o:
                if show_options:
                    show_options = False
                else:
                    show_options = True
            if event.key == pygame.K_c:
                points = list()
                sticks = list()
                physics = False
                show_points = True
            if event.key == pygame.K_b:
                if bounce:
                    bounce = False
                else:
                    bounce = True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_SPACE:
                if physics:
                    physics = False
                    line_start = None
                    show_points = True
                else:
                    physics = True
                    line_start = None
            if event.key == pygame.K_h:
                if show_points:
                    show_points = False
                else:
                    show_points = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for p in points:
                    if math.dist((p.x, p.y), mouse) <= p.radius:
                        if not physics:
                            line_start = p
                            break
                else:
                    if not physics:
                        points.append(Point(mouse, mouse))
                    else:
                        line_start = mouse
            elif event.button == 3:
                for p in points:
                    if math.dist((p.x, p.y), mouse) < p.radius:
                        if p.pinned:
                            p.pinned = False
                        else:
                            p.pinned = True
                        break

    win.fill((90, 105, 242))

    if physics:
        update(stiffness=stiffness)
        if line_start:
            pressed = pygame.mouse.get_pressed(3)
            if pressed[0]:
                pygame.draw.line(win, (255, 0, 0), line_start, mouse)
            else:
                for s in sticks:
                    if s.touching_line(line_start, mouse):
                        sticks.remove(s)
                line_start = None
    else:
        if line_start:
            pressed = pygame.mouse.get_pressed(3)
            if pressed[0]:
                pygame.draw.line(win, (0, 0, 0), (line_start.x, line_start.y), mouse, 3)
            else:
                for p in points:
                    if math.dist((p.x, p.y), mouse) < p.radius and p != line_start:
                        sticks.append(Stick(line_start, p))
                        break
                line_start = None
        for s in sticks:
            s.draw()
        if show_points:
            for p in points:
                p.draw()

        if keys[pygame.K_l]:
            if line_last_point:
                if math.dist(line_last_point, mouse) > line_spacing:
                    line_last_point = mouse
                    points.append(Point(mouse, mouse))
                    sticks.append(Stick(points[-1], points[-2]))
            else:
                line_last_point = mouse
                points.append(Point(mouse, mouse))
        else:
            line_last_point = None

    if show_options:
        win.blit(font.render(f"Physics (space): {physics}", True, (255, 255, 255)), (5, 5))
        win.blit(font.render(f"Bounce (b): {bounce}", True, (255, 255, 255)), (5, 30))
        win.blit(font.render(f"Show Points (h): {show_points}", True, (255, 255, 255)), (5, 60))
        win.blit(font.render(f"Stiffness (increase 2, decrease 1) {stiffness}:", True, (255, 255, 255)), (5, 85))
        win.blit(font.render("--Other Keys---", True, (255, 255, 255)), (5, 110))
        win.blit(font.render("clear (c)", True, (255, 255, 255)), (5, 135))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
