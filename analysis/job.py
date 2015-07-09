#!/usr/bin/env 
# -*- coding: utf8 -*-

import sys
import schedule
import time
import getpass
from rt import EventManager
import time_util

data_path = './log'
#data_path = 'D:/baolingfeng/GitHub/ProgramComprehension/data/user1/log'
user_name = getpass.getuser()

def job():
    try:
        print 'run job..... %s' % data_path

        #data_path = 'D:/baolingfeng/GitHub/ProgramComprehension/data/user1/log'
        day = time_util.today()

        outputfile = 'stat_' + user_name + '_' + day + '.txt'

        with EventManager(data_path) as em:
            em.retrieve_events(day)
            #em.retrieve_events()
            em.filter_no_need()
            em.aggregate_events_in_rts()
            em.aggregate_events_in_process()
            em.aggregate_events_in_window()
            
            em.stat(outputfile)
    except Exception, e:
        print e
   

if __name__ == '__main__': 
    execute_mode = 'day'   
    try:
        for idx, arg in enumerate(sys.argv):
            if idx == 0:
                continue

            if arg[0] == '-':
                if idx+1>=len(sys.argv):
                    raise Exception('arguement incomplete')

                next_arg = sys.argv[idx+1]
                if arg[1:] == 'data':
                    data_path = next_arg
                elif arg[1:] == 'u':
                    user_name = next_arg
                elif arg[1:] == 's':
                    execute_mode == next_arg

    except Exception, e:
        print e
    
    if execute_mode == 'hour':
        schedule.every().hour.do(job)
    elif execute_mode == 'day':
        schedule.every().day.at("18:00").do(job)
        schedule.every().day.at("23:30").do(job)
    elif execute_mode == 'second':
        schedule.every(10).seconds.do(job)
    else:
        print 'no schedule mode, just hour or day'
        sys.exit(0)

    while True:
        
        schedule.run_pending()
        time.sleep(1)

  