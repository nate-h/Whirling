#Copyright 2006 DR0ID <dr0id@bluewin.ch> http://mypage.bluewin.ch/DR0ID
#
#
#
"""
gradients demo
"""

__author__ = "$Author: DR0ID $"
__version__= "$Revision: 106 $"
__date__   = "$Date: 2007-08-09 17:43:42 +0200 (Do, 09 Aug 2007) $"


import pygame
import math
import gradients
##from gradients import gradient
from gradients import genericFxyGradient
import random



def main():
        pygame.init()
        screen = pygame.display.set_mode((800, 700), pygame.SRCALPHA)
        bgd = pygame.Surface(screen.get_size())
        bgd.blit(gradients.vertical(bgd.get_size(), (227, 200, 53, 255), (157, 116, 2, 255)), (0, 0))
        bgd.fill((128,)*3)
        screen.blit(bgd, (0, 0))
        pygame.key.set_repeat(500, 30)

        def f1(x):
            return x
        def f2(x):
            return 0.49*math.cos(10*x)+0.5
        def f3(x):
            return 0.49*math.sin(100*x)+0.5
        def f4(x):
            return math.exp(x)
        def f5(x):
            return x*x
        def f6(x):
            return math.cos(1.5*x)
        def f7(x):
            return math.sqrt(x)
        def f8(x):
            return x % 5
        def f9(x):
            return math.exp(-x/10.)*math.sin(x)
        def f10(x):
            return math.ceil(x/10.)
        def f11(x):
            return math.exp(x-10)+math.exp(-x-10)
        def f12(x):
            return x**2-x**4
        def f13(x):
            return 10*x+10
        def f14(x):
            if x < -math.pi/2.:
                return 0
            elif x > math.pi/2:
                return 2
            else:
                return math.sin(x)+1



        def expf(x,y=1):
            return math.sin(15*y-math.sin(15*x))*math.cos(15*x-math.cos(15*y))*3

        types  = ["line", "circle", "rect"]
        modes  = [0, 1, 2, 3, 4, 5]
        type   = 0
        mode   = 0
        funcs  = [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14]
        rf     = 1
        gf     = 1
        bf     = 1
        af     = 0
        spoint = (300, 500)
        epoint = (320, 640)
        scol   = (0, 255, 0, 100)
        ecol   = (100, 0, 50, 255)
        offset = (0, 0)

        pygame.display.set_caption( "mode:"+str(modes[mode])+
                                    " type:"+str(types[type])+
                                    " rf:"+str(rf)+
                                    " gf:"+str(gf)+
                                    " bf:"+str(bf)+
                                    " af:"+str(af)+
                                    "    keys: r,g,b,a,  t,m, ctrl+click"
                                    )
        running = True
        changed = True
        while running:
            event = pygame.event.wait()
            if pygame.QUIT==event.type:
                running = False
            elif pygame.KEYDOWN == event.type:
                if event.key == pygame.K_ESCAPE:#pygame.K_ESCAPE == event.key:
                    running = False
                elif event.key == pygame.K_t:
                    type += 1
                    type %= len(types)
                elif event.key == pygame.K_m:
                    mode += 1
                    mode %= len(modes)
                elif event.key == pygame.K_r:
                    rf += 1
                    rf %= len(funcs)
                elif event.key == pygame.K_g:
                    gf += 1
                    gf %= len(funcs)
                elif event.key == pygame.K_b:
                    bf += 1
                    bf %= len(funcs)
                elif event.key == pygame.K_a:
                    af += 1
                    af %= len(funcs)
                elif event.key == pygame.K_SPACE:
                    rint = random.randint
                    scol = (rint(1,254), rint(1,254), rint(1,254), rint(1,254))
                    ecol = (rint(1,254), rint(1,254), rint(1,254), rint(1,254))
                elif event.key == pygame.K_DOWN:
                    offset = (offset[0], offset[1]+1)
                elif event.key == pygame.K_UP:
                    offset = (offset[0], offset[1]-1)
                elif event.key == pygame.K_LEFT:
                    offset = (offset[0]-1, offset[1])
                elif event.key == pygame.K_RIGHT:
                    offset = (offset[0]+1, offset[1])
                changed = True
            elif pygame.MOUSEBUTTONDOWN == event.type:
                if pygame.key.get_mods()&pygame.KMOD_CTRL:
                    spoint = list(pygame.mouse.get_pos())
                else:
                    epoint = list(pygame.mouse.get_pos())
                changed = True

            if changed:
                changed = False
                mode_str = []
                if gradients.BLEND_MODES_AVAILABLE:
                    mode_str = ["normal", "add", "sub", "mult", "min", "max"]
                else:
                    mode_str = ["normal"]*6
                pygame.display.set_caption( "mode:"+mode_str[modes[mode]]+
                                            " type:"+str(types[type])+
                                            " rf:"+str(rf)+
                                            " gf:"+str(gf)+
                                            " bf:"+str(bf)+
                                            " af:"+str(af)+
                                            "    keys: r,g,b,a,  t,m, ctrl+click"+
                                            " space: chg color"
                                            )
                screen.fill((50,50,50))
                screen.blit(bgd, (0,0))
# genericFxyGradient
                #genericFxyGradient(screen, pygame.Rect(600,100,195,200), (0,100,200),(255,50,100), expf, (-2,2), (-2,2))
                # gradient
                func = gradients.draw_gradient
                if types[type]=="circle":
                    func = gradients.draw_circle
                elif types[type]=="rect":
                    func = gradients.draw_squared
                func(screen, spoint,epoint, scol, ecol, funcs[rf], funcs[gf], funcs[bf], funcs[af], modes[mode])
                
                pygame.draw.line(screen, (255,0,255), spoint, epoint)

                print( "startcolor:",scol)
                print( "endcolor", ecol)
                print( "startpoint", spoint)
                print( "endpoint", epoint)
                print( "------------------")
                screen.blit(gradients.horizontal((198, 198), scol, ecol), (1,1))
                screen.blit(gradients.vertical((198,198), scol, ecol), (201, 1))
                screen.blit(gradients.radial(99, scol, ecol), (401, 1))
                screen.blit(gradients.squared(198, scol, ecol), (601, 1))
                
                screen.blit(gradients.horizontal_func((198, 198), scol, ecol, funcs[rf], funcs[gf], funcs[bf], funcs[af]), (1,201))
                screen.blit(gradients.vertical_func((198,198), scol, ecol, funcs[rf], funcs[gf], funcs[bf], funcs[af]), (201, 201))
                screen.blit(gradients.radial_func(99, scol, ecol, funcs[rf], funcs[gf], funcs[bf], funcs[af]), (401, 201))
                screen.blit(gradients.squared_func(198, scol, ecol, funcs[rf], funcs[gf], funcs[bf], funcs[af], offset), (601, 201))
                
                screen.blit(gradients.chart(spoint, epoint, scol, ecol, funcs[rf], funcs[gf], funcs[bf], funcs[af]), (0,700-257))

                screen.blit(gradients.radial_func_offset(99, scol, ecol, funcs[rf], funcs[gf], funcs[bf], funcs[af], offset=offset), (601, 401))
                
                pygame.display.flip()
                
            
        pygame.quit()
    
        



if __name__ == '__main__':
##    import profile
##    profile.run('main()')
    main()