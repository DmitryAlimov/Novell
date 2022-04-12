import sys, time
import pygame as pg
import NovClasses as NC
import numpy as np


def parameter_line_parcing(line):
    pars, vals, labeling, cnt = [], [], [0], 0
    for i in range(len(line)):
        if line[i] in [',', '=']:
            labeling.append(i)
    labeling.append(len(line))

    for i in range(len(labeling) - 1):
        split = line[labeling[i]:labeling[i+1]].replace(',', '').replace('=', '').replace('"', '').replace("'", '').split()
        string = split[0]
        for j in range(1, len(split)):
            string += ' ' + split[j]
        if cnt % 2:
            vals.append(string)
        else:
            pars.append(string)
        cnt += 1
    return pars, vals


def extract_command(line, command, delete_command=True):
    if command in line.split():
        value = line.split()[line.split().index(command) + 1]
        value = value.replace(':', '')
        if delete_command == True:
            line = line[0:line.find(command)] + line[line.find(command) + len(command):len(line)]
            line = line[0:line.find(value)] + line[line.find(value) + len(value):len(line)]
    if len(line.split()) > 0:
        if ':' in line.split()[0]:
            line = line.replace(":", " ")
    return line, value


def load_characters(screen, lines):
    characters = []
    for line in lines:
        pars, vals = parameter_line_parcing(line)
        small_image_name, large_image_name, color, font = 'default_character.png', 'default_character.png', 'black', 'Verdana-Bold.ttf'
        if "small_image_name" in pars:
            small_image_name = vals[pars.index("small_image_name")]
        if "large_image_name" in pars:
            large_image_name = vals[pars.index("large_image_name")]
        if "color" in pars:
            color = vals[pars.index("color")]
        if "font" in pars:
            font = vals[pars.index("font")]
        characters.append(
            NC.character(screen, name=vals[0], obj_name=pars[0], small_image_name=small_image_name, large_image_name=large_image_name, color=color, font=font))
    return characters


def load_locations(screen, lines):
    locations = []
    for line in lines:
        pars, vals = parameter_line_parcing(line)
        image_name = 'default_location.png'
        if "image_name" in pars:
            image_name = vals[pars.index("image_name")]
        locations.append(NC.location(screen, obj_name=pars[0], name=vals[0], image_name=image_name))
    return locations


def load_images(screen, lines):
    images = []
    for line in lines:
        pars, vals = parameter_line_parcing(line)
        image_name, position, size = 'default_scene.png', [0, 0], (0,0)
        if "image_name" in pars:
            image_name = vals[pars.index("image_name")]
        if "position" in pars:
            position = vals[pars.index("position")]
            position = [int(a) for a in position.replace('.', ' ').split()]
        if "size" in pars:
            size = vals[pars.index("size")]
            size = [int(a) for a in size.replace('.', ' ').split()]
        images.append(NC.image(obj_name=pars[0], image_name=image_name, position=position, size=size, visible=False))
    return images


def load_audios(screen, lines):
    audios = []
    for line in lines:
        pars, vals = parameter_line_parcing(line)
        audio_name = 'default_audio.wav'
        '''if "abc" in pars:
            abc = vals[pars.index("abc")]'''
        audios.append(NC.audio(obj_name=pars[0], audio_name=vals[0]))
    return audios


def load_things(screen, lines):
    things = []
    for line in lines:
        pars, vals = parameter_line_parcing(line)
        image_name, size, position = 'default_thing.png', (0, 0), [200, 200]
        if "image_name" in pars:
            image_name = vals[pars.index("image_name")]
        if "position" in pars:
            position = vals[pars.index("position")]
            position = [int(a) for a in position.replace('.', ' ').split()]
        if "size" in pars:
            size = vals[pars.index("size")]
            size = [int(a) for a in size.replace('.', ' ').split()]
        things.append(NC.thing(screen, obj_name=pars[0], name=vals[0], image_name=image_name, size=size, position=position))
    return things


def load_labels(script):
    labels, labels_ids = [], []
    for label_type in ['LABEL', 'LOCATION']:
        lines, run_flag = script.lines(), True
        while run_flag:
            run_flag = False
            for i in range(len(script.list)):
                if label_type in lines[i].split() and (script.list[i][1] in labels_ids) == False:
                    if label_type == 'LOCATION':
                        delete_command = False
                    if label_type == 'LABEL':
                        delete_command = True
                    script.list[i][0], label = extract_command(lines[i], label_type, delete_command=delete_command)
                    labels.append([label, script.list[i][1]])
                    labels_ids.append(script.list[i][1])
                    run_flag = True
    return labels, script


def load_selections(script, screen):
    selections, selections_ids, run_flag = [], [], True

    while run_flag:
        run_flag = False
        for i in range(len(script.list)):
            lines = script.lines()
            if i < len(lines):
                if 'SELECT' in lines[i].split() and (script.list[i][1] in selections_ids) == False:
                    for j in range(i+1, len(lines)):
                        if 'END' in lines[j].split():
                            break
                    lines[i], variable = extract_command(line=lines[i], command='SELECT', delete_command=False)

                    options = []
                    for cnt in range(i + 1, j):
                        if lines[cnt].find('#') != -1:
                            lines[cnt], value = extract_command(line=lines[cnt], command='#', delete_command=True)
                            options.append([value, lines[cnt]])
                        else:
                            options[-1][1] = options[-1][1] + ' ' + lines[cnt]

                    script.list[i][0], script.list[j][0] = 'SELECT', ''
                    selections.append([variable, options, script.list[i][1]])
                    selections_ids.append(script.list[i][1])
                    for _ in range(i, j):
                        del script.list[i+1]
                    run_flag = True
    return selections, script

def load_conditions(script, screen):
    conditions, own_conditions, cases, lines = [], [], [], script.lines()
    layer = 0
    for i in range(len(lines)):
        if 'END' in lines[i].split():
            layer -= 1
        script.list[i][2] = layer
        if 'IF' in lines[i].split() or 'IF_OWN' in lines[i].split() or 'CASE' in lines[i].split():
            layer += 1
    run_flag, condition_ids = True, []

    while run_flag:
        run_flag = False
        for i in range(len(lines)):
            if ('IF' in lines[i].split() or 'IF_OWN' in lines[i].split() or 'CASE' in lines[i].split()) and (script.list[i][1] in condition_ids) == False:
                i_start, layer_start = i, script.list[i][2]
                #находим конец блока IF
                for j in range(i, len(lines)):
                    if 'END' in lines[j].split() and layer_start == script.list[j][2]:
                        i_stop = j
                        break
                #находим options
                options = []
                for j in range(i_start+1, i_stop):
                    if script.list[j][2] == layer_start+1 and lines[j].find('#')!=-1 and 'CASE' in lines[i].split():
                        i_min, i_max = lines[j].find('#')+1, lines[j].find(':')
                        if i_min == -1:
                            i_min = 0
                        if i_max == -1:
                            i_min = len(lines[j])
                        value = lines[j][i_min:i_max]
                        script.list[j][0], _ = extract_command(line=lines[j], command='#', delete_command=True)
                        script.list[j][0] = ''
                        options.append([value, script.list[j][1]])
                    if script.list[j][2] == layer_start+1 and lines[j].find('#')!=-1 and not('CASE' in lines[i].split()):
                        i_min, i_max = lines[j].find('#')+1, lines[j].find(':')
                        if i_min == -1:
                            i_min = 0
                        if i_max == -1:
                            i_min = len(lines[j])
                        value = lines[j][i_min:i_max]
                        script.list[j][0] = ''
                        options.append([value, script.list[j][1]])
                # записываем conditions
                if 'IF' in lines[i].split():
                    _, variable = extract_command(line=lines[i_start], command='IF', delete_command=True)
                    conditions.append([variable, options, script.list[i][1]])
                if 'IF_OWN' in lines[i].split():
                    _, variable = extract_command(line=lines[i_start], command='IF_OWN', delete_command=True)
                    own_conditions.append([variable, options, script.list[i][1]])
                if 'CASE' in lines[i].split():
                    _, variable = extract_command(line=lines[i_start], command='CASE', delete_command=True)
                    cases.append([variable, options, script.list[i][1]])
                # записываем condition_ids, чтобы показать, что уже записали данный блок
                condition_ids.append(script.list[i][1])
                run_flag = True
    return conditions, own_conditions, cases, script


