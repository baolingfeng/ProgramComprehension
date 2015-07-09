#!/usr/bin/env 
# -*- coding: utf8 -*-

import csv

class Application:
    """
    defined application
    process: process name
    name: the application window title is usually 'File Path - Name', used to determine whether the window is main window
        for example, Firefox(firefox.exe), name='Mozilla Firefox', its window title is page title - Mozilla Firefox
    type: browser, IDE, text editor, office, pdf reader, etc
    suffixes: file suffix
    """
    def __init__(self, process, name, apptype, chs_name='', suffixes=''):
        self.process = process
        self.names = name
        self.type = apptype
        self.chs_names = chs_name
        self.suffixes = suffixes

    def __str__(self):
        return self.process + ', ' + self.name + ', ' + self.type + ', ' + self.chs_name + ', ' + self.suffixes

def load_applications(csv_file='applications.csv'):
    applications = []
    with open(csv_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for idx, row in enumerate(reader):
            if idx == 0:
                continue

            process = row[0].strip()
            names = row[1].strip().split('|')
            chs_names = row[2].strip().split('|')
            apptype = row[3].strip()
            suffixes = row[4].strip().split('|')

            applications.append(Application(process, names, apptype, chs_names, suffixes))

    return applications

def remove_special_char(window_name):
    """
    remove some special character since the file is modified and its name will add '*' or '?', etc or not recognized char
    """
    special_chars = ['*', '?']
    for c in special_chars:
        window_name = window_name.replace(c, '')
    
    return window_name.strip()

def get_idx(window_name, names):
    for name in names:
        idx = window_name.find(' - ' + name)
        if idx > 0:
            return idx

    return -1

def is_main_window(event, app):
    window_name = remove_special_char(event['window_name'])
    parent_window = remove_special_char(event['parent_window'])
    process_name = event['process_name']

    if app:
        if app.type == 'Office':
            for s in app.suffixes:
                idx = get_idx(parent_window, app.names)
                if idx>0:
                    window_name = parent_window[0:idx+1]
                    return True, window_name
                else:
                    return False, window_name

        else:
            idx = get_idx(window_name, app.names)
            idx2 = get_idx(parent_window, app.names)
            if idx>0:
                window_name = window_name[0:idx+1]
                return True, window_name
            elif idx2>0:
                #window_name = parent_window[0:idx+1]
                return True, parent_window[0:idx2+1]
            else:
                return False, window_name     
    else:
        print 'warning: the application %s is not defined in applications.csv' % process_name
        return True, window_name

if __name__ == '__main__':
    window_name = 'Chrome Legacy Window'
    parent_window = 'MPS MP2359 1.2A, 24V, 1.4MHz Step-Down Converter. Available in SOT23-6 and TSOT23-6 Packages - Google Chrome'
    idx = window_name.find(' - '+'Google Chrome')
    idx2 = parent_window.find(' - '+'Google Chrome')
    if idx>0:
        window_name = window_name[0:idx+1]
        print True, window_name
    elif idx2>0:
        #window_name = parent_window[0:idx+1]
        print parent_window
        print True, parent_window[0:idx2+1]
    else:
        print False, window_name     