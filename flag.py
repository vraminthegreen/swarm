import pygame
from stage import Stage

FLAG_SIZE = 12
FLAG_POLE_COLOR = (200, 200, 200)

FLAG_TYPE_NORMAL = "normal"
FLAG_TYPE_FAST = "fast"
FLAG_TYPE_STOP = "stop"
FLAG_TYPE_ARCHER = "archer"


class Flag(Stage):
    """Visual representation of a flag on the stage."""

    def __init__(self, pos=None, color=(255, 100, 100), number=None, flag_type=FLAG_TYPE_NORMAL):
        super().__init__()
        self.pos = pos
        self.color = color
        self.number = number
        self.flag_type = flag_type

    def _draw_flag_at(self, screen, position, number=None):
        fx, fy = position
        pole_top = (fx, max(0, fy - 10))
        pygame.draw.line(screen, FLAG_POLE_COLOR, position, pole_top)

        if self.flag_type == FLAG_TYPE_FAST:
            left1 = pole_top
            right1 = (pole_top[0] + FLAG_SIZE // 2, pole_top[1] + FLAG_SIZE // 2)
            bottom1 = (pole_top[0], pole_top[1] + FLAG_SIZE)
            left2 = (pole_top[0] + FLAG_SIZE // 2, pole_top[1])
            right2 = (pole_top[0] + FLAG_SIZE, pole_top[1] + FLAG_SIZE // 2)
            bottom2 = (pole_top[0] + FLAG_SIZE // 2, pole_top[1] + FLAG_SIZE)
            pygame.draw.polygon(screen, self.color, [left1, right1, bottom1])
            pygame.draw.polygon(screen, self.color, [left2, right2, bottom2])
        elif self.flag_type == FLAG_TYPE_STOP:
            bar_height = 3
            gap = 2
            rect1 = pygame.Rect(pole_top[0], pole_top[1], FLAG_SIZE, bar_height)
            rect2 = pygame.Rect(
                pole_top[0], pole_top[1] + bar_height + gap, FLAG_SIZE, bar_height
            )
            pygame.draw.rect(screen, self.color, rect1)
            pygame.draw.rect(screen, self.color, rect2)
        elif self.flag_type == FLAG_TYPE_ARCHER:
            flag_points = [
                pole_top,
                (pole_top[0] + FLAG_SIZE, pole_top[1] + FLAG_SIZE // 2),
                (pole_top[0], pole_top[1] + FLAG_SIZE),
            ]
            pygame.draw.polygon(screen, self.color, flag_points)
            center = (pole_top[0] + FLAG_SIZE // 2, pole_top[1] + FLAG_SIZE // 2)
            pygame.draw.line(
                screen,
                FLAG_POLE_COLOR,
                (center[0] - 3, center[1]),
                (center[0] + 3, center[1]),
                1,
            )
            pygame.draw.line(
                screen,
                FLAG_POLE_COLOR,
                (center[0], center[1] - 3),
                (center[0], center[1] + 3),
                1,
            )
        else:
            flag_points = [
                pole_top,
                (pole_top[0] + FLAG_SIZE, pole_top[1] + FLAG_SIZE // 2),
                (pole_top[0], pole_top[1] + FLAG_SIZE),
            ]
            pygame.draw.polygon(screen, self.color, flag_points)
        if number is not None:
            font = pygame.font.Font(None, 16)
            text = font.render(str(number), True, (255, 255, 255))
            text_rect = text.get_rect(midleft=(pole_top[0] + FLAG_SIZE + 2, pole_top[1] + FLAG_SIZE // 2))
            screen.blit(text, text_rect)

    def _draw(self, screen):
        if self.pos is None:
            return
        self._draw_flag_at(screen, self.pos, self.number)

    def draw_icon(self, screen, idx, height, active=False):
        """Draw a small icon representation of this flag."""
        spacing = FLAG_SIZE * 2 + 20
        base_x = 20 + idx * spacing
        base_y = height - 5
        self._draw_flag_at(screen, (base_x, base_y), idx + 1)
        if active:
            rect = pygame.Rect(base_x - 4, base_y - 16, FLAG_SIZE + 12, FLAG_SIZE + 20)
            pygame.draw.rect(screen, (255, 255, 0), rect, 1)
