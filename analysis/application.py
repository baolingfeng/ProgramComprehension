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


def load_controls(csv_file='controls.csv'):
    controls = {}
    with open(csv_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        lang_idx = {}
        for idx, row in enumerate(reader):
            if idx == 0:
                for idx2, lang in enumerate(row):
                    lang = lang.strip()
                    controls[lang] = []
                    lang_idx[idx2] = lang
                continue

            for idx2, c in enumerate(row):
                lang = lang_idx[idx2]

                controls[lang].append(c.strip())

    return controls


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
                if idx > 0:
                    window_name = parent_window[0:idx+1]
                    return True, window_name
                else:
                    return False, window_name

        else:
            idx = get_idx(window_name, app.names)
            idx2 = get_idx(parent_window, app.names)
            if idx > 0:
                window_name = window_name[0:idx+1]
                return True, window_name
            elif idx2 > 0:
                #window_name = parent_window[0:idx+1]
                return True, parent_window[0:idx2+1]
            else:
                return False, window_name
    else:
        print 'warning: the application %s is not defined in applications.csv' % process_name
        return True, window_name


controls = load_controls()


def is_control(en_name, name):
    idx = controls['English'].index(en_name)

    for lang in controls:
        if controls[lang][idx] == name:
            return True

    return False


def is_paste_event(e):
    if e['type'] == 'mouse' and 'action_name' in e:
        action_name = e['action_name'].lower()
        action_type = e['action_type']
        if is_control('menu item', action_type) and (action_name.find('paste') >= 0 or action_name.find('粘帖') >= 0):
            return True
    elif e['type'] == 'key':
        event_name = e['event_name']
        if event_name == 'Ctrl+V':
            return True

    return False


if __name__ == '__main__':
    #controls = load_controls()
    print is_control('menu item', '菜单项')
