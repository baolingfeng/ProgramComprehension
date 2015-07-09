from datetime import datetime
from datetime import timedelta

#defalut_fmt = %Y-%m-%dT%H:%M:%SZ
defalut_fmt = '%Y-%m-%d %H:%M:%S.%f'

def from_unix_time(timestamp, FMT=defalut_fmt):
    int_time = timestamp
    if type(int_time) == str:
        int_time = int(int_time)

    return datetime.fromtimestamp(int_time).strftime(FMT)

def format_datetime(dt, FMT=defalut_fmt):
    return dt.strftime(FMT)

def now(FMT=defalut_fmt):
    return format_datetime(datetime.now(), FMT)

def today(FMT='%Y-%m-%d'):
    return format_datetime(datetime.now(), FMT)

def get_interval(tdelta, mode='m'):
    if mode == 'm':
        return tdelta.total_seconds() / 60.0 
    elif mode == 's':
        return tdelta.total_seconds()
    elif mode == 'h':
        return tdelta.total_seconds() / 3600.0
    elif mode == 'd':
        return tdelta.days
    elif mode == 'mi':
        return tdelta.total_seconds() * 1000
    else:
        return tdelta.total_seconds()

def time_diff(t1, t2, FMT=defalut_fmt, mode='s'):
    #tdelta = datetime.strptime(t2, FMT) - datetime.strptime(t1, FMT)
    return time_interval(datetime.strptime(t1, FMT), datetime.strptime(t2, FMT), mode)

#unix timestamp
def time_interval(dt1, dt2, mode='s'):
    if dt1 < dt2:
        return get_interval(dt2 - dt1, mode)
    else:
        return 0 - get_interval(dt1 - dt2, mode) 

def time_interval_unix(t1, t2, mode='s'):
    dt1 = datetime.fromtimestamp(t1)
    dt2 = datetime.fromtimestamp(t2)

    return time_interval(dt1, dt2)


def from_now_unix(unix_time, mode='s'):
    if type(unix_time) == str:
        unix_time = int(unix_time)

    return time_interval(datetime.now(), datetime.fromtimestamp(unix_time), mode)

def to_unix_time(dt, epoch=datetime(1970,1,1)):
    td = dt - epoch
    # return td.total_seconds()
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6

def str_to_unix_time(timestr, FMT=defalut_fmt):
    return to_unix_time(datetime.strptime(timestr, FMT))

def is_in_day(timestr, day, FMT=defalut_fmt):
    dt = datetime.strptime(timestr, defalut_fmt)
    dt2 = datetime.strptime(day, '%Y-%m-%d')
    return dt.date() == dt2.date()

def day2timestamp(day, FMT=defalut_fmt):
    dt = datetime.strptime(day, '%Y-%m-%d')
    return datetime.strftime(dt, defalut_fmt)

def day_with_interval(day, interval, FMT='%Y-%m-%d'):
    dt = datetime.strptime(day, FMT)
    next_dt = dt + timedelta(days=interval)

    return datetime.strftime(next_dt, FMT)

def next_day_timestamp(day):
    dt = datetime.strptime(day, '%Y-%m-%d')
    next_dt = dt + timedelta(days=1)

    return datetime.strftime(next_dt, defalut_fmt)

if __name__ == '__main__':
    #print datetime.now()
    #print to_unix_time(datetime.now())
    #print str_to_unix_time('2015-06-25 17:11:53.442')
    #print time_diff('2015-06-25 15:31:54.299','2015-06-25 15:31:42.892')
    #print time_diff('2015-06-25 15:31:54.299','2015-06-25 15:31:42.892', FMT=defalut_fmt, mode='mi')
    
    print day_with_interval('2015-07-08', -2)
