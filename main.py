import pygame
import piano_lists as pl
from pygame import mixer
from time import sleep, perf_counter
import threading
from datetime import datetime
import time
import os
import asyncio


pygame.init()

font = pygame.font.Font('assets/Terserah.ttf', 48)
medium_font = pygame.font.Font('assets/Terserah.ttf', 28)
small_font = pygame.font.Font('assets/Terserah.ttf', 16)
real_small_font = pygame.font.Font('assets/Terserah.ttf', 10)
fps = 60
timer = pygame.time.Clock()
WIDTH = 52 * 35
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])

LEFT = 1
RIGHT = 3


gold = (212,175,55)

beat = 30
instrument = 7
boxes = []

piano_clicked = [[-1, 1] for _ in range(beat)]
joined_positions = [[_, 1, -1] for _ in range(beat)] #start, end, clicked or not, selected or not
clicked = [[-1 for _ in range(beat)] for _ in range(instrument)]

previous_piano_clicked = [[-1, 1] for _ in range(beat)]
previous_joined_positions = [[_, 1, -1] for _ in range(beat)]
previous_click = [[-1 for _ in range(beat)] for _ in range(instrument)]


bpm = 400
actual_bpm = bpm//4
playing = True
active_length = 0
active_beat = 1
beat_change = True
select_coords = -1
select_open = False
note_played = [[] for i in range(beat)]
piano_box_play_start = False

white_sounds = []
black_sounds = []

white_sounds_piano = []
black_sounds_piano = []


white_notes = []
black_notes = []

active_whites = []
active_blacks = []
left_oct = 4
right_oct = 5

left_hand = pl.left_hand
right_hand = pl.right_hand
piano_notes = pl.piano_notes
white_notes = pl.white_notes
black_notes = pl.black_notes
black_labels = pl.black_labels


high_hat = mixer.Sound('assets\\sounds\\hi hat.wav')
snare = mixer.Sound('assets\\sounds\\snare.wav')
kick = mixer.Sound('assets\\sounds\\kick.wav')
crash = mixer.Sound('assets\\sounds\\crash.wav')
clap = mixer.Sound('assets\\sounds\\clap.wav')
tom = mixer.Sound('assets\\sounds\\tom.wav')
bass = mixer.Sound('assets\\sounds\\bass.mp3')
pygame.mixer.set_num_channels(100)



for i in range(len(white_notes)):
    white_sounds.append(mixer.Sound(f'assets\\notes\\{white_notes[i]}.wav'))
    white_sounds_piano.append(mixer.Sound(f'assets\\notes\\{white_notes[i]}.wav'))
    white_notes.append(white_notes[i])

for i in range(len(black_notes)):
    black_sounds.append(mixer.Sound(f'assets\\notes\\{black_notes[i]}.wav'))
    black_sounds_piano.append(mixer.Sound(f'assets\\notes\\{black_notes[i]}.wav'))
    black_notes.append(black_notes[i])

def piano_joined_positions():
    start = None
    joined_positions.clear()
    for i in range(len(piano_clicked) - 1):
        if piano_clicked[i][0] == 1:
            if start is None:
                start = i
        elif piano_clicked[i][0] == -1:
            if start is not None:
                joined_positions.append((start, i-1, 1))
                joined_positions.append((i,i,-1))
                start = None
            else:
                joined_positions.append((i, i, -1))
    
    if piano_clicked[-1][0] == 1 and start is not None:
        joined_positions.append((start, len(piano_clicked) - 1, 1))

    elif piano_clicked[-1][0] == -1 and start is not None:
        joined_positions.append((start, len(piano_clicked) - 2, 1))
        joined_positions.append((len(piano_clicked) - 1, len(piano_clicked) - 1, -1))

    elif piano_clicked[-1][0] == -1 and start is None:
        joined_positions.append((len(piano_clicked) - 1, len(piano_clicked) - 1, -1))
                                
    elif piano_clicked[-1][0] == 1 and start is None:
        joined_positions.append((len(piano_clicked) - 1, len(piano_clicked) - 1, 1))


    
async def play_piano_notes(position, note_played, playing, length, active_beat):
    current_beat = active_beat
    if note_played[position]:
        for i, note in enumerate(note_played[position]):
            if note in white_notes:
                white_sounds_piano[white_notes.index(note)].play()
            if note in black_notes:
                black_sounds_piano[black_notes.index(note)].play()

def play_notes():

    for i in range(len(clicked)):
        if clicked[i][active_beat] == 1:
            if i == 0:
                bass.play()
            if i ==2:
                high_hat.play()
            if i == 1:
                kick.play()
            if i == 3:
                snare.play()
            if i == 4:
                clap.play()
            if i == 5:
                crash.play()
            if i == 6:
                tom.play()
        
    # for i in range(len(joined_positions)):
    #     if joined_positions[i][2] == 1:
    #         length = joined_positions[i] - joined_positions[i][0] + 1
    #         time = beat_length * length

def draw_instrument(number, instrument_list):
    height_increment = (HEIGHT - 300)//(number+1)

    for i, instrument in enumerate(instrument_list):
        text_render = medium_font.render(str(instrument), True, 'black')
        screen.blit(text_render ,(30, 30 + (i+1)*height_increment))

    text_render_keyboard = medium_font.render('Keyboard', True, 'black')
    screen.blit(text_render_keyboard ,(30, 30))

    for i in range(number):
        pygame.draw.line(screen, 'black', (0, (i+1)*height_increment), (200, (i+1)*height_increment), 3)

    pygame.draw.line(screen, 'black', (0, height_increment), (200, height_increment), 3)

def draw_beat_board(clicked, active_beat, piano_clicked, joined_positions, select_open, select_coords, note_played):
    piano_boxes = []
    boxes = []
    joined_piano_boxes = []
    left_box = pygame.draw.rect(screen, 'black',[0,0,200, 600], 5)
    right_box = pygame.draw.rect(screen, 'black', [200,0,1200,600], 5)
    menu_box = pygame.draw.rect(screen, 'black', [1400, 0, 420, 600], 5)
    clear_rect = []
    
    instruments = ['BassDrum', 'Kick', 'High hat', 'Snare', 'Clap', 'Crash','Floor Tom']

    draw_instrument(instrument, instruments)

    for i in range(beat):
        for j in range(instrument):
            if clicked[j][i] == -1:
                color =  gold
                color_fill = 'gray'
            elif clicked[j][i] == 1:
                color_fill = 'black'
                color = gold

            rect = pygame.draw.rect(screen, color_fill, [i*(1200//beat) + 200, (j+1)*((HEIGHT-300)//(instrument+1)), 1200//beat, (HEIGHT - 300)//(instrument+1)],0 , 3)
            
            pygame.draw.rect(screen, color, [i*(1200//beat) + 200, (j+1)*((HEIGHT-300)//(instrument+1)), 1200//beat, (HEIGHT - 300)//(instrument+1)], 3,3)
            boxes.append((rect,(i,j)))
    
    for i in range(beat):
        if piano_clicked[i][0] == -1:
            color =  gold
            color_fill = 'gray'
        elif piano_clicked[i][0] == 1:
            color_fill = 'black'
            color = gold

        piano_rect = pygame.draw.rect(screen, color_fill, [i*(1200//beat) + 200, 0, (1200//beat), (HEIGHT - 300)//(instrument+1)], 0, 3)
        pygame.draw.rect(screen, color, [i*(1200//beat) + 200, 0, (1200//beat), (HEIGHT - 300)//(instrument+1)], 3, 3)

        piano_boxes.append((piano_rect,i))
    
    j = 0
    real_no_boxes = 0
    for i, box in enumerate(joined_positions):
        length = box[1] - box[0] + 1
        start_position = box[0]
        clicked_or_not = box[2]

        if clicked_or_not == 1:   
            real_no_boxes += 1    
            color_fill = 'black'
            color = gold
            piano_rect = pygame.draw.rect(screen, color_fill, [start_position*(1200//beat) + 200, 0, (1200//beat)*length, (HEIGHT - 300)//(instrument+1)], 0,3 )
            pygame.draw.rect(screen, color, [start_position*(1200//beat) + 200, 0, (1200//beat)*length, (HEIGHT - 300)//(instrument+1)], 3, 3)

            joined_piano_boxes.append((piano_rect, j, start_position, length))
            j = j + 1
    
    if real_no_boxes < len(note_played):
        note_played = note_played[:(len(note_played) - (len(note_played) - real_no_boxes))]
    else:     
        for i in range(real_no_boxes - len(note_played)):
            note_played.append([])

    # note_played_list = []
    # for notes in note_played:
    #     for note in notes:

    if select_open:
        # box = joined_piano_boxes[select_coords]
        # start_position = box[2]
        # length = box[3]
        
        select_rect = pygame.draw.rect(screen, 'black', [1525, HEIGHT-455, 100,50], 0, 5)
        clear_rect_rect = pygame.draw.rect(screen, 'black', [1625, HEIGHT-455, 100,50], 0, 5)
        clear_rect.append(clear_rect_rect)
        select_text = medium_font.render('Select', True, 'white')
        clear_text = medium_font.render('Clear', True, 'white')
        screen.blit(select_text, (1530, HEIGHT - 450))
        screen.blit(clear_text, (1630, HEIGHT - 450))

        j = 0
        height = HEIGHT - 375
        if select_open:
            for i, note in enumerate(note_played[joined_piano_boxes[select_coords][1]]):
                text = small_font.render(note, True, 'white')
                if 1525 + (i-j)*30 > 1725:
                    j = i
                    height += 25
                else:
                    pass
                    
    
                width = 1525 + (i-j)*30
                screen.blit(text, (width, height))
       
    active = pygame.draw.rect(screen, 'green', [active_beat*(1200//beat) + 200, 0, 1200//beat, 600], 3, 3)

    return boxes, piano_boxes, joined_piano_boxes, clear_rect, note_played


def draw_piano(whites, blacks):
    white_rects = []
    for i in range(52):
        rect = pygame.draw.rect(screen, 'white', [i * 35, HEIGHT - 300, 35, 300], 0, 2)
        white_rects.append(rect)
        pygame.draw.rect(screen, 'black', [i * 35, HEIGHT - 300, 35, 300], 2, 2)
        key_label = small_font.render(white_notes[i], True, 'black')
        screen.blit(key_label, (i * 35 + 3, HEIGHT - 20))
    skip_count = 0
    last_skip = 2
    skip_track = 2
    black_rects = []
    for i in range(36):
        rect = pygame.draw.rect(screen, 'black', [23 + (i * 35) + (skip_count * 35), HEIGHT - 300, 24, 200], 0, 2)
        for q in range(len(blacks)):
            if blacks[q][0] == i:
                if blacks[q][1] > 0:
                    pygame.draw.rect(screen, 'green', [23 + (i * 35) + (skip_count * 35), HEIGHT - 300, 24, 200], 2, 2)
                    blacks[q][1] -= 1

        key_label = real_small_font.render(black_labels[i], True, 'white')
        screen.blit(key_label, (25 + (i * 35) + (skip_count * 35), HEIGHT - 120))
        black_rects.append(rect)
        skip_track += 1
        if last_skip == 2 and skip_track == 3:
            last_skip = 3
            skip_track = 0
            skip_count += 1
        elif last_skip == 3 and skip_track == 2:
            last_skip = 2
            skip_track = 0
            skip_count += 1

    for i in range(len(whites)):
        if whites[i][1] > 0:
            j = whites[i][0]
            pygame.draw.rect(screen, 'green', [j * 35, HEIGHT - 100, 35, 100], 2, 2)
            whites[i][1] -= 1

    return white_rects, black_rects, whites, blacks


def draw_hands(rightOct, leftOct, rightHand, leftHand):
    # left hand
    pygame.draw.rect(screen, 'dark gray', [(leftOct * 245) - 175, HEIGHT - 60, 245, 30], 0, 4)
    pygame.draw.rect(screen, 'black', [(leftOct * 245) - 175, HEIGHT - 60, 245, 30], 4, 4)
    text = small_font.render(leftHand[0], True, 'white')
    screen.blit(text, ((leftOct * 245) - 165, HEIGHT - 55))
    text = small_font.render(leftHand[2], True, 'white')
    screen.blit(text, ((leftOct * 245) - 130, HEIGHT - 55))
    text = small_font.render(leftHand[4], True, 'white')
    screen.blit(text, ((leftOct * 245) - 95, HEIGHT - 55))
    text = small_font.render(leftHand[5], True, 'white')
    screen.blit(text, ((leftOct * 245) - 60, HEIGHT - 55))
    text = small_font.render(leftHand[7], True, 'white')
    screen.blit(text, ((leftOct * 245) - 25, HEIGHT - 55))
    text = small_font.render(leftHand[9], True, 'white')
    screen.blit(text, ((leftOct * 245) + 10, HEIGHT - 55))
    text = small_font.render(leftHand[11], True, 'white')
    screen.blit(text, ((leftOct * 245) + 45, HEIGHT - 55))
    text = small_font.render(leftHand[1], True, 'black')
    screen.blit(text, ((leftOct * 245) - 148, HEIGHT - 55))
    text = small_font.render(leftHand[3], True, 'black')
    screen.blit(text, ((leftOct * 245) - 113, HEIGHT - 55))
    text = small_font.render(leftHand[6], True, 'black')
    screen.blit(text, ((leftOct * 245) - 43, HEIGHT - 55))
    text = small_font.render(leftHand[8], True, 'black')
    screen.blit(text, ((leftOct * 245) - 8, HEIGHT - 55))
    text = small_font.render(leftHand[10], True, 'black')
    screen.blit(text, ((leftOct * 245) + 27, HEIGHT - 55))
    # right hand
    pygame.draw.rect(screen, 'dark gray', [(rightOct * 245) - 175, HEIGHT - 60, 245, 30], 0, 4)
    pygame.draw.rect(screen, 'black', [(rightOct * 245) - 175, HEIGHT - 60, 245, 30], 4, 4)
    text = small_font.render(rightHand[0], True, 'white')
    screen.blit(text, ((rightOct * 245) - 165, HEIGHT - 55))
    text = small_font.render(rightHand[2], True, 'white')
    screen.blit(text, ((rightOct * 245) - 130, HEIGHT - 55))
    text = small_font.render(rightHand[4], True, 'white')
    screen.blit(text, ((rightOct * 245) - 95, HEIGHT - 55))
    text = small_font.render(rightHand[5], True, 'white')
    screen.blit(text, ((rightOct * 245) - 60, HEIGHT - 55))
    text = small_font.render(rightHand[7], True, 'white')
    screen.blit(text, ((rightOct * 245) - 25, HEIGHT - 55))
    text = small_font.render(rightHand[9], True, 'white')
    screen.blit(text, ((rightOct * 245) + 10, HEIGHT - 55))
    text = small_font.render(rightHand[11], True, 'white')
    screen.blit(text, ((rightOct * 245) + 45, HEIGHT - 55))
    text = small_font.render(rightHand[1], True, 'black')
    screen.blit(text, ((rightOct * 245) - 148, HEIGHT - 55))
    text = small_font.render(rightHand[3], True, 'black')
    screen.blit(text, ((rightOct * 245) - 113, HEIGHT - 55))
    text = small_font.render(rightHand[6], True, 'black')
    screen.blit(text, ((rightOct * 245) - 43, HEIGHT - 55))
    text = small_font.render(rightHand[8], True, 'black')
    screen.blit(text, ((rightOct * 245) - 8, HEIGHT - 55))
    text = small_font.render(rightHand[10], True, 'black')
    screen.blit(text, ((rightOct * 245) + 27, HEIGHT - 55))


run = True
while run:
    left_dict = {'Z': f'C{left_oct}',
                 'S': f'C#{left_oct}',
                 'X': f'D{left_oct}',
                 'D': f'D#{left_oct}',
                 'C': f'E{left_oct}',
                 'V': f'F{left_oct}',
                 'G': f'F#{left_oct}',
                 'B': f'G{left_oct}',
                 'H': f'G#{left_oct}',
                 'N': f'A{left_oct}',
                 'J': f'A#{left_oct}',
                 'M': f'B{left_oct}'}

    right_dict = {'R': f'C{right_oct}',
                  '5': f'C#{right_oct}',
                  'T': f'D{right_oct}',
                  '6': f'D#{right_oct}',
                  'Y': f'E{right_oct}',
                  'U': f'F{right_oct}',
                  '8': f'F#{right_oct}',
                  'I': f'G{right_oct}',
                  '9': f'G#{right_oct}',
                  'O': f'A{right_oct}',
                  '0': f'A#{right_oct}',
                  'P': f'B{right_oct}'}
    timer.tick(fps)
    screen.fill('gray')
    white_keys, black_keys, active_whites, active_blacks = draw_piano(active_whites, active_blacks)
    draw_hands(right_oct, left_oct, right_hand, left_hand)

    boxes, piano_boxes, joined_piano_boxes, clear_rect,note_played = draw_beat_board(clicked, active_beat, piano_clicked, joined_positions, select_open, select_coords, note_played)
    
    #play/pause
    play_pause = pygame.draw.rect(screen, 'black', [1525, HEIGHT - 875, 200,100], 0, 5)
    play_text = medium_font.render("Play/Pause", True, 'white')
    screen.blit(play_text, (1550, HEIGHT - 845 ))

    if playing:
        play_text2 = small_font.render('Playing', True, 'white')
    else:
        play_text2 = small_font.render('Pausing', True, 'white')

    screen.blit(play_text2, (1550, HEIGHT - 815 ))

    #+/- beats
    plus_minus = pygame.draw.rect(screen, 'black', [1525, HEIGHT - 770, 200,100], 0, 5)

    minus = pygame.draw.rect(screen, 'red', [1525, HEIGHT - 720, 100,50], 0, 5)
    plus = pygame.draw.rect(screen, 'blue', [1625, HEIGHT - 720, 100,50], 0, 5)

    add_box_text = medium_font.render("+/- beats", True, 'white')
    screen.blit(add_box_text, (1550, HEIGHT-755))

    minus_text = medium_font.render("-", True, 'white')
    screen.blit(minus_text, (1570, HEIGHT - 710))

    plus_text = medium_font.render("+", True, 'white')
    screen.blit(plus_text, (1670, HEIGHT - 710))

    #clear/restore
    clear_box = pygame.draw.rect(screen, 'black', [1525, HEIGHT - 665, 200,50], 0, 5)
    restore_box = pygame.draw.rect(screen, 'black', [1525, HEIGHT - 615, 200,50], 0, 5)

    clear_text = medium_font.render("Clear", True, 'white')
    screen.blit(clear_text, (1575, HEIGHT - 655 ))

    restore_text = medium_font.render("Restore", True, 'white')
    screen.blit(restore_text, (1575, HEIGHT - 605))

    pygame.draw.line(screen, 'gray', (1525, HEIGHT - 615), (1725, HEIGHT - 615), 3)


    #+/- bpm
    bpm_box = pygame.draw.rect(screen, 'black', [1525, HEIGHT - 560, 200, 100], 0, 5)
    minus_bpm = pygame.draw.rect(screen, 'red', [1525, HEIGHT - 510, 100,50], 0, 5)
    plus_bpm = pygame.draw.rect(screen, 'blue', [1625, HEIGHT - 510, 100,50], 0, 5)

    add_bpm_box_text = medium_font.render(f'{actual_bpm} bpm', True, 'white')
    screen.blit(add_bpm_box_text, (1555, HEIGHT-555))

    minus_bpm_text = medium_font.render("-", True, 'white')
    screen.blit(minus_bpm_text, (1570, HEIGHT - 500))

    plus_bpm_text = medium_font.render("+", True, 'white')
    screen.blit(plus_bpm_text, (1670, HEIGHT - 500))



    if beat_change:
        for box in joined_piano_boxes:
            start_position = box[2] 
            length = box[3]
            positions = [i for i in range(start_position, start_position + length + 1)]

            if active_beat == start_position:        
                asyncio.run(play_piano_notes(box[1],note_played, True, length, active_beat))
            # elif active_beat not in positions:
            #     asyncio.run(play_piano_notes(box[1],note_played, False, length, active_beat))

        play_notes()
        beat_change = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
            for i in range(len(boxes)):
                if boxes[i][0].collidepoint(event.pos):
                    coords = boxes[i][1]
                    clicked[coords[1]][coords[0]] *= -1

            for i in range(len(piano_boxes)):
                if piano_boxes[i][0].collidepoint(event.pos):
                    coords = piano_boxes[i][1]
                    piano_clicked[coords][0] *= -1
                    piano_joined_positions()

            for i in range(len(joined_piano_boxes)):
                if joined_piano_boxes[i][0].collidepoint(event.pos):
                    coords = joined_piano_boxes[i][1]
                    joined_positions[coords][2] *= -1

            # if select_mode:
            #     for i in range(len(black_keys)):
            #         if black_keys[i].collidepoint(event.pos):
            #             note_played.append(black_notes[i])
            #             black_sounds[i].play(0, 1000)
            #             black_key = True
            #             active_blacks.append([i, 30])

            #         for i in range(len(white_keys)):
            #             if white_keys[i].collidepoint(event.pos) and not black_key:
            #                 note_played.append(white_notes[i])
            #                 white_sounds[i].play(0, 3000)
            #                 active_whites.append([i, 30])

            black_key = False
            for i in range(len(black_keys)):
                if black_keys[i].collidepoint(event.pos):
                    black_sounds[i].play(0, 1000)
                    black_key = True
                    active_blacks.append([i, 30])
                    if select_open is True:
                        note_played[joined_piano_boxes[select_coords][1]].append(black_notes[i])

            for i in range(len(white_keys)):
                if white_keys[i].collidepoint(event.pos) and not black_key:
                    white_sounds[i].play(0, 3000)
                    active_whites.append([i, 30])
                    if select_open:
                        note_played[joined_piano_boxes[select_coords][1]].append(white_notes[i])
                        print(note_played)
                        print(select_open)

        if event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
            if play_pause.collidepoint(event.pos):
                if playing:
                    playing = False
                elif not playing:
                    playing = True

            if plus.collidepoint(event.pos):
                beat += 1
                for click in clicked:
                    click.append(-1)
                
                piano_clicked.append([-1,1])
                piano_joined_positions()
            
            if minus.collidepoint(event.pos):
                if beat == 4:
                    pass
                else:
                    beat -= 1
                    piano_clicked.pop(-1)
                    piano_joined_positions()

            if clear_box.collidepoint(event.pos):
                if select_open:
                    print("deselect")
                else:
                    previous_click = clicked
                    previous_joined_positions = joined_positions
                    previous_piano_clicked = piano_clicked

                    clicked = [[-1 for _ in range(beat)] for _ in range(instrument)]
                    piano_clicked = [[-1, 1] for _ in range(beat)]
                    joined_positions = [[_, 1, -1] for _ in range(beat)]
            
            if restore_box.collidepoint(event.pos):
                clicked = previous_click
                piano_clicked = previous_piano_clicked
                joined_positions = previous_joined_positions

            if plus_bpm.collidepoint(event.pos):
                bpm += 40
                actual_bpm = bpm//4

            if minus_bpm.collidepoint(event.pos):
                bpm -= 40
                actual_bpm = bpm//4

            if clear_rect:
                if clear_rect[0].collidepoint(event.pos):
                    if select_open:
                        note_played[joined_piano_boxes[select_coords][1]].clear()
                    else:
                        print("select a box")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT:
            for box in joined_piano_boxes:
                if box[0].collidepoint(event.pos):
                    current_box = box
                    if select_open is False:
                        select_open = True
                        select_coords = box[1]
                        print(select_coords)
                    elif select_open is True:
                        select_open = False
                        select_coords = -1
                   
            
        if event.type == pygame.TEXTINPUT:
            if event.text.upper() in left_dict:
                if left_dict[event.text.upper()][1] == '#':
                    index = black_labels.index(left_dict[event.text.upper()])
                    black_sounds[index].play(0, 1000)
                    active_blacks.append([index, 30])
                else:
                    index = white_notes.index(left_dict[event.text.upper()])
                    white_sounds[index].play(0, 1000)
                    active_whites.append([index, 30])
            if event.text.upper() in right_dict:
                if right_dict[event.text.upper()][1] == '#':
                    index = black_labels.index(right_dict[event.text.upper()])
                    black_sounds[index].play(0, 1000)
                    active_blacks.append([index, 30])
                else:
                    index = white_notes.index(right_dict[event.text.upper()])
                    white_sounds[index].play(0, 1000)
                    active_whites.append([index, 30])

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if right_oct < 8:
                    right_oct += 1
            if event.key == pygame.K_LEFT:
                if right_oct > 0:
                    right_oct -= 1
            if event.key == pygame.K_UP:
                if left_oct < 8:
                    left_oct += 1
            if event.key == pygame.K_DOWN:
                if left_oct > 0:
                    left_oct -= 1

    beat_length = 3600 // bpm

    if playing:
        if active_length < beat_length:
            active_length += 1
        else:
            active_length = 0
            if active_beat < beat - 1:
                active_beat += 1
                beat_change = True
            else:
                active_beat = 0
                beat_change = True



    pygame.display.flip()
pygame.quit()

