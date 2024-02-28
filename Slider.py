import pygame


class Slider:
    def __init__(self, x, y, w, h, min_val=0, max_val=1, initial_val=1):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.grabbed = False
        self.knob_rect = pygame.Rect(x + (w - 10) * ((initial_val - min_val) / (max_val - min_val)), y, 10, h)

    def draw(self, win):
        pygame.draw.rect(win, (200, 200, 200), self.rect)
        pygame.draw.rect(win, (150, 150, 150), self.knob_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.knob_rect.collidepoint(event.pos):
                self.grabbed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.grabbed = False
        elif event.type == pygame.MOUSEMOTION and self.grabbed:
            self.knob_rect.x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width - self.knob_rect.width))
            self.val = self.min_val + ((self.knob_rect.x - self.rect.x) / (self.rect.width - self.knob_rect.width)) * (
                        self.max_val - self.min_val)
            return True
        return False
