#!/usr/bin/env 
# -*- coding: utf8 -*-

import ftplib
import util
import os

@util.handleError
def send_to_ftp(filename, filepath, host, user, password):
    print 'begin to send %s to ftp' % filename

    session = ftplib.FTP(host, user, password)
    file = open(os.path.join(filepath, filename),'rb')                  # file to send
    session.storbinary('STOR ' + filename, file)     # send the file
    file.close()                                    # close file and FTP
    session.quit()

    print 'success to send!!!'

if __name__ == '__main__':
    send_to_ftp('__init__.py', '', '127.0.0.1', 'user', '123456')