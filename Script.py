import sys, time, pygame_textinput, pylab, serial, pygame, os
import pygame as pg
import numpy as np
import AdditionalFuncs as AF


class script(object):
    def __init__(self, fname='scripts/Script.txt', partitions_list=[], commands_list=[]):
        input = open('scripts/' + fname, 'r', encoding = 'utf-8').readlines()
        input.append('\n')
        input[len(input)-2]+= '\n'
        input = [line for line in input if len(line.split()) != 0 if line.split()[0][0] != '%']
        full_input=[]
        for line in input:
            if 'INCLUDE' in line.split():
                _, fname = AF.extract_command(line, 'INCLUDE')
                chapter = open('scripts//' + fname, 'r', encoding = 'utf-8').readlines()
                chapter.append('\n')
                chapter[len(chapter)-2]+= '\n'
                chapter = [line for line in chapter if len(line.split()) != 0 if line.split()[0][0] != '%']
                for line in chapter:
                    full_input.append(line)
            else:
                full_input.append(line)
        full_input = [line.replace("'", '"') for line in full_input]
            
        # строки скрипта хранятся в виде списка из [string, id, level] где id-типа порядковый номер, level - уровень вложенности по IF (аналог табов в питоне)
        self.list = [[full_input[i][0:len(full_input[i]) - 1], i, 0] for i in range(len(full_input)) if len(full_input[i]) > 1]

        self.partitions = []
        for i in range(len(self.lines())):
            # коректируем написание команд
            for a in np.append(commands_list, partitions_list):
                if not (a in ['IF', 'LOCATION']):
                    self.list[i][0] = self.list[i][0].replace(a, ' ' + a + ' ')
            #self.list[i][0] = self.list[i][0].replace('CASE', 'CASE OF')
            self.list[i][0] = self.list[i][0].replace('IF_OWN', 'IF_OWN OF')

            #убираем табы
            line_without_tabs = ''
            for l in self.list[i][0].split():
                line_without_tabs = line_without_tabs + l + ' '
            self.list[i][0] = line_without_tabs

            #записываем partitions_list, состоящий из ["partition", ind]
            for a in partitions_list:
                if a in self.lines()[i].split():
                    self.partitions.append([a, self.ids()[i]])

        self.labels = []
        self.selections = []
        self.conditions = []
        self.own_conditions = []
        self.cases = []
        self.specials = []
        self.terminators = []
    def lines(self):
        return [a[0] for a in self.list]
    def ids(self):
        return [a[1] for a in self.list]
    def layers(self):
        return [a[2] for a in self.list]
    def id2i(self, id):
        # преобразует id строки в порядковый номер в списке
        ids = self.ids()
        for i in range(len(ids)):
            if id == ids[i]:
                break
        return i
    def get_partition_lines(self, inp, lines_only=True):
        # возвращает кусок script.list, соответствующий данному partition. Если lines_only=True, то только кусок script.lines()
        L = len(self.partitions)
        names, inds = [self.partitions[i][0] for i in range(L)], [self.partitions[i][1] for i in range(L)]
        if names.index(inp) < len(names) - 1:
            rng = np.arange(inds[names.index(inp)] + 1, inds[names.index(inp) + 1])
        else:
            rng = np.arange(inds[names.index(inp)], len(self.list))
        if lines_only==True:
            return [self.list[i][0] for i in range(len(self.list)) if i in rng]
        if lines_only==False:
            return [self.list[i] for i in range(len(self.list)) if i in rng]
    def print(self):
        for l in self.list:
            print(l[1], l[2], l[0])
        print('______________________________________________________________')
    def remove_ENDs(self):
        for i in range(len(self.list)):
            self.list[i][0] = self.list[i][0].replace('END', '')
    def set_terminators(self):
        #находит номера строк, где стоят варианты развилок "#value: bla-bla"
        for i in range(len(self.conditions)):
            options = self.conditions[i][1]
            for rec in options:
                self.terminators.append(rec[1])
        for i in range(len(self.own_conditions)):
            options = self.own_conditions[i][1]
            for rec in options:
                self.terminators.append(rec[1])
        for i in range(len(self.cases)):
            options = self.cases[i][1]
            for rec in options:
                self.terminators.append(rec[1])
