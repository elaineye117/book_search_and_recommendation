from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
from rank_bm25 import BM25Okapi
from rank_bm25 import BM25Plus
from rank_bm25 import BM25L
import string
from nltk import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
import math 
from collections import Counter


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/get")
def get_bot_response():
    what_the_user_said = request.args.get('msg')

    # TODO: Design a ranking function that treats what_the_user_said as the
    # query and returns the relevant book to that. Your bot can
    # respond with any relevant response.
    if what_the_user_said in ['hi', 'hello']:
        return 'Hi, you could ask "How to stay in a healthy relationship?", I will return a book for you.'
    elif what_the_user_said in ['bye', 'see you', 'Bye']:
        return "Bye"
    else:
        query_cleaned = clean_query(what_the_user_said)
        # message = calculate_bm25(message_list, query_cleaned)
        # message_query = " ".join(message)
        returned_clean_response = calculate_f2exp(response_list, query_cleaned)
        list_to_str = ' '.join(returned_clean_response)
        df_response = df2.loc[df2['response_cleaned'] == list_to_str]
        bookname = df_response.iloc[0]['book']
        book_summary = df_response.iloc[0]['response']


        if len(what_the_user_said) == 0:
            return('Please enter a valid dream job...')
        elif len(bookname) == 0:
            return "Your dream is too ambitious, I'd recommend that you try to relax..."
        return (f'I recommend you to read "{bookname}", and its one sentence summary is "{book_summary}". What would you next dream be?')
    

def clean_query(s):
    wordnet_lemmatizer = WordNetLemmatizer()
    cleaned = nltk.word_tokenize(s.lower())
    cleaned = [i.strip(string.punctuation) for i in cleaned] 
    cleaned = [wordnet_lemmatizer.lemmatize(i) for i in cleaned]
    cleaned_list = [ i for i in cleaned if i not in set(stopwords.words('english') + [''])]
    query = " ".join(cleaned_list)

    return query

def clean_df(df, column):
    df['response_cleaned'] = df[column].str.lower().replace('[^A-Za-z0-9]+', ' ')
    stop = stopwords.words('english')

    df2 = df.copy()

    df2['response_cleaned'] = df2['response_cleaned'].astype(str)

    df2['response_cleaned'] = df2['response_cleaned'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))
    return df2


# def calculate_bm25(corpus, query):
#     tokenized_corpus = [doc.split(" ") for doc in corpus]
#     bm25 = BM25Plus(tokenized_corpus, k1=1.25,b=0.35,delta=0.5)

#     tokenized_query = query.split(" ")
#     top_results = bm25.get_top_n(tokenized_query, corpus, n=1)
    
#     return top_results

class BM25:
    def __init__(self, corpus, tokenizer=None):
        self.corpus_size = len(corpus)
        self.avgdl = 0
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
        self.tokenizer = tokenizer

        if tokenizer:
            corpus = self._tokenize_corpus(corpus)

        nd = self._initialize(corpus)
        self._calc_idf(nd)

    def _initialize(self, corpus):
        nd = {}  # word -> number of documents with word
        num_doc = 0
        for document in corpus:
            self.doc_len.append(len(document))
            num_doc += len(document)

            frequencies = {}
            for word in document:
                if word not in frequencies:
                    frequencies[word] = 0
                frequencies[word] += 1
            self.doc_freqs.append(frequencies)

            for word, freq in frequencies.items():
                try:
                    nd[word]+=1
                except KeyError:
                    nd[word] = 1

        self.avgdl = num_doc / self.corpus_size
        return nd

    def _tokenize_corpus(self, corpus):
        pool = Pool(cpu_count())
        tokenized_corpus = pool.map(self.tokenizer, corpus)
        return tokenized_corpus

    def _calc_idf(self, nd):
        raise NotImplementedError()

    def get_scores(self, query):
        raise NotImplementedError()

    def get_batch_scores(self, query, doc_ids):
        raise NotImplementedError()

    def get_top_n(self, query, documents, n=5):

        assert self.corpus_size == len(documents), "The documents given don't match the index corpus!"

        scores = self.get_scores(query)
        top_n = np.argsort(scores)[::-1][:n]
        return [documents[i] for i in top_n]


class F2EXP(BM25):
    def __init__(self, corpus, tokenizer=None, k1=1.5, b=0.75, delta=0.5):
        # Algorithm specific parameters
        self.k1 = k1
        self.b = b
        self.delta = delta
        super().__init__(corpus, tokenizer)

    def _calc_idf(self, nd):
        for word, freq in nd.items():
            idf = math.pow((self.corpus_size + 1)/(freq),self.k1)
            self.idf[word] = idf

    def get_scores(self, query):
        score = np.zeros(self.corpus_size)
        doc_len = np.array(self.doc_len)
        qlist = list(query)
        counts = Counter(qlist)
        for q in query:
            q_freq = np.array([(doc.get(q) or 0) for doc in self.doc_freqs])
            ctd = q_freq / (q_freq + 0.5 + 0.5 * doc_len / self.avgdl)
            score += (self.idf.get(q) or 0) * ctd * counts[q]
        return score

    def get_batch_scores(self, query, doc_ids):
        """
        Calculate bm25 scores between query and subset of all docs
        """
        assert all(di < len(self.doc_freqs) for di in doc_ids)
        score = np.zeros(len(doc_ids))
        doc_len = np.array(self.doc_len)[doc_ids]
        qlist = list(query.split(' '))
        counts = Counter(qlist)
        for q in query:
            q_freq = np.array([(self.doc_freqs[di].get(q) or 0) for di in doc_ids])
            ctd = q_freq / (q_freq + 0.5 + 0.5 * doc_len / self.avgdl)
            score += (self.idf.get(q) or 0) * ctd * counts[q]
        return score.tolist()

def calculate_f2exp(corpus, query):
    tokenized_corpus = [doc.split(" ") for doc in corpus]
    bm25 = F2EXP(tokenized_corpus, k1=0.35)

    tokenized_query = query.split(" ")
    top_results = bm25.get_top_n(tokenized_query, corpus, n=1)
    
    return top_results

if __name__ == "__main__":
    #get dataframe
    df = pd.read_table("summary.txt", delimiter=',', index_col=0) 
    # clean response column in df
    df2 = clean_df(df, 'response')
    #clean message column in df
    # df3 = clean_df(df2, 'message')
    # convert response column to list
    response_list = df2['response_cleaned'].tolist()
    # convert message column to list
    # message_list = df3['message'].tolist()

    # IMPLEMENTATION HINT: you probably want to load and cache your conversation
    # database (provided by us) here before the chatbot runs
    
    app.run()
