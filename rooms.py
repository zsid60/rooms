#!/bin/env python
import datetime
import os
import requests
import string
import sys
import time

DIBS="https://ucsd.evanced.info/dibsapi"
GEISEL_ID=1001
BME_ID=1000
TIME_FMT="%Y-%m-%dT%H:%M:%S"

rooms = {}

def getTimeTable():
    times = []
    dt = datetime.datetime(2017,1,1, 8, 0, 0)
    end = datetime.datetime(2017, 1, 1, 23, 29, 0)
    step = datetime.timedelta(minutes=30)

    while dt < end:
        times.append("%-8s" % (dt.strftime("%H:%M-"))) 
        dt += step
    return times


def getRooms(times):
    roomData = requests.get("%s/rooms/" % DIBS).json()
    for room in roomData:
        rooms[room['RoomID']] = \
            (room['BuildingID'] % 1000, string.strip(room['Name'], "\r\n"), 
             times[:])

def printRooms():
    for rid, rm in rooms.iteritems():
        print "%s:\t%s" % (rid, rm)

def getTimeRange(roomHours):
    raw_end = roomHours['EndTime']
    raw_start = roomHours['StartTime']
    t_start = time.strptime(raw_start, TIME_FMT) 
    t_end = time.strptime(raw_end, TIME_FMT)
    start_idx = (t_start.tm_hour - 8) * 2
    if (t_start.tm_min):
        start_idx += 1
    end_idx = (t_end.tm_hour - 8) * 2
    if (t_end.tm_min):
        end_idx += 1
    return start_idx, end_idx


def reserve(rId, startIdx, endIdx):
    for i in range (startIdx, endIdx):
        rooms[rId][2][i] = "%-8s" % ("-" * 6)
 

def getReservations():
    today = datetime.date.today()
    todayStr = "%d-%d-%d" % (today.year, today.month, today.day) 
    todayQuery = "%s/reservations/%s/" % (DIBS, todayStr)

    for i in rooms:
        rs = requests.get("%s/%d" % (todayQuery, i)).json()
        for r in rs:
            start, end = getTimeRange(r)
            reserve(i, start, end)


def printReservations():
    for rId, room in rooms.iteritems():
        print "%-25.20s%s" % ("%s:" % room[1], "".join(room[2]))

def main(args):
   getRooms(getTimeTable())
   getReservations()
   printReservations()





if __name__ == '__main__':
    main(sys.argv)
