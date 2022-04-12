import sys, time, pygame_textinput, pylab, serial, pygame, os, pickle
import pygame as pg
import numpy as np
import NovClasses as NC
import AdditionalFuncs as AF
import Menu


with open('E://Games//Novell//company.pkl', 'rb') as f:
    company1 = pickle.load(f)
print(company1.list[0].image_name)