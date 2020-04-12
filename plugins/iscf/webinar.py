import os
import pandas as pd
import html
import heapq
from pytz import timezone
from datetime import datetime, timedelta

WB_INDEX = 'webinars'

def submit(db, args):

    if len(args) != 3:
        return 'Something is missing. You should follow "<NAME> <DD/MM/YYYY hh:mm AM/PM> <WEBINAR_LINK>" format to submit a webinar'
    
    if not db.get(WB_INDEX, False):
        db[WB_INDEX] = []
    
    try:
        parsed_date = datetime.strptime(args[1] + ' +0530', '%d/%m/%Y %I:%M %p %z')
    except:
        return 'Date should be formatted as <DD/MM/YYYY hh:mm AM/PM>. eg: "12/04/2020 3:05 PM"'

    now = datetime.now(timezone('Asia/Kolkata'))

    if parsed_date < now:
        return 'Is this webinar a ghost? Buddy, check the date. You are living in the past.'

    temp_heap = db[WB_INDEX]

    heapq.heappush(temp_heap, (parsed_date, {
        'name': args[0],
        'link': args[2]
    }))

    db[WB_INDEX] = temp_heap
    
    return html.escape('Thanks!! You submitted **' + args[0] + '** which is scheduled at **' + datetime.strftime(parsed_date, '%d %b, %Y %I:%M %p') + '**.')

# args: !wb get 3
def get(db, args):
    if not db.get(WB_INDEX, False):
        return 'Sorry. No upcoming events.'
    
    num = 0

    if len(args) == 0:
        num = 5
    elif len(args) == 1:
        try:
            num = int(args[0])
        except:
            return 'You entered a non numeric value as the argument.'
    else:
        return 'You should enter number of upcoming webinars as an argument.'
    
    

    res = ''
    #stop_at = num if num < len(db[WB_INDEX]) else len(db[WB_INDEX])
    heap = db[WB_INDEX]
    cnt = 0
    while(True):
        if cnt >= num or len(heap) == 0 or cnt >= len(heap):
            break
        
        if heap[0][0] < datetime.now(timezone('Asia/Kolkata')):
            heapq.heappop(heap)
        else:
            res = display_format(res, heap[cnt][1]['link'], heap[cnt][1]['name'], heap[cnt][0])
            cnt = cnt + 1

    db[WB_INDEX] = heap
    
    if res == '':
        return 'Sorry. No upcoming events.'
    return html.escape(res)

def notify(self):
    if not self.get(WB_INDEX, False):
        return

    heap = self[WB_INDEX]
    cnt = 0
    res = ''
    while(True):
        if len(heap) == 0 or cnt >= len(heap):
            break
        
        cnt = cnt + 1
        if heap[0][0] < (datetime.now(timezone('Asia/Kolkata')) + timedelta(minutes = 10)):
            res = display_format(res, display_format('', heap[0][1]['link'], heap[0][1]['name'], heap[0][0]))
            heapq.heappop(heap)
    
    if res != '':
        self.send(self.build_identifier("#events"), html.escape('**Upcoming Events**\n' + res))
    
    self[WB_INDEX] = heap

def display_format(res, link, name, time):
    res = res + 'Name: <' + link + '|**' + name + '**>. \nDate and Time: **' + datetime.strftime(time, '%d %b, %Y %I:%M %p') + '** \n\n'
    return res

if '__main__' == __name__:
    print(submit({}))