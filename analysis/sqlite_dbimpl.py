#!/usr/bin/env 
# -*- coding: utf8 -*-

import util
import sqlite3

@util.handleError
def sqlite_query(conn, sql, *arg):
    """
    this function is query the result from sqlite database
    paramter: sqlite database connection, and sql 
    return: a result list with each instance is a dict whose key is column dependent on sql
    """
    cur = conn.cursor()
    cur.execute(sql, arg)

    columns = list(map(lambda x: x[0], cur.description))

    datas = cur.fetchall()

    map_datas = []
    for d in datas:
        m = dict()
        for idx, c in enumerate(columns):
            v = d[idx]
            if type(v) == unicode:
                v = v.replace('\x00', '')
                v = v.encode('utf8', 'ignore')
                #print v

            m[c] = v

        map_datas.append(m)

    cur.close()
    return map_datas

@util.handleError
def sqlite_query_one(conn, sql, *arg):
    """
    fetch one result from database
    parameters are the same as sqlite_query
    return: only one record if exists
    """
    cur = conn.cursor()
    cur.execute(sql, arg)

    columns = list(map(lambda x: x[0], cur.description))

    data = cur.fetchone()
    m = dict()
    for idx, c in enumerate(columns):
        v = data[idx]
        if type(v) == unicode:
            v = v.replace('\x00', '')
            v = v.encode('utf8', 'ignore')

        m[c] = v

    return m

if __name__ == '__main__':
    sqlite_conn = sqlite3.connect('log.db3')
    res = sqlite_query_one(sqlite_conn, 'select * from tbl_key_event')
    print res