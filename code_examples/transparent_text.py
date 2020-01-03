import pygame as pg


pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((640, 480))
font = pg.font.Font(None, 64)
blue = pg.Color('dodgerblue1')
sienna = pg.Color('sienna2')

# Render the text surface.
txt_surf = font.render('transparent text', True, blue)
# Create a transparent surface.
alpha_img = pg.Surface(txt_surf.get_size(), pg.SRCALPHA)
# Fill it with white and the desired alpha value.
alpha_img.fill((255, 255, 255, 140))
# Blit the alpha surface onto the text surface and pass BLEND_RGBA_MULT.
txt_surf.blit(alpha_img, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

done = False
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True

    screen.fill((30, 30, 30))
    pg.draw.rect(screen, sienna, (105, 40, 130, 200))
    screen.blit(txt_surf, (30, 60))
    pg.display.flip()
    clock.tick(30)

pg.quit()