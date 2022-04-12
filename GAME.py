import sys, time, pygame_textinput, pylab, serial, pygame, os, pickle
import pygame as pg
import numpy as np
import NovClasses as NC
import AdditionalFuncs as AF
import Menu


class GAME(object):
    def __init__(self, screen, script, partitions_list, commands_list):
        self.menu = Menu.menu(screen)
        self.background = NC.image(image_name='default_background.png', size=screen.get_size())
        self.current_id, self.current_level = 0, 0
        self.current_location = None
        self.linerun_flag = True
        self.partitions_list, self.commands_list = partitions_list, commands_list
        self.delay_start_t, self.delay_t = 0, 0


        self.characters = []
        self.locations = []
        self.images = []
        self.audios = []
        self.variables = []
        self.things = []
        self.taken_things = []
        
        self.window_text = []
        self.script = script
        self.svf = -1
        self.upd_lvl = True
    def init(self, script):
        p_names, p_ids = [a[0] for a in script.partitions], [a[1] for a in script.partitions]
        self.current_id = script.id2i(p_ids[p_names.index('BEGIN')])
        label = script.lines()[self.current_id].replace('BEGIN', '').split()[0]
        self.goto(script, label)
    def save(self):
        with open('savings/saving.pkl', 'wb') as f:
            if str(type(self.svf)) != "<class 'int'>":
                pickle.dump(self.svf, f, pickle.HIGHEST_PROTOCOL)
    def load(self, screen):
        with open('savings/saving.pkl', 'rb') as f:
            [self.taken_things, self.variables, label] = pickle.load(f)
        self.goto(self.script, label)
        for i in range(len(self.characters.list)):
            self.characters.list[i].textbox.clear()
            self.characters.list[i].visible = False
            self.characters.list[i].back_visible = False
        events = pg.event.get()
        self.update(events, screen)
    def update(self, events, screen):
        self.background.update(events, screen)
        if self.current_location != None:
            self.current_location.update(events, screen)
        for obj in self.characters.list:
            obj.update(events, screen, mode='back', GAME=self)
        for obj in self.characters.list:
            obj.update(events, screen, GAME=self)
        for obj in self.images.list:
            obj.update(events, screen)
        self.menu.update(events, screen, GAME=self)

    def delay(self, t):
        self.delay_start_t, self.delay_t = time.time(), t
    def goto(self, script, label):
        cnt = np.where(np.array(script.labels)[:, 0] == label)[0][0]
        self.current_id = script.labels[cnt][1]
        self.current_level = script.list[script.id2i(self.current_id)][2]
        self.set_location(script)
        self.svf = [self.taken_things, self.variables, label]
    def set_location(self, script):
        #идем вверх по скрипту и находим первую попавшуюся локацию
        for i in range(len(script.list)):
            line = script.list[script.id2i(self.current_id)-i][0]
            if line.find('LOCATION') != -1:
                loc_name = line.split()[line.split().index('LOCATION')+1]
                break
        last_name=''
        if self.current_location != None:
            last_name = self.current_location.name
        self.current_location = self.locations.get(obj_name=loc_name)
        self.svf = [self.taken_things, self.variables, loc_name]
        if self.current_location != None:
            if self.current_location.name != last_name:
                for i in range(len(self.characters.list)):
                    self.characters.list[i].hide()
                

    # value = select(options, screen)
    def select(self, options, screen):
        options = np.array(options)
        x, y = screen.get_size()
        select_buttons, shift = [], 0
        shadow = NC.image(image_name='shadow.png', size=screen.get_size(), alpha=25)
        events = pg.event.get()
        for i in range(12):
            shadow.update(events, screen)
            time.sleep(0.04)
            pg.display.update()
        for i in range(len(options)):
            size, fontsize = [int(x * 0.5), y], 20
            test = NC.textbox(size=size, font_size=fontsize)
            test.add_line(options[i][0])
            size[1] = len(test.text) * fontsize * 2
            select_buttons.append(NC.button(obj_name=str(i), image_name='select_button.png', button_text=options[i][1],
                                            position=[int(x * 0.2), int(y * 0.3) + shift], size=size, font_size=20))
            shift += size[1] + 15
        self.background = NC.image(image_name='default_background.png', size=(int(x*0.5)+50, shift + 50), position=[int(x * 0.2)-25, int(y * 0.3)-25])
        
        while 1:
            events = pg.event.get()
            #self.menu.update(events, screen, GAME=self)
            self.background.update(events, screen)
            for button in select_buttons:
                select = button.update(events, screen)
                if select != None:
                    return options[int(select)][0]
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit(), sys.exit()
            pg.display.update()
            
    def im_show(self, screen, image_name):
        x, y = screen.get_size()
        lx, ly = pg.image.load('graphics/images/' + image_name).get_size()
        scl = min((int(x*0.7)-100)/lx, (int(y*0.7)-100)/ly)
        
        self.image = NC.image(image_name=image_name, size=(int(lx*scl), int(ly*scl)), position=[int(x * 0.1)+50, int(y * 0.1)+50])
        self.background = NC.image(image_name='default_background.png', size=(int(x*0.7), int(y*0.7)), position=[int(x * 0.1), int(y * 0.1)])
        self.button = NC.button(obj_name='close', image_name='select_button.png', button_text='Закрыть', font_size=20, position=[int(x * 0.68)-60, int(y * 0.73)], size=(125, 25))
        
        pg.image.save(screen, 'graphics/images/tmp.jpg')
        shadow = NC.image(image_name='shadow.png', size=screen.get_size(), alpha=25)
        events = pg.event.get()
        for i in range(12):
            shadow.update(events, screen)
            self.background.update(events, screen)
            self.image.update(events, screen)
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
        tmp = NC.image(image_name='tmp.jpg', size=screen.get_size())
        tmp.update(events, screen)
        pg.display.update()
            
    def execute_script(self, script,  screen):
        if time.time() - self.delay_start_t > self.delay_t:
            curr_i = script.id2i(self.current_id)
            # если текущая строка на нашем уровне или ниже, выполняем ее. Обновляем текущий уровень
            if self.current_level >= script.list[curr_i][2]:
                self.execute_line(script,  screen, line=script.list[curr_i][0])
                curr_i = script.id2i(self.current_id)
                if self.upd_lvl:
                    self.current_level = script.list[curr_i][2]
                self.upd_lvl = True

            #идем на следующую строку, если встречаем другой вариант текущего IF, то спускаемся на уровень ниже
            if curr_i < len(script.list)-1:
                if self.linerun_flag == True:
                    self.current_id = script.list[curr_i + 1][1]
                    curr_i = script.id2i(self.current_id)
                    if self.current_id in script.terminators and self.current_level == script.list[curr_i-1][2]:
                        self.current_level -= 1
            self.linerun_flag = True
    def execute_line(self, script, screen, line):
        com_bool = False
        for command in self.commands_list:
            if command in line.split():
                com_bool = True
                if command == 'GOTO':
                    _, label = AF.extract_command(line, command, delete_command=False)
                    self.goto(script, label)
                    self.run_flag = False
                    break
                if command == 'IF':
                    cnt = [a[2] for a in script.conditions].index(self.current_id)
                    [variable, options, _] = script.conditions[cnt]
                    # ищем значение данной variable (от значения которой зависит выполнение IF) среди сделанных выборов
                    value = ''
                    for i in range(len(self.variables)):
                        if self.variables[-i-1][0] == variable:
                            value = self.variables[-i-1][1]
                            self.linerun_flag = False
                            break
                    # проверяем, есть ли записанное value данной variable среди options
                    
                    if value.replace(' ','') in [a[0].replace(' ','') for a in options]:
                        cnt = [a[0].replace(' ', '') for a in options].index(value.replace(' ', ''))
                        
                        self.current_id = options[cnt][1]
                        self.current_level = script.list[script.id2i(self.current_id)][2]
                        self.set_location(script)
                    else:
                        self.current_id = options[0][1]
                        self.upd_lvl = False
                if command == 'IF_OWN':
                    cnt = [a[2] for a in script.own_conditions].index(self.current_id)
                    [variable, options, _] = script.own_conditions[cnt]
                    
                    if str(type(self.taken_things)) !="<class 'list'>":
                        for value in [thing.obj_name for thing in self.taken_things.list]:
                            if value.replace(' ','') in [a[0].replace(' ','') for a in options]:
                                cnt = [a[0].replace(' ','') for a in options].index(value.replace(' ',''))
                                self.current_id = options[cnt][1]
                                self.current_level = script.list[script.id2i(self.current_id)][2]
                                self.set_location(script)
                                break
                            self.linerun_flag = False
                    else:
                        self.current_id = options[0][1]
                        self.upd_lvl = False
                if command == 'CASE':
                    cnt = [a[2] for a in script.cases].index(self.current_id)
                    [variable, options, _] = script.cases[cnt]
                    # select и добавление выбранной переменной в лист variables
                    sel_options = [[rec[0], rec[0]] for rec in options]
                    value = self.select(sel_options, screen)
                    self.variables.append([variable, value])
                    # переход к выбранному варианту как в IF
                    cnt = [a[0] for a in options].index(value)
                    self.current_id = options[cnt][1]
                    self.current_level = script.list[script.id2i(self.current_id)][2]
                    self.set_location(script)
                    self.linerun_flag = False
                if command == 'SELECT':
                    cnt = [a[2] for a in script.selections].index(self.current_id)
                    [variable, options, _] = script.selections[cnt]
                    value = self.select(options, screen)
                    self.variables.append([variable, value])
                if command == 'TAKE':
                    _, thing_name = AF.extract_command(line, command, delete_command=False)
                    if self.things.index(obj_name=thing_name)==None:
                        self.things.append(NC.thing(screen, obj_name=thing_name, name=thing_name))
                    thing=self.things.get(obj_name=thing_name)
                    if self.taken_things == []:
                        self.taken_things = NC.objlist(list=[thing])
                    else:
                        self.taken_things.append(thing)
                if command == 'REMOVE':
                    _, thing = AF.extract_command(line, command, delete_command=False)
                    if self.taken_things != []:
                        index = self.taken_things.index(obj_name=thing)
                        del self.taken_things.list[index]
                if command == '$':
                    line, obj_name = AF.extract_command(line, command, delete_command=True)
                    ind = self.characters.index(obj_name=obj_name)
                    self.characters.list[ind].textbox.add_line(line)
                    self.characters.list[ind].sleep = True
                    
                    for i in range(len(self.characters.list)):
                        if self.characters.list[i].obj_name != obj_name:
                            self.characters.list[i].textbox.clear()
                            self.characters.list[i].visible = False
                    if obj_name=='main':
                        self.characters.list[ind].show_left(screen)
                    else:
                        self.characters.list[ind].show_right(screen)
                if command == 'EVAL':
                    line, variable = AF.extract_command(line, command, delete_command=False)
                    value = ''.join([a + ' ' for a in line.split()[2:]])
                    self.variables.append([variable, value])
                if command in ['CH_RIGHT', 'CH_LEFT', 'CH_HIDE', 'CH_SMALL_RIGHT', 'CH_BACK']:
                    line, obj_name = AF.extract_command(line, command, delete_command=True)
                    if command != 'CH_BACK':
                        for ind in range(len(self.characters.list)):
                            self.characters.list[ind].visible = False
                    ind = self.characters.index(obj_name=obj_name)
                    if command == 'CH_RIGHT':
                        self.characters.list[ind].show_right(screen)
                    if command == 'CH_SMALL_RIGHT':
                        self.characters.list[ind].show_small_right(screen)
                    if command == 'CH_LEFT':
                        self.characters.list[ind].show_left(screen)
                    if command == 'CH_HIDE':
                        if ind == None:
                            for i in range(len(self.characters.list)):
                                self.characters.list[i].hide()
                        else:
                            self.characters.list[ind].hide()
                    if command == 'CH_BACK':
                        shifts = [self.characters.list[i].back_shift for i in range(len(self.characters.list)) if self.characters.list[i].back_visible]
                        shift = 0
                        while shift in shifts:
                            shift += 1
    
                        self.characters.list[ind].back_shift = shift
                        self.characters.list[ind].show_back(screen)
                        time.sleep(0.2)
                if command == 'PLAY_MUSIC':
                    self.audios.list[0].play()
                    _, obj_name = AF.extract_command(line, command, delete_command=True)
                    ind = self.audios.index(obj_name=obj_name)
                    self.audios.list[ind].play()
                if command == 'STOP_MUSIC':
                    pg.mixer.music.stop()
                if command == 'DELAY':
                    _, t = AF.extract_command(line, command, delete_command=True)
                    self.delay(int(t))
                if command == 'IM_SHOW':
                    line, image_name = AF.extract_command(line, command, delete_command=True)
                    self.im_show(screen, image_name)
                    '''ind = self.images.index(obj_name=obj_name)
                    self.images.list[ind].visible = True'''
                if command == 'IM_HIDE':
                    _, obj_name = AF.extract_command(line, command, delete_command=False)
                    if obj_name == 'ALL':
                        for ind in range(len(self.images.list)):
                            self.images.list[ind].visible = False
                    else:
                        ind = self.images.index(obj_name=obj_name)
                        self.images.list[ind].visible = False
                if command == 'SPECIAL':
                    _, func_name = AF.extract_command(line, command, delete_command=True)
                    ind = [a[0] for a in script.specials.list].index(func_name)
                    self, script = script.specials.list[ind][1](screen, self, script)
                if command == 'LOCATION':
                    self.set_location(script)
                    for i in range(len(self.characters.list)):
                        self.characters.list[i].hide()
                if command == 'WINDOW':
                    window = NC.window(screen, text_arr=self.window_text)
                    window.show(screen)
                    self.window_text=[]
                if command == 'EMOTION':
                    _, obj_name, val = line.split()
                    ind = self.characters.index(obj_name=obj_name)
                    self.characters.list[ind].emotion = val
                if command == 'VIDEO':
                    _, video_name = AF.extract_command(line, command)
                    print(video_name)
        if not com_bool:
            self.window_text.append(line)