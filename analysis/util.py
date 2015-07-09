#!/usr/bin/env 
# -*- coding: utf8 -*-

def handleError(function):
    """
    wrapper for handle exception
    """
    def handleProblems(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception, e:
            #logger.error(e.message)
            print function, e

    return handleProblems

#@handleError
def list_slice(tuples, lambda_func):
    try:
        start, i = 0, 1
        pre = lambda_func(tuples[start])

        slices = []
        while i < len(tuples):
            cur = lambda_func(tuples[i])
                
            if pre != cur:
                slices.append((pre, start, i-1))       
                start = i
                pre = lambda_func(tuples[start])

            i+=1

        aslice = []

        slices.append((pre, start, i-1))

        return slices
    except Exception, e:
        print tuples

def drange(start, stop, step):
    while start < stop:
        yield start
        start += step

if __name__ == '__main__':
    a= [(1,1),(1,1),(2,2),(2,3),(1,1),(2,2),(2,3),(2,3)]
    b = [{'p':'a'}, {'p':'a'},{'p':'b'},{'p':'a'},{'p':'a'},{'p':'b'},{'p':'a'},{'p':'a'}]

    print list_slice(a, lambda k:k[0])
    print list_slice(b, lambda k:k['p'])
