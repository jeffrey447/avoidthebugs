import pygame
import sys
import os
import time
import random
# https://www.pygame.org/docs/tut/PygameIntro.html

pygame.init() # initialize the display window
pygame.mixer.init() # initialize the module that plays sounds

size = (width, height) = (800, 450)
scrn = pygame.display.set_mode(size)

highScore = 0

base_y = height-100

def get_files(dir):
    for (_, _, filenames) in os.walk(dir):
        return filenames

images = {}
for file in get_files('assets/images/'):
    name = os.path.splitext(file)[0]
    images[name] = pygame.image.load('assets/images/' + file)

sfx = {}
for file in get_files('assets/sfx/'):
    info = os.path.splitext(file)
    
    name = info[0]
    ext = info[1]

    path = 'assets/sfx/' + file
    
    if ext == '.ogg':
        pygame.mixer.music.load(path)
    else:
        sfx[name] = pygame.mixer.Sound(path)

pygame.display.set_caption('Avoid the Bugs')
pygame.display.set_icon(images['appicon'])

mcFont = pygame.font.Font('assets/fonts/Minecraft.ttf', 24)

images['gary'] = pygame.transform.scale(images['gary'], (64, 64))
images['bug'] = pygame.transform.scale(images['bug'], (32, 32))
images['platform'] = ground = pygame.transform.scale(images['platform'], (width, images['platform'].get_size()[1]))

playRect = pygame.Rect((width-300)//2,(height+70)//2,300,120)
images['playbtn'] = pygame.transform.scale(images['playbtn'], playRect.size)
images['titleimg'] = pygame.transform.scale(images['titleimg'], (798, 242))

images['sky'] = pygame.transform.scale(images['sky'], size)

state = 0 # 0: MENU, 1: PLAY, 2: RESULTS
score = 0 # increments as time passes

class Bug(pygame.sprite.Sprite): # inherit base sprite class
    def __init__(self, speed):
        pygame.sprite.Sprite.__init__(self)

        self.image = images['bug']
        self.x = width + self.image.get_size()[0] # making sure the starting x-pos is outside of the screen
        self.speed = speed

def getMaxBugs(score):
    info = {}
    if score <= 150:
        info['max'] = 1
        info['speed'] = (0.3, 0.4)
    elif score > 150 and score <= 300:
        info['max'] = 2
        info['speed'] = (0.3, 0.65)
    elif score > 300 and score <= 750:
        info['max'] = 3
        info['speed'] = (0.3, 0.85)
    elif score > 750 and score <= 1500:
        info['max'] = 4
        info['speed'] = (0.85, 1.2)
    elif score > 1500 and score <= 2000:
        info['max'] = 4
        info['speed'] = (0.9, 1.35)
    else:
        info['max'] = 5
        info['speed'] = (0.95, 1.5)
    
    return info

jump = {
    'isJumping': False,
    'falling': False,
    'height': 0
}

bugs = []

collided = False

lastCreated = time.time() # keep a variable to store the last time that we've created a bug, we want to give the player a small rest before another bug comes rushing in.

pygame.mixer.music.play(-1) # -1 meaning the music will repeat indefinitely.

started = False # Will turn True once the player hits space as an indicator to go.
while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            sys.exit() # make sure pygame clears everything out smoothly
        elif ev.type == pygame.MOUSEBUTTONUP:
            pos = ev.pos

            if playRect.collidepoint(pos) and state == 0:
                state = 1
                score = 0
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE and state == 2:
                collided = False
                state = 0
    
    scrn.blit(images['sky'], (0, 0))

    if (state == 0):
        creditS = mcFont.render('Game developed by Jeffrey H. & Henry C.', False, (0, 0, 0))
        scrn.blit(creditS, (playRect.x - 90, playRect.y + 160))
        
        scrn.blit(images['titleimg'], (playRect.x - 250, playRect.y - 250))
        scrn.blit(images['playbtn'], (playRect.x, playRect.y))
    elif (state == 1):
        # Draw the sprites onto the screen through blit.

        groundY = base_y - ground.get_size()[1]
        Gary = scrn.blit(images['gary'], (25, groundY+jump['height']))
        if jump['isJumping']:
            if jump['height'] <= -255 or jump['falling']:
                jump['falling'] = True

                if jump['height'] >= 0:
                    jump['isJumping'] = False
                    jump['falling'] = False
                    jump['height'] = 0
                else:
                    jump['height'] += 1
            else:
                jump['height'] -= 1

        if pygame.key.get_pressed()[pygame.K_SPACE] and not jump['isJumping']:
            jump['isJumping'] = True
            sfx['jump'].play()
            if not started: started = True
        
        if started:
            scoreS = mcFont.render('SCORE: ' + str(int(score)), False, (0, 0, 0))
            scrn.blit(scoreS, (5, 5))

            if score > highScore: highScore = score
            hS = mcFont.render('HIGH SCORE: ' + str(int(highScore)), False, (0, 0, 0))
            scrn.blit(hS, (5, 32))
            
            details = getMaxBugs(score)
            if len(bugs) < details['max']:
                now = time.time()
                if (now - lastCreated) > random.uniform(0.6, 1.25):
                    lastCreated = now
                    bugs.append(Bug(details['speed']))
            
            for bug in bugs:
                if bug.x < (bug.image.get_size()[0] * -1):
                    bugs.remove(bug)
                else:
                    bug.x -= random.uniform(bug.speed[0], bug.speed[1])
                    bugS = scrn.blit(bug.image, (bug.x, groundY+32))

                    # check for collision through "bugS"
                    if bugS.colliderect(Gary) and not collided:
                        collided = True
                        started = False
                        bugs = []
                        jump['falling'] = False
                        jump['height'] = 0
                        jump['isJumping'] = False
                        sfx['explode'].play()
                        state = 2
                        
                        break
            
            if started: score += 0.025 # make sure the player is still alive before we increment the score.
        else:
            scoreS = mcFont.render('Press SPACE to start!', False, (0, 0, 0))
            scrn.blit(scoreS, (5, 5))

        scrn.blit(ground, (0, base_y + ground.get_size()[1]))
    elif state == 2:
        # game over
        scrn.blit(images['gameover'], (playRect.x - 120, playRect.y - 250))
        resultS = mcFont.render('FINAL SCORE: ' + str(int(score)), False, (0, 0, 0))
        scrn.blit(resultS, (playRect.x + 50, playRect.y))

        hS = mcFont.render('HIGH SCORE: ' + str(int(highScore)), False, (0, 0, 0))
        scrn.blit(hS, (playRect.x + 50, playRect.y + 50))

        restartS = mcFont.render('Press SPACE to return to the menu!', False, (0, 0, 0))
        scrn.blit(restartS, (playRect.x - 60, playRect.y + 150))
    
    # update graphics
    pygame.display.flip()
