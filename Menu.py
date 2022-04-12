import sys, time, pygame_textinput, pylab, serial, pygame, os
import pygame as pg
import numpy as np
import NovClasses as NC
import AdditionalFuncs as AF


class menu(object):
    def __init__(self, screen):
        (x, y) = screen.get_size()
        self.buttons = [NC.button(obj_name='menu_main_button', image_name='menu_main_button.JPG', position=[x-35, 0]), \
                        NC.button(obj_name='menu_invent_button', image_name='menu_invent_button.JPG', position=[x-70, 0]), \
                        NC.button(obj_name='menu_save_button', image_name='menu_save_button.png', visible=False, position=[x-35, 50]), \
                        NC.button(obj_name='menu_load_button', image_name='menu_load_button.png', visible=False, position=[x-35, 100])]
    def update(self, events, screen, GAME):
        for button in self.buttons:
            button_pressed = button.update(events, screen)
            if button_pressed =='menu_main_button':
                for i in range(2, len(self.buttons)):
                    self.buttons[i].visible = not self.buttons[i].visible
            if button_pressed == 'menu_invent_button':
                if str(type(GAME.taken_things)) != "<class 'list'>":
                    text_arr = [thing.name for thing in GAME.taken_things.list]
                    if text_arr == []:
                        text_arr.append('В инвентаре ничего нет')
                    window = NC.window(screen, text_arr=text_arr)
                    window.show(screen)
            if button_pressed == 'menu_save_button':
                for i in range(2, len(self.buttons)):
                    self.buttons[i].visible = False
                GAME.save()
            if button_pressed == 'menu_load_button':
                for i in range(2, len(self.buttons)):
                    self.buttons[i].visible = False
                GAME.load(screen)