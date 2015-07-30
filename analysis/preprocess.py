#!/usr/bin/env 
# -*- utf8 -*-
from rt import EventManager

data_path = '../data/user2/log'

with EventManager(data_path) as em:
    em.retrieve_events()
    #em.retrieve_events()
    em.filter_no_need()

    for idx, e in enumerate(em.combined_events):
        if e['type'] == 'key':
            if e['event_name'].find('Ctrl') >=0:
                print e 
    