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
    query_cleaned = clean_query(what_the_user_said)
    # message = calculate_bm25(message_list, query_cleaned)
    # message_query = " ".join(message)
    returned_clean_response = calculate_bm25(response_list, query_cleaned)
    list_to_str = ' '.join(returned_clean_response)
    df_response = df2.loc[df2['response_cleaned'] == list_to_str]
    bookname = df_response.iloc[0]['book']
    book_summary = df_response.iloc[0]['response']


    if len(what_the_user_said) == 0:
        return('Please enter a valid dream job...')
    elif len(bookname) == 0:
        return "Your dream is too ambitious, I'd recommend that you try to relax..."
    return (f'I recommend you to read "{bookname}", and its one sentence summary is "{book_summary}"')
    

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


def calculate_bm25(corpus, query):
    tokenized_corpus = [doc.split(" ") for doc in corpus]
    bm25 = BM25Plus(tokenized_corpus, k1=1.25,b=0.35,delta=0.5)

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
