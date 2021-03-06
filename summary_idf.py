# coding=UTF-8
from __future__ import division
import sys
import math
import numpy
from nltk.tokenize import word_tokenize
import codecs
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

        # We normalize the result by the average number of words
        return len(s1.intersection(s2)) / ((len(s1) + len(s2)) / 2)
    
    #Calculate tf*idf for all tokens
    def tfidf(self, sentences):
        words = {}
        for s in sentences:
            alreadycounted = False
            for t in word_tokenize(s):
                if alreadycounted == False:
                    if t in words:
                        words[t] = [words[t][0]+1, words[t][1]+1]
                    else:
                        words[t] = [1, 1]
                else:
                    words[t] = [words[t][0]+1, words[t][1]]
        for w in words:
            #print "tf*idf = " + str(words[w][0]) + "*" + str(len(sentences)/words[w][1])
            words[w] = (words[w][0]) * (len(sentences)/words[w][1])
        return words #dictionary of all tokens containing a tf*idf value


    # Format a sentence - remove all non-alphbetic chars from the sentence
    # We'll use the formatted sentence as a key in our sentences dictionary
    def format_sentence(self, sentence):
        sentence = re.sub(r'\W+', '', sentence)
        return sentence

    # Convert the content into a dictionary <K, V>
    # k = The formatted sentence
    # V = The rank of the sentence
    def get_sentences_ranks(self, content):

        # Split the content into sentences
        sentences = self.split_content_to_sentences(content)
        
        tokens_ranked = self.tfidf(sentences)
        median = numpy.median(numpy.fromiter(iter(tokens_ranked.values()), dtype=numpy.uint32))
        maximum = max(numpy.fromiter(iter(tokens_ranked.values()), dtype=numpy.uint32))
        topics=[]
        for token in tokens_ranked:
            if tokens_ranked[token] >= median:
                topics.append(token)
            #print tokens_ranked[token]
        topics=set(topics)
        #print "Topics: " + ", ".join(topics)
        #sys.exit()

        # Calculate the intersection of every sentence with the topic set
        n = len(sentences)
        values = [0 for x in xrange(n)]
        for i in range(0, n):
            values[i] = set(word_tokenize(sentences[i].lower())).intersection(topics)

        # Build the sentences dictionary
        # The score of a sentences is the sum of all its intersection
        sentences_dic = {}
        for i in range(0, n):
            sentences_dic[self.format_sentence(sentences[i])] = values[i]
        return sentences_dic

    
    # Return the best sentence in a paragraph
    def get_best_sentence(self, paragraph, sentences_dic):

        # Split the paragraph into sentences
        sentences = self.split_content_to_sentences(paragraph)

        # Ignore short paragraphs
        if len(sentences) < 2:
            return ""

        # Get the best sentence according to the sentences dictionary
        best_sentence = ""
        max_value = 0
        for s in sentences:
            strip_s = self.format_sentence(s)
            if strip_s:
                if sentences_dic[strip_s] > max_value and len(s)>20:
                    max_value = sentences_dic[strip_s]
                    best_sentence = s

        return best_sentence

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
    with codecs.open(filename,'r', 'utf-8-sig' ) as chat:
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

    # Build the summary with the sentences dictionary
    summary = st.get_summary(content, sentences_dic)

    # Print the summary
    print summary

    # Print the ratio between the summary length and the original length
    print ""
    print "Original Length %s" % len(content)
    print "Summary Length %s" % len(summary)
    print "Summary Ratio: %s" % (100 - (100 * (len(summary) / len(content))))


if __name__ == '__main__':
    main()
