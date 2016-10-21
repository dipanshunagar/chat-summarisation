from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

def get_continuous_chunks(text):
     chunked = ne_chunk(pos_tag(word_tokenize(text)), binary=True)
     prev = None
     continuous_chunk = []
     other_chunks = []
     current_chunk = []
     for i in chunked:
             if type(i) == Tree:
                     current_chunk.append(" ".join([token for token, pos in i.leaves()]))
             elif current_chunk:
                     named_entity = " ".join(current_chunk)
                     if named_entity not in continuous_chunk:
                             continuous_chunk.append(named_entity)
                             current_chunk = []
             elif i[1] in ["CD", "NNP", "NNS"] :
                 other_chunks.append(i[0])
             else:
                     continue
             #print i
     return [continuous_chunk, other_chunks]

s = "Haha. But Naveen Sir won't be taking his two classes on Monday. He will be out of station, probably in Mumbai."
print ne_chunk(pos_tag(word_tokenize(s)))


print get_continuous_chunks(s)


"""
s = "Yes. He said that when he came to DE Shaw recruitment process. That, he gonna start from 31st of may!"
#s= "I couldn't find jobs at JP Morgan"
s = "These are three of the biggest problemsWedMeGood facing today's AI"
tokens = nltk.word_tokenize(s)
tagged = nltk.pos_tag(tokens)
ne_tagged = nltk.chunk.ne_chunk(tagged)
print ne_tagged
"""
