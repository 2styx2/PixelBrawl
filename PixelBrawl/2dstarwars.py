import pygame, sys

clock = pygame.time.Clock()

from pygame.locals import *
pygame.init() # initiates pygame

pygame.display.set_caption('My Pygame Window')

WINDOW_SIZE = (1024,768)

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate window

display = pygame.Surface((512,384))

moving_right = False
moving_left = False
air_timer = 0

true_scroll = [0,0]

grass_hill_img =  pygame.image.load('grass_on_hill.png')
grass_img = pygame.image.load('grass.png')
dirt_img = pygame.image.load('dirt.png')

background_objects = [[0.25,[120,50,70,400]],[0.25,[280,40,40,400]],[0.25,[370,75,120,400]],[0.5,[30,55,40,400]],[0.5,[130,170,100,400]],[0.5,[300,80,200,400]]]

def load_map(path):
    f = open(path + '.txt','r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map

game_map = load_map('map')

global animation_frames
animation_frames = {}

def load_animation(path,frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((255,255,255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame

animation_database = {}

animation_database['run'] = load_animation('player_animations/run',[15,15])
animation_database['idle'] = load_animation('player_animations/idle',[30,15,10])

player_action = 'idle'
player_frame = 0
player_flip = False

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types

player_rect = pygame.Rect(50,50,10,31)
test_rect = pygame.Rect(100,100,100,50)

player_y_momentum = 0

while True: # game loop
    display.fill((146,244,255))

    true_scroll[0] += (player_rect.x-true_scroll[0]-266)/20
    true_scroll[1] += (player_rect.y-true_scroll[1]-207)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    pygame.draw.rect(display,(35,122,135), pygame.Rect(0,230,600,500))
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0]-scroll[0]*background_object[0],background_object[1][1]-scroll[1]*background_object[0],background_object[1][2],background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display, (56,175,193),obj_rect)
        else:
            pygame.draw.rect(display, (27,188,166),obj_rect)

    tile_rects = []
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '1':
                display.blit(dirt_img, (x*16-scroll[0],y*16-scroll[1]))
            if tile == '2':
                display.blit(grass_img,(x*16-scroll[0],y*16-scroll[1]))
            if tile == '3':
                display.blit(grass_hill_img,(x*16-scroll[0],y*16-scroll[1]))
            if tile != '0':
                tile_rects.append(pygame.Rect( x*16, y*16, 16, 16))
            x += 1
        y += 1

    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 3
    if moving_left:
        player_movement[0] -= 3
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    if player_y_momentum > 3:
        player_y_momentum = 3

    if player_movement[0] > 0:
        player_action,player_frame = change_action(player_action,player_frame,'run')
        player_flip = False
    if player_movement[0] == 0:
        player_action,player_frame = change_action(player_action,player_frame,'idle')
    if player_movement[0] < 0:
        player_action,player_frame = change_action(player_action,player_frame,'run')
        player_flip = True

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom'] or collisions['top'] == True:
        player_y_momentum = 0
        air_timer = 0
        num_jumps = 1
    else:
        air_timer += 1

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_img,player_flip,False),(player_rect.x-scroll[0],player_rect.y-scroll[1]))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_d:
                moving_right = True
            if event.key == K_a:
                moving_left = True
            if event.key == K_w:
                if air_timer < 6:
                    player_y_momentum = -6
        if event.type == KEYUP:
            if event.key == K_d:
                moving_right = False
            if event.key == K_a:
                moving_left = False

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0,0))
    pygame.display.update()
    clock.tick(60)
