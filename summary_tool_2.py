# coding=UTF-8
from __future__ import division
import sys
import np_extractor
from nltk.tokenize import word_tokenize
import re
date = r"[0-9][0-9]?/[0-9][0-9]?/[0-9][0-9]?"
time = r"[0-9][0-9]?:[0-9][0-9]?"

class SummaryTool(object):

    # Naive method for splitting a text into sentences
    def split_content_to_sentences(self, content):
        content = content.replace("\n", ". ")
        content = content.lower()
        return content.split(". ")

    # Naive method for splitting a text into paragraphs
    def split_content_to_paragraphs(self, content):
        return content.split("\n\n")

    # Caculate the intersection between 2 sentences
    def sentences_intersection(self, sent1, sent2):

        # split the sentence into words/tokens
        s1 = set(sent1.split(" "))
        s2 = set(sent2.split(" "))

        #Filter unimportant words
        stopWords = ['oh', 'Oh', 'Ohh', 'Haha','Hm', 'Hmm', 'hmm', 'Yo', 'yo', 'Bye', 'bye', 'Hi', 'Hello']
        for w in s1.intersection(stopWords):
            s1.remove(w)
        for w in s2.intersection(stopWords):
            s2.remove(w)

        # If there is not intersection, just return 0
        if (len(s1) + len(s2)) == 0:
            return 0
        print len(s1.intersection(s2)) / len(s1.union(s2))
        # We normalize the result using jaccard index
        return len(s1.intersection(s2)) / len(s1.union(s2))

    # Format a sentence - remove all non-alphbetic chars from the sentence
    # We'll use the formatted sentence as a key in our sentences dictionary
    def format_sentence(self, sentence):
        sentence = re.sub(r'\W+', '', sentence)
        return sentence

    def get_topic_intersection(self, topics, s=""):
        n=0
        for t in topics:
            if s.find(t) >=0 :
                n = n +1
        return n

    
    # Convert the content into a dictionary <K, V>
    # k = The formatted sentence
    # V = The rank of the sentence
    def get_sentences_ranks(self, content):

        # Split the content into sentences
        sentences = self.split_content_to_sentences(content)

        topics=[]
        for s in sentences:
            extractor = np_extractor.NPExtractor(s)
            result = extractor.extract()
            for t in result:
                topics.append(t.lower())
        topics=set(topics)
        #print "Topics: " + ", ".join(topics)

        # Calculate the intersection of every sentence with the topic set
        n = len(sentences)
        values = [0 for x in xrange(n)]
        for i in range(0, n):
            values[i] = self.get_topic_intersection(topics, sentences[i].lower())
            #print values[i]
        

        # Build the sentences dictionary
        # The score of a sentences is the sum of all its intersection
        sentences_dic = {}
        for i in range(0, n):
            sentences_dic[self.format_sentence(sentences[i].lower())] = values[i]
        return sentences_dic
    
    
    # Return the best sentence in a paragraph
    def get_best_sentence(self, paragraph, sentences_dic):

        # Split the paragraph into sentences
        sentences = self.split_content_to_sentences(paragraph)

        # Get the best sentence according to the sentences dictionary
        best_sentence =""
        secondbest = ""
        max_value = 0
        secondmax = 0
        for s in sentences:
            strip_s = self.format_sentence(s.lower())
            if strip_s:
                if sentences_dic[strip_s] > max_value and len(s)>20:
                    secondmax = max_value
                    max_value = sentences_dic[strip_s]
                    secondbest = best_sentence
                    best_sentence = s
        
        return best_sentence + "\n " + secondbest
        #return secondbest

    # Build the summary
    def get_summary(self, content, sentences_dic):

        # Split the content into paragraphs
        paragraphs = self.split_content_to_paragraphs(content)

        # Add the title
        summary = []
        summary.append("")

        # Add the best sentence from each paragraph
        for p in paragraphs:
            sentence = self.get_best_sentence(p, sentences_dic).strip()
            if sentence:
                summary.append(sentence)

        return ("\n").join(summary)


#Parse chat log
def getChat(filename):
    chatlog = []
    with open(filename) as chat:
        for line in chat:
            if line.find("Messages you send to this chat and calls are now secured with end-to-end encryption. Tap for more info.") >0:
                continue
            m = re.search(r"^"+ date + r",[\s]" + time +"[\s](AM)?(am)?(PM)?(pm)?[\s]", line)
            if m:
                matchedstr = m.group(0)[:]
                message = re.search(r"- .+", line)
                if message:
                    item = [matchedstr.split(",")[0], message.group(0)[:]]
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

# Main method, just run "python summary_tool.py"


def main():

    if len(sys.argv) <= 1:
        print """
        Usage: python summary_tool.py <chat corpus>
        """
        return

    content = '\n\n'.join(getChat(sys.argv[1])[:])

    # Create a SummaryTool object
    st = SummaryTool()

    # Build the sentences dictionary
    sentences_dic = st.get_sentences_ranks(content)
    #print sentences_dic
    
    # Build the summary with the sentences dictionary
    summary = st.get_summary(content, sentences_dic)

    # Print the summary
    print summary

    # Print the ratio between the summary length and the original length
    print ""
    print "Original Length %s" % len(content)
    print "Summary Length %s" % len(summary)
    print "Compression: %s" % (100 - (100 * (len(summary) / len(content))))


if __name__ == '__main__':
    main()
