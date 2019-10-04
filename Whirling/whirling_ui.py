import pygame as pg

WHITE = (255, 255, 255)


class Button():
    def __init__(self, msg, action, rect, color=WHITE, font="Comic Sans MS", font_size=32):
        self.msg = msg
        self.color = color
        self.font = pg.font.SysFont(font, font_size)
        self.text_surf = self.font.render(self.msg, True, self.color)
        self.image_normal = pg.Surface((rect.w, rect.h))
        self.image_normal.fill(pg.Color('dodgerblue1'))
        self.image_hover = pg.Surface((rect.w, rect.h))
        self.image_hover.fill(pg.Color('lightskyblue'))
        self.action = action

        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=(rect.x, rect.y))
        # To center the text rect.
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def handle_event(self, event):

        # Motion.
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.image = self.image_hover
            else:
                self.image = self.image_normal

        # Clicking.
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.perform_action()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.text_surf, self.text_rect)

    def perform_action(self):
        self.action()


#####################################################

class ToggleButton(Button):
    def __init__(self, states, rect, color=WHITE, font="Comic Sans MS", font_size=32):
        self.states = states
        self.state = self.get_next_state()
        super(ToggleButton, self).__init__(
            self.state[0], self.state[1]['action'], rect, color, font, font_size)

    def perform_action(self):
        self.action()
        self.toggle_state()

    def get_next_state(self):
        if not hasattr(self, 'state') or self.state is None:
            return list(self.states.items())[0]
        raw_index = list(self.states.keys()).index(self.state[0])
        index = (raw_index + 1) % len(self.states)
        return list(self.states.items())[index]

    def toggle_state(self):
        self.state = self.get_next_state()
        self.msg = self.state[0]
        self.action = self.state[1]['action']
        self.text_surf = self.font.render(self.msg, True, self.color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
