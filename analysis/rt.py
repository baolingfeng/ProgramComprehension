#!/usr/bin/env 
# -*- coding: utf8 -*-

import util
import time_util
from sqlite_dbimpl import sqlite_query
import sqlite3
from application import load_applications
from application import is_main_window

class EventManager:
    """
    In ICPC2015 Paper:
    the idle period is determined if no interactions in 5 minutes
    the reaction time(RT) between low level events is set to 1 seconds. but it could be from 0.15 to 1.5 seconds 
    
    """
    def __init__(self, data_path):
        self.conn = sqlite3.connect(data_path + '/log.db3')
        self.idle_threshold = 5 * 60 # 5 minutes in icpc paper
        self.apps = load_applications("applications.csv")
        self.app_dict = {app.process:app for app in self.apps}
        self.rts = util.drange(0.2, 1.5, 0.2)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.conn.close()

    def retrieve_events(self, day=None):
        """
        if day is not none, get the events in one day,
        for example, day= '2015-07-08', the where condition is 
        'timestamp'>'2015-07-08 00:00:00.000' and 'timestamp'<2015-07-09 00:00:00.000'

        get mouse, keyboard, copy events from database, combine mouse and keyboard
        """

        self.day = day

        where_condition = ''
        if day:
            start_time = time_util.day2timestamp(day)
            end_time = time_util.next_day_timestamp(day)
            where_condition = " WHERE timestamp>'" + start_time + "' and timestamp<'" + end_time + "'"

        #print where_condition

        sql = 'select * from tbl_mouse_event' + where_condition
        self.mouse_events = sqlite_query(self.conn, sql)

        sql = 'select * from tbl_click_action' + where_condition
        click_actions = sqlite_query(self.conn, sql)

        click_time_map = {c['timestamp']: idx for idx, c in enumerate(click_actions)}
        for i in range(len(self.mouse_events)):
            t = self.mouse_events[i]['timestamp']
            if t in click_time_map:
                self.mouse_events[i].update(click_actions[click_time_map[t]])

        sql = 'select * from tbl_key_event' + where_condition
        self.key_events = sqlite_query(self.conn, sql)

        sql = 'select * from tbl_key_action' + where_condition
        key_actions = sqlite_query(self.conn, sql)
        key_time_map = {c['timestamp']: idx for idx, c in enumerate(key_actions)}
        for i in range(len(self.key_events)):
            t = self.key_events[i]['timestamp']
            if t in key_time_map:
                self.key_events[i].update(key_actions[key_time_map[t]])

        strsql = 'select * from tbl_copy_event'
        self.copy_events = sqlite_query(self.conn, strsql)

        self.combined_events = sorted(self.mouse_events + self.key_events, key=lambda k:k['timestamp'])
        total_length = len(self.combined_events)

        self.idle_times = []
        for i in range(0, total_length):
            if i == total_length - 1:
                self.combined_events[i]['duration'] = 0
            else:
                cur_t = self.combined_events[i]['timestamp']
                next_t = self.combined_events[i+1]['timestamp']
                interval = time_util.time_diff(cur_t, next_t)
                if interval > self.idle_threshold:
                    #print 'warning: maybe idle time. ', interval, cur_t, next_t
                    self.idle_times.append((cur_t, next_t, interval))
                    self.combined_events[i]['duration'] = 0
                else:
                    self.combined_events[i]['duration'] = interval

    def filter_no_need(self):
        """
        filter events whose name is 'UNKNOW' or process name is 'explorer.exe'
        'explorer.exe' is windows explorer or taskbar 
        """

        self.filter_events = []
        self.process_stat = {'UNKNOWN':0, 'explorer.exe':0}
        for e in self.combined_events:
            if e['event_name'] == 'UNKNOWN':
                self.process_stat['UNKNOWN'] += e['duration']
            elif e['process_name'] == 'explorer.exe':
                self.process_stat['explorer.exe'] += e['duration']
            else:
                if e['process_name'] in self.process_stat:
                    self.process_stat[e['process_name']] += e['duration']
                else:
                    self.process_stat[e['process_name']] = e['duration']

                self.filter_events.append(e)

        self.events_time_map = {e['timestamp']: idx for idx, e in enumerate(self.filter_events)}

    def aggregate_events_in_rts(self):
        self.rt_res = {}
        for rt in self.rts:
            self.rt_res[rt] = self.aggregate_events_in_rt(rt)

    def aggregate_events_in_rt(self, rt):
        rt_res = {'total_duration':0, 'total_number':0, 'nodefined_duration':0, 'nodefined_number':0}
        for app in self.apps:
            key = app.type
            rt_res[key+'_duration'] = 0
            rt_res[key+'_number'] = 0

        self.max_rt_events = []
        for idx, e in enumerate(self.filter_events):
            if e['duration'] > rt:
                app = self.get_application(e['process_name'])
                if app:
                    rt_res[app.type+'_duration'] += e['duration']
                    rt_res[app.type+'_number'] += 1
                else:
                    rt_res['nodefined_duration'] += e['duration']
                    rt_res['nodefined_number'] += 1

                if len(self.max_rt_events) < 10:
                    self.max_rt_events.append(e)
                elif e['duration'] > self.max_rt_events[0]['duration']:
                    self.max_rt_events[0] = e

                self.max_rt_events = sorted(self.max_rt_events, key=lambda k:k['duration'])

                rt_res['total_duration'] += e['duration']
                rt_res['total_number'] += 1

        return rt_res

    def aggregate_events_in_process(self):
        self.process_slices = util.list_slice(self.filter_events, lambda k:k['process_name'])

    def get_application(self, process_name):
        return self.app_dict[process_name] if process_name in self.app_dict else None

    def aggregate_events_in_window(self):
        self.window_slices = []
        last_prcess_window = {}

        for p in self.process_slices:
            process_name, start, end = p
            app = self.get_application(process_name)

            main_windows = []
            for i in range(start, end+1):
                me = self.filter_events[i]
                flag, window_name = is_main_window(me, app)

                if flag:
                    main_windows.append((i, window_name))
                    
            if len(main_windows)<=0:
                if process_name in last_prcess_window:
                    self.window_slices.append((process_name, last_prcess_window[process_name], start, end))
                continue

            slices = util.list_slice(main_windows, lambda k:k[1])       
            for sidx, s in enumerate(slices):
                idx1 = main_windows[s[1]][0]
                idx2 = main_windows[s[2]][0]
                window_name = s[0]

                if sidx == 0:
                    idx1 = start
                
                if sidx == len(slices)-1:
                    idx2 = end
                else:
                    idx2 = main_windows[slices[sidx+1][1]-1][0]

                self.window_slices.append((process_name, s[0], idx1, idx2))


            if len(self.window_slices)>0:
                last_prcess_window[process_name] = self.window_slices[-1][1]

    def get_window_title(self, event):
        idx = self.events_time_map[event['timestamp']]

        for w in self.window_slices:
            p, w, start, end = w

            if idx>=start and idx<=end:
                return w

        return event['window_name'] if event['window_name'] != '' else event['parent_window']

    def stat(self):
        filename = self.day if self.day else 'all'
        with open('stat_'+filename+'.txt', 'w') as statfile:
            start_time = em.combined_events[0]['timestamp']
            end_time = em.combined_events[-1]['timestamp']
            total_duration = time_util.time_diff(start_time, end_time) 
            print 'The time is from %s to %s, the total duration is %0.3f hour(s)' % (start_time, end_time, total_duration/3600)
            statfile.write('The time is from %s to %s, the total duration is %0.3f hour(s)\n\n' % (start_time, end_time, total_duration/3600))


            print 'Bellow time may be idle time (idle threshold %d minutes):' % (self.idle_threshold/60,)
            statfile.write('Bellow time may be idle time (idle threshold %d minutes):\n' % (self.idle_threshold/60,))
            total_idle = 0
            for idle in self.idle_times:
                total_idle += idle[2]
                print 'from %s to %s, duration is %0.3f minutes' % (idle[0], idle[1], idle[2]/60)
                statfile.write('from %s to %s, duration is %0.3f minutes\n' % (idle[0], idle[1], idle[2]/60))
            statfile.write('Total idle time: %0.3f hours, real working hours: %0.3f\n\n' % (total_idle/3600, (total_duration-total_idle)/3600))

            print 'Application Usage:'
            statfile.write('Application Usage:\n')
            process_list = [(key, self.process_stat[key]) for key in self.process_stat if key not in ('UNKNOWN', 'explorer.exe')]
            process_list = sorted(process_list, key=lambda k: k[1], reverse=True)
        
            for p in process_list:
                print 'Process: %s, Time: %0.3f minutes' % (p[0], p[1]/60)
                statfile.write('Process: %s, Time: %0.3f minutes\n' % (p[0], p[1]/60))
            print 'No Moniter Application Usage Time: %0.3f minutes' %  (self.process_stat['UNKNOWN']/60,)
            print 'Windows Explorer or Taskbar Usage Time: %0.3f minutes' %  (self.process_stat['explorer.exe']/60,)
            statfile.write('No Moniter Application Usage Time: %0.3f minutes\n' %  (self.process_stat['UNKNOWN']/60,))
            statfile.write('Windows Explorer or Taskbar Usage Time: %0.3f minutes\n' %  (self.process_stat['explorer.exe']/60,))
            statfile.write('\n')

            window_dict = {}
            for ws in self.window_slices:
                process_name, window_name, start, end = ws

                duration = 0
                for i in range(start, end+1):
                    duration += self.filter_events[i]['duration']

                if window_name in window_dict:
                    window_dict[window_name + ' - ' + process_name] += duration
                else:
                    window_dict[window_name + ' - ' + process_name] = duration

            window_list = [(key, window_dict[key]) for key in window_dict]
            window_list = sorted(window_list, key=lambda k:k[1], reverse=True)
            statfile.write('The top 10 longest application windows\n')
            for idx, w in enumerate(window_list):
                if idx<10:
                    statfile.write('Title: %s, Duration: %0.3f minutes\n' % (w[0], w[1]/60))
                    print w[0], w[1]
            statfile.write('\n')

            apptype_dict = {}
            for p in process_list:
                apptype = self.get_application(p[0]).type
                if apptype in apptype_dict:
                    apptype_dict[apptype] += p[1]
                else:
                    apptype_dict[apptype] = p[1]

            rt_list = [(key, self.rt_res[key]) for key in self.rt_res]
            rt_list = sorted(rt_list, key=lambda k:k[0])
            for res in rt_list:
                print 'Reaction Time %f' % (res[0])
                statfile.write('Reaction Time %f\n' % (res[0]))
                total_duration = res[1]['total_duration']
                total_number = res[1]['total_number']

                durations = [(key, res[1][key]) for key in res[1] if key.find('_duration')>0 and key!='total_duration']
                #numbers = [(key, res[1][key]) for key in res[1] if key.find('_number')>0 and key!='total_number']
                durations = sorted(durations, key=lambda k:k[1], reverse=True)
                #numbers = sorted(numbers, key=lambda k:k[1], reverse=True)

                print 'Total Reaction Time: %0.3f minutes, Number: %d' % (total_duration/60, total_number)
                for idx, d in enumerate(durations):
                    idx = d[0].find('_duration')
                    apptype = d[0][0:idx]
                    
                    if d[1] > 0:
                        apptype_total = apptype_dict[apptype]
                        print 'Application: %s, Duration: %0.3f minutes, Number: %d, Percentage: %0.2f%%' %(apptype, d[1]/60, res[1][apptype+'_number'], d[1]/apptype_total * 100)
                        statfile.write('Application: %s, Duration: %0.3f minutes, Number: %d, Percentage: %0.2f%%\n' %(apptype, d[1]/60, res[1][apptype+'_number'], d[1]/apptype_total * 100))
                statfile.write('\n')

            print 'The top 10 longest reaction time events:'
            statfile.write('The top 10 longest reaction time events:\n')
            for e in self.max_rt_events:
                print 'Timestamp: %s, Process: %s, Window: %s, Reaction Time: %0.3f seconds' % (e['timestamp'],e['process_name'], self.get_window_title(e), e['duration'])
                statfile.write('Timestamp: %s, Process: %s, Window: %s, Reaction Time: %0.3f seconds\n' % (e['timestamp'],e['process_name'], self.get_window_title(e), e['duration']))

if __name__ == '__main__':
    data_path = '../data/user2/log'

    with EventManager(data_path) as em:
        em.retrieve_events()
        #em.retrieve_events()
        em.filter_no_need()
        em.aggregate_events_in_rts()
        em.aggregate_events_in_process()
        em.aggregate_events_in_window()
        
        em.stat()
    