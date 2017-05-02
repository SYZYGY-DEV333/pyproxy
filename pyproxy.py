#!/usr/bin/env python3
# Copyright (c) 2017, SYZYGY-DEV333
# All rights reserved.
# Licensed under SPL 1.0 [splicense.pen.io]
# pyproxy

import os,sys,socket

try:
    import _thread
except ImportError:
    import _dummy_thread as _thread

#********* CONSTANT VARIABLES *********
BACKLOG = 50            # how many pending connections queue will hold
MAX_DATA_RECV = 999999  # max number of bytes we receive at once
DEBUG = True             # set to True to see the debug msgs
BLOCKED = []            # just an example. Remove with [""] for no blocking at all.

#**************************************
#********* MAIN PROGRAM ***************
#**************************************

def main():

    # check the length of command running
    if (len(sys.argv)<2):
        print("No port given, using :8080 (http-alt)") 
        port = 8080
    else:
        port = int(sys.argv[1]) # port from argument

    # host and port info.
    host = ''               # blank for localhost
    
    print("Proxy Server Running on ",host,":",port)

    try:
        # create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # associate the socket to host and port
        s.bind((host, port))

        # listenning
        s.listen(BACKLOG)
    
    except socket.error as xxx_todo_changeme:
        (value, message) = xxx_todo_changeme.args
        if s:
            s.close()
        print("Could not open socket:", message)
        sys.exit(1)

    # get the connection from client
    while 1:
        conn, client_addr = s.accept()

        # create a thread to handle request
        _thread.start_new_thread(proxy_thread, (conn, client_addr))
        
    s.close()
#************** END MAIN PROGRAM ***************

def printout(type,request,address):
    if "Block" in type or "Blacklist" in type:
        colornum = 91
    elif "Request" in type:
        colornum = 92
    elif "Reset" in type:
        colornum = 93

    print("\033[",colornum,"m",address[0],"\t",type,"\t",request,"\033[0m")

#*******************************************
#********* PROXY_THREAD FUNC ***************
# A thread to handle request from browser
#*******************************************
def proxy_thread(conn, client_addr):

    # get the request from browser
    request = conn.recv(MAX_DATA_RECV)

    # parse the first line
    first_line = request.split('\n'.encode())[0]

    # get url
    url = first_line.split(' '.encode())[1]

    for i in range(0,len(BLOCKED)):
        if BLOCKED[i] in url:
            printout("Blacklisted",first_line,client_addr)
            conn.close()
            sys.exit(1)


    printout("Request",first_line,client_addr)
    # print "URL:",url
    # print
    
    # find the webserver and port
    http_pos = url.find("://".encode())          # find pos of ://
    if (http_pos==-1):
        temp = url
    else:
        temp = url[(http_pos+3):]       # get the rest of url
    
    port_pos = temp.find(":".encode())           # find the port pos (if any)

    # find end of web server
    webserver_pos = temp.find("/".encode())
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos==-1 or webserver_pos < port_pos):      # default port
        port = 80
        webserver = temp[:webserver_pos]
    else:       # specific port
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]

    try:
        # create a socket to connect to the web server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        s.connect((webserver, port))
        s.send(request)         # send request to webserver
        
        while 1:
            # receive data from web server
            data = s.recv(MAX_DATA_RECV)
            
            if (len(data) > 0):
                # send to browser
                conn.send(data)
            else:
                break
        s.close()
        conn.close()
    except socket.error as xxx_todo_changeme1:
        (value, message) = xxx_todo_changeme1.args
        if s:
            s.close()
        if conn:
            conn.close()
        printout("Peer Reset",first_line,client_addr)
        sys.exit(1)
#********** END PROXY_THREAD ***********
    
if __name__ == '__main__':
    main()
