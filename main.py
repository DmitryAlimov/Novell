import sys, time, pygame_textinput, pylab, serial, pygame, os
import pygame as pg
import numpy as np
from pygame.locals import *
from pydub import AudioSegment

import GAME, Script, Menu
import NovClasses as NC
import AdditionalFuncs as AF
import SpecialFucs as SF


pg.init(), pg.mixer.init(22050, -16, 2, 2048), pg.mixer.music.set_volume(0.7)
window = pygame.display.set_mode((1200, 850), DOUBLEBUF)
#window = pygame.display.set_mode((800, 600), DOUBLEBUF)
screen = pygame.display.get_surface()
pg.display.set_caption("Novell")


image = pg.transform.scale(pg.image.load('graphics/images/loading.png'), screen.get_size())
screen.blit(image, (0, 0, screen.get_size()[0], screen.get_size()[1]))
pg.display.update()

partitions_list = ["CHARACTERS", "LOCATIONS", "IMAGES", "AUDIOS", "THINGS", "BEGIN"]
commands_list = ['LABEL', 'GOTO', 'IF', 'IF_OWN', 'CASE', 'END', 'SELECT', 'TAKE', 'EVAL', 'VIDEO', \
                 'CH_RIGHT', 'CH_LEFT', 'CH_HIDE', 'PLAY_MUSIC', 'STOP_MUSIC', 'DELAY', 'IM_SHOW', 'IM_HIDE',\
                 'SPECIAL', 'LOCATION', 'CH_SMALL_RIGHT', 'WINDOW', 'CH_BACK', 'INCLUDE', 'REMOVE', 'EMOTION', '$', '#']
script = Script.script(fname='contents.txt', partitions_list=partitions_list, commands_list=commands_list)
GAME = GAME.GAME(screen=screen, script=script, partitions_list=partitions_list, commands_list=commands_list)



# загружаем объекты в GAME
GAME.characters = NC.objlist(list=AF.load_characters(screen, lines=script.get_partition_lines("CHARACTERS")))
GAME.locations = NC.objlist(list=AF.load_locations(screen, lines=script.get_partition_lines("LOCATIONS")))
GAME.images = NC.objlist(list=AF.load_images(screen, lines=script.get_partition_lines("IMAGES")))
GAME.audios = NC.objlist(list=AF.load_audios(screen, lines=script.get_partition_lines("AUDIOS")))
GAME.things = NC.objlist(list=AF.load_things(screen, lines=script.get_partition_lines("THINGS")))


# загружаем логическую разметку скрипта
script.labels, script = AF.load_labels(script)
script.selections, script = AF.load_selections(script, screen)
script.conditions, script.own_conditions, script.cases, script = AF.load_conditions(script, screen)
script.list = script.get_partition_lines("BEGIN", lines_only=False)
script.specials = SF.specials()
script.set_terminators()
script.print()


GAME.init(script)


while True:
    GAME.execute_script(script,  screen)

    events = pg.event.get()
    GAME.update(events, screen)

    for event in events:
        if event.type == pg.QUIT:
            pg.quit(), sys.exit()
    pg.display.update()


