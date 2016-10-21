import codecs
import re
import sys
date = r"[0-9][0-9]?/[0-9][0-9]?/[0-9][0-9]?"
time = r"[0-9][0-9]?:[0-9][0-9]?"

#Parse chat log
def getChat(filename):
    chatlog = []
    with codecs.open(filename,'r', 'utf-8-sig' ) as chat:
        for line in chat:
            if line.find("Messages you send to this chat and calls are now secured with end-to-end encryption. Tap for more info.") >0:
                continue
            m = re.search(r"^"+ date + r",[\s]" + time +"[\s](AM)?(am)?(PM)?(pm)?[\s]", line)
            if m:
                matchedstr = m.group(0)[:]
                message = re.search(r"- .+", line)
                if message:
                    if message.group(0)[:].find("~meta")>0:
                        del chatlog[len(chatlog)-1]
                    item = [matchedstr.split(",")[0], message.group(0).replace("~meta ", "")]
                    chatlog.append(item)
            else:
                chatlog[len(chatlog)-1][1] = chatlog[len(chatlog)-1][1] + ". " + line

    #print chatlog[0][0]
    contents = []
    tempDate = ""
    i = -1
    for msg in chatlog:
        #print contents[0]
        if msg[0] == tempDate:
            contents[i] = contents[i] + "\n" + msg[1][msg[1].find(': ')+2:]
        else:
            i=i+1
            tempDate = msg[0]
            contents.append(msg[1][msg[1].find(': ')+2:])
    return contents #Each element has a date and one day of messages separated by linefeeds

def main():
    if len(sys.argv) <= 1:
        print """
        Usage: python getChat.py <chat corpus>
        """
        return

    content = '\n\n'.join(getChat(sys.argv[1])[:])
    print content
if __name__ == '__main__':
    
    main()
    