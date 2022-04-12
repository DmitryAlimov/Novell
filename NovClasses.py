import sys, os, time
import pygame as pg
import numpy as np
from pydub import AudioSegment

import AdditionalFuncs



class objlist(object):
    def __init__(self, obj_name='', list=[]):
        self.obj_name = obj_name
        self.list = list
    def append(self, input):
        if type(input) == type([]):
            for rec in input:
                self.list.append(rec)
        else:
            self.list.append(input)
    def index(self, obj_name='', name=''):
        for i in range(len(self.list)):
            if obj_name != '':
                if self.list[i].obj_name == obj_name:
                    return i
            if name != '':
                if self.list[i].name == name:
                    return i
    def get(self, obj_name='', name=''):
        if obj_name != '':
            return self.list[self.index(obj_name=obj_name)]
        if name != '':
            return self.list[self.index(name=name)]


class image(object):
    def __init__(self, obj_name='', image_name='default_scene.png', position=[0, 0], size=(300, 300), visible=True, alpha=-1):
        self.obj_name = obj_name
        self.obj_type = 'image'
        self.position = position
        self.size = size
        self.image_name = image_name
        self.visible = visible

        loaded = pg.image.load('graphics/images/' + image_name)
        self.image = pg.transform.scale(loaded, self.size)
        if alpha != -1:
            self.image.set_alpha(alpha)
        self.position = position
    def update(self, events, screen):
        if self.visible:
            screen.blit(self.image, (self.position[0], self.position[1], self.position[0] + self.size[0], self.position[1] + self.size[1]))


class audio(object):
    def __init__(self, obj_name='', audio_name='default_audio.wav'):
        self.obj_name = obj_name
        self.obj_type = 'audio'

        audio_name = 'audio/' + audio_name
        if audio_name.find('.mp3') != -1 and os.path.exists(audio_name.replace('.mp3', '.wav')) == False:
            AudioSegment.from_mp3(audio_name).export(audio_name.replace('.mp3', '.wav'), format="wav")
        self.audio = audio_name.replace('.mp3', '.wav')
    def play(self):
        pg.mixer.music.load(self.audio)
        pg.mixer.music.play()


class text(object):
    def __init__(self, obj_name='', text='text', color='black', font='Ethna.ttf', font_size=12, position=[0, 0]):
        self.obj_name = obj_name
        self.obj_type = 'text'
        self.text = text
        self.color = color
        self.font = pg.font.Font('graphics/fonts/' + font, font_size)
        self.position = position
    def update(self, events, screen):
        self.surface = self.font.render(self.text, True, pg.Color(self.color))
        screen.blit(self.surface, self.position)


class textbox(object):
    def __init__(self, obj_name='', color='black', font='Ethna.ttf', font_size=20, position=[0, 0], size=(300, 300)):
        self.obj_name = obj_name
        self.obj_type = 'text'
        self.text = []
        self.color = color
        self.font = pg.font.Font('graphics/fonts/' + font, font_size)
        self.position = position
        self.size = size
    def add_line(self, input):
        split = [a + ' ' for a in input.split()]
        split_lens = [self.font.render(a, True, pg.Color(self.color)).get_size()[0] for a in split]
        comp_len, comp = 0, ''
        for i in range(len(split)):
            if comp_len + split_lens[i] > self.size[0]:
                self.text.append([comp])
                comp_len, comp = split_lens[i], split[i]
            else:
                comp_len, comp = comp_len + split_lens[i], comp + split[i]
        if comp != '':
            self.text.append([comp])
    def clear(self):
        self.text = []
    def update(self, events, screen):
        n_lines = int(self.size[1] / (self.font.get_height() * 1.5))
        for i in range(max(0, len(self.text) - n_lines), len(self.text)):
            surface = self.font.render(self.text[i][0], True, pg.Color(self.color))
            screen.blit(surface, [self.position[0], self.position[1] + (self.font.get_height() * 1.15)*(i - max(0, len(self.text) - n_lines))])

class button(object):
    def __init__(self, obj_name='', image_name='default_button.png', button_text='', position=[0, 0], size=(30, 30), visible=True, font_size=15):
        self.obj_name = obj_name
        self.obj_type = 'button'
        self.text = text(text=button_text, position=[int(position[0] + 20), position[1]], font_size=font_size)
        self.image = image(image_name=image_name, position=position, size=size)
        self.size = size
        self.position = position
        self.visible = visible
    def update(self, events, screen):
        if self.visible:
            self.image.update(events, screen)
            self.text.update(events, screen)
            for event in events:
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x, y = pg.mouse.get_pos()
                        if x > self.position[0] and x < self.position[0] + self.size[0] and y > self.position[1] and y < \
                                self.position[1] + self.size[1]:
                            return self.obj_name


class character(object):
    def __init__(self, screen, name='', obj_name='', small_image_name='default_character.png', large_image_name='default_character.png', color='black', font='Ethna.ttf', font_size=20):
        self.obj_name = obj_name
        self.obj_type = 'character'
        self.name = name
        self.visible, self.back_visible = False, False
        self.show_mode = 'CH_HIDE'
        self.back_shift = 0
        self.sleep = False
        self.emotion = 0

        (x, y) = screen.get_size()
        self.small_image_name = small_image_name
        small_image_name = self.small_image_name[0:self.small_image_name.find('.')] + '_' + str(self.emotion) + self.small_image_name[self.small_image_name.find('.'):len(self.small_image_name)]
        loaded = pg.image.load('graphics/images/' + small_image_name)
        scl = min(x*0.4/loaded.get_size()[0], y*0.4/loaded.get_size()[1])
        small_image_size = (int(loaded.get_size()[0]*scl), int(loaded.get_size()[1]*scl))
        self.small_image = image(image_name=small_image_name, size=small_image_size)
        self.small_image_size = small_image_size
        
        loaded = pg.image.load('graphics/images/' + large_image_name)
        scl = y*0.95/loaded.get_size()[1]
        large_image_size = (int(loaded.get_size()[0]*scl), int(loaded.get_size()[1]*scl))
        self.large_image = image(image_name=large_image_name, size=large_image_size)
        self.large_image_name = large_image_name
        self.large_image_size = large_image_size
        
        self.button = button(obj_name='continue', image_name='select_button.png', button_text='Дальше', font_size=20, position=[int(x * 0.68), int(y * 0.95)-5], size=(125, 25))
        self.text_name = text(text = self.name, color='white', font='Lifehack.ttf', font_size=25, position = [int(x*0.5), int(y*0.5)])
        self.text_background = image(image_name='text_background_left.png', position=[int(x * 0.2), int(y * 0.4)], size=(int(x * 0.7), int(y * 0.25)))
        self.textbox = textbox(color='black', font='Ethna.ttf', font_size=20, size=(int(x * 0.75), int(y * 0.15)))
    def show_left(self, screen):
        small_image_name = self.small_image_name[0:self.small_image_name.find('.')] + '_' + str(self.emotion) + self.small_image_name[self.small_image_name.find('.'):len(self.small_image_name)]
        self.small_image = image(image_name=small_image_name, size=self.small_image_size)
        (x, y) = screen.get_size()
        self.text_background = image(image_name='text_background_left.png', position=[int(x * 0.10), int(y * 0.76)], size=(int(x * 0.89), int(y * 0.4)))
        self.small_image.position = [int(x * -0.03), int(y * 0.6)]
        self.textbox.position = [int(x * 0.21), int(y * 0.84)]
        self.text_name.position = [int(x * 0.25), int(y * 0.78)]
        self.visible, self.show_mode = True, 'CH_LEFT'
    def show_right(self, screen):
        small_image_name = self.small_image_name[0:self.small_image_name.find('.')] + '_' + str(self.emotion) + self.small_image_name[self.small_image_name.find('.'):len(self.small_image_name)]
        self.small_image = image(image_name=small_image_name, size=self.small_image_size)
        (x, y) = screen.get_size()
        self.text_background = image(image_name='text_background_right.png', position=[int(x * 0.025), int(y * 0.76)], size=(int(x * 0.85), int(y * 0.4)))
        self.small_image.position = [int(x * 0.75), int(y * 0.6)]
        self.textbox.position = [int(x * 0.05), int(y * 0.84)]
        self.text_name.position = [int(x * 0.63), int(y * 0.78)]
        self.visible, self.show_mode = True, 'CH_RIGHT'
    def show_small_right(self, screen):
        small_image_name = self.small_image_name[0:self.small_image_name.find('.')] + '_' + str(self.emotion) + self.small_image_name[self.small_image_name.find('.'):len(self.small_image_name)]
        self.small_image = image(image_name=small_image_name, size=(int(self.small_image_size[0]*0.7), int(self.small_image_size[1]*0.7)))
        (x, y) = screen.get_size()
        self.text_background = image(image_name='text_background_right.png', position=[int(x * 0.025), int(y * 0.76)], size=(int(x * 0.85), int(y * 0.4)))
        self.image.position = [int(x * 0.75), int(y * 0.6)]
        self.textbox.position = [int(x * 0.2), int(y * 0.84)]
        self.text_name.position = [int(x * 0.63), int(y * 0.78)]
        self.visible, self.show_mode = True, 'CH_SMALL_RIGHT'
    def show_back(self, screen):
        (x, y) = screen.get_size()
        self.back_visible = True
        self.large_image.position = [int(x*(0.05 + self.back_shift*0.22)), int(y*0.15)]
    def hide(self):
        self.visible, self.back_visible, self.show_mode = False, False, 'CH_HIDE'
    def update(self, events, screen, GAME, mode=''):
        if self.back_visible and mode == 'back':
            self.large_image.update(events, screen)
        if self.visible and mode == '':
            self.text_background.update(events, screen)
            self.small_image.update(events, screen)
            self.textbox.update(events, screen)
            self.text_name.update(events, screen)
            select = self.button.update(events, screen)
            while self.sleep:
                events = pg.event.get()
                for event in events:
                    if event.type == pg.QUIT:
                        pg.quit(), sys.exit()
                    if int(str(event.type)) in [771, 768, 769]:
                        self.sleep = False
                GAME.menu.update(events, screen, GAME=GAME)
                select = self.button.update(events, screen)
                if select == 'continue':
                    break
                pg.display.update()
            self.sleep = False


class location(object):
    def __init__(self, screen, obj_name='', name='', image_name='default_scene.png'):
        self.obj_name = obj_name
        self.name = name
        self.obj_type = 'location'

        x, y = screen.get_size()
        loaded = pg.image.load('graphics/images/' + image_name)
        scl = min(screen.get_size()[0] / loaded.get_size()[0], screen.get_size()[1] / loaded.get_size()[1])
        size = (int(loaded.get_size()[0]*scl), int(loaded.get_size()[1]*scl))
        position = [(screen.get_size()[0] - size[0]) // 2, (screen.get_size()[1] - size[1]) // 2]
        #self.image = image(image_name=image_name, size=size, position=position)
        self.image = image(image_name=image_name, size=(x, y), position=[0, 0])
        self.location_name_background = image(image_name='location_name_background.png', size=(int(x*0.5), int(y*0.2)), position=(int(x*0.025), int(y*0.02)))
        self.text = text(text=name, font='Lifehack.ttf', font_size=25, position=[int(x*0.1), int(y*0.026)], color='white')
    def update(self, events, screen):
        self.image.update(events, screen)
        self.location_name_background.update(events, screen)
        self.text.update(events, screen)
        

class thing(object):
    def __init__(self, screen, obj_name='', name='', image_name='default_thing.png', size=(0, 0), position=[200, 200]):
        self.obj_name = obj_name
        self.name = name
        self.obj_type = 'thing'

        x, y = screen.get_size()
        if size == (0, 0):
            size = (int(x*0.05), int(x*0.05))
        self.image_name = image_name
        self.position = position
        self.size = size
    def update(self, events, screen):
        i=0

class window(object):
    def __init__(self, screen, text_arr=[]):
        x, y = screen.get_size()
        self.background = image(image_name='default_background.png', size=(int(x*0.7), int(y*0.7)), position=[int(x * 0.1), int(y * 0.1)])
        self.button = button(obj_name='close', image_name='select_button.png', button_text='Закрыть', font_size=20, position=[int(x * 0.68)-60, int(y * 0.73)], size=(125, 25))
        self.textbox = textbox(size=(int(x*0.6), int(y*0.6)), position=[int(x * 0.1)+40, int(y * 0.1)+20])
        for sent in text_arr:
            self.textbox.add_line(sent)
    def show(self, screen):
        pg.image.save(screen, 'graphics/images/tmp.jpg')
        shadow = image(image_name='shadow.png', size=screen.get_size(), alpha=25)
        events = pg.event.get()
        for i in range(12):
            shadow.update(events, screen)
            self.background.update(events, screen)
            self.textbox.update(events, screen)
            time.sleep(0.04)
            pg.display.update()
        run_flag = True
        while run_flag:
            events = pg.event.get()
            select = self.button.update(events, screen)
            if select =='close':
                break
            for event in events:
                if int(str(event.type)) == 771:
                    run_flag = False
                if event.type == pg.QUIT:
                    pg.quit(), sys.exit()
            pg.display.update()
        tmp = image(image_name='tmp.jpg', size=screen.get_size())
        tmp.update(events, screen)
        pg.display.update()
            
    
        