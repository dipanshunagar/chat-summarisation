import sys
import re
date = r"[0-9][0-9]?/[0-9][0-9]?/[0-9][0-9]?"
time = r"[0-9][0-9]?:[0-9][0-9]?"

def getStats(filename):
    chatlog = []
    with open(filename) as chat:
        for line in chat:
            m = re.search(r"^"+ date + r",[\s]" + time +"[\s](AM)?(am)?(PM)?(pm)?[\s]", line)
            if m:
                matchedstr = m.group(0)[:]
                message = re.search(r"- .+", line)
                if message:
                    item = [matchedstr.split(",")[0], message.group(0)[:]]
                    chatlog.append(item)
    contents = []
    tempDate = ""
    i = 0 #Total number of messages
    sum = 0 #for average messages in a day
    days = 0 #total number of days
    messages = 0 #messages per day
    for msg in chatlog:
        if msg[0] == tempDate:
            messages = messages + 1
        else:
            i=i+1
            days = days+1
            sum=sum+messages  #For calculating average.
            messages=0
            tempDate = msg[0]
    avg = len(chatlog) / days
    print '\nTotal number of messages: '+str(len(chatlog)), '\nNumber of Days: '+str(days), '\n'
        
def nMessages(contents):
    print 'Total number of messages: ' + len(contents)

def nDays(contents):
    print 'Number of days: ' + len(set(contents))

def nAvgMessages(contents):
    prevDay = contents[0]
    for day in contents:
        if day[0] == prevDay:
            pass
def main():
    if len(sys.argv) <= 1:
        print """
        Usage: python stats.py <chat corpus>
        """
        return

    getStats(sys.argv[1])
if __name__ == '__main__':
   main()
