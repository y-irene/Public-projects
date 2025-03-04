from task1_metrics import mean_average_precision, mean_ndcg
import spacy
from string import punctuation
import time
from collections import Counter
import csv
import re
import matplotlib.pyplot as plt
import numpy as np
from unidecode import unidecode
from spacy.lang.en import stop_words
from nltk.stem.snowball import SnowballStemmer
from functools import partial
import pandas as pd
from collections import defaultdict
import concurrent.futures
import json
from math import log10, log
import os


# Initialise global tokenizer
tokenizer = spacy.load("en_core_web_sm")
#Initialise global stemmer
stemmer = SnowballStemmer(language='english')


'''
Coursework 1, Task 1 (text preprocessing and vocabulary)
    - text preprocessing function
    - function that returns the vocabulary of a passage, used in the next tasks
'''
def preprocess_passage(passage):
    # Unidecode
    new_passage = unidecode(passage)
    # Lowercase everything
    new_passage = new_passage.lower().strip()
    # Unify punctuation
    new_passage = re.sub(r"’|‘", "'", new_passage)
    new_passage = re.sub(r"‟|“|ʺ|„|”", '"', new_passage)
    # Remove dots from abbreviations
    new_passage = re.sub(r"\b(?:[a-z]\.)+\b", lambda m: m.group().replace('.', ''), new_passage)
    return new_passage


def get_passage_vocabulary(remove_stopwords, passage):
    # Clean passage
    new_passage = preprocess_passage(passage)
    # Tokenize
    global tokenizer
    tokens = list(tokenizer(new_passage))
    # Get lemmas of tokens
    tokens = [token.lemma_.lower().strip(punctuation) for token in tokens if str(token) != "" and not str(token).isdigit()]
    new_tokens = [split_token 
                  for t in tokens 
                  for split_token in list(filter(lambda x: x != None and x != "", re.split("!|\"|\#|\$|%|\&|'|\(|\)|\*|\+|,|\-|\.|/|:|;|<|=|>|\?|@|\[|\\\\|\]|\^|_|`|\{|\||\}|\~| |\n", t))) 
                  if not split_token.isdigit()]
    if remove_stopwords:
        new_tokens = [stemmer.stem(token) for token in new_tokens if token not in stop_words.STOP_WORDS]
    else:
        new_tokens = [stemmer.stem(token) for token in new_tokens]
    return new_tokens


'''
Coursework 1, Task 2 (inverted index)
    - function that computes the inverted index of a passage
    - function that computes the inverted index of the entire collection
      (validation.tsv in this coursework)
'''
def get_passage_inverted_index(remove_stop_words, passage_info):
     # Get passage information
     passage_id = passage_info[0]
     passage = passage_info[1]
     # Get passage vocabulary (from Task 1) and term frequency
     passage_voc = dict(Counter(get_passage_vocabulary(remove_stop_words, passage)))
     # Get passage inverted index
     inv_idx_entry = {term : {passage_id : passage_voc[term]} for term in passage_voc}
     return inv_idx_entry


def get_inverted_index():
    passages_df = pd.read_csv('./validation_data.tsv', sep='\t')
    passages_df.drop(columns=['qid', 'queries', 'relevancy'], inplace=True)
    passages_df.drop_duplicates(inplace=True)
    passages_info = passages_df.values.tolist()

    print('Data read')

    # Remove stopwords
    remove_stop_words = True

    # Get inverted index for each passage
    start_time = time.time()
    get_passage_inverted_index_partial = partial(get_passage_inverted_index, remove_stop_words)
    with concurrent.futures.ProcessPoolExecutor(max_workers=12) as executor:
        pc_inv_idx = executor.map(get_passage_inverted_index_partial, passages_info)
    task_completion_time = time.time() - start_time
    print("All inverted index tasks done in %s seconds" % (task_completion_time))

    # Combine results from all passages
    start_time = time.time()
    pc_inv_idx = list(pc_inv_idx)
    inverted_index = defaultdict(dict)
    for doc in pc_inv_idx:
        for term in doc:
            inverted_index[term].update(doc[term])

    # Store inverted index in json file
    if remove_stop_words:
        with open("task1_inverted_index_no_stopwords.json", "w") as f:
            json.dump(inverted_index, f, indent=4)
    else:
        with open("task1_inverted_index.json", "w") as f:
            json.dump(inverted_index, f, indent=4)

    task_completion_time = time.time() - start_time
    print("Results combined and saved in %s seconds" % (task_completion_time))


'''
Coursework 1, Task 3 (BM25)
'''
def get_candidates_scores_bm25(inverted_index, transposed_inverted_index, avg_dl, N, remove_stopwords, query):
    # BM25 parameters
    k1 = 1.2
    k2 = 100
    b = 0.75
    
    # Query information
    qid = query[0]
    query_text = query[1]
    candidate_passages = query[2]

    # Tokenise queries and get term frequencies
    query_term_frequency = dict(Counter(get_passage_vocabulary(remove_stopwords, query_text)))

    # Compute BM25 parameters
    R = len(candidate_passages)
    ri_query = {term: len(set([int(pid) for pid in list(inverted_index.get(term, {}).keys())]).intersection(set(candidate_passages)))
                for term in query_term_frequency}
    ni_query = {term: len(inverted_index.get(term, {}))
                for term in query_term_frequency}
    
    scores = {}
    for pid in candidate_passages:
        # Get passage length
        passage_term_frequency = transposed_inverted_index[pid]
        dl = sum(list(passage_term_frequency.values()))

        # Get BM25 score
        K = k1 * ((1 - b) + b * dl / avg_dl)
        score = 0
        for term in query_term_frequency:
            ni = ni_query[term]
            qfi = query_term_frequency[term]
            ri = ri_query[term]
            fi = passage_term_frequency.get(term, 0)
            score += (log(((ri + 0.5) / (R - ri + 0.5)) / ((ni - ri + 0.5) / (N - ni - R + ri + 0.5))) 
                      * (((k1 + 1) * fi) / (K + fi)) 
                      * (((k2 + 1) * qfi) / (k2 + qfi)))
        scores[pid] = score
    
    scores = {k: v for k, v in sorted(scores.items(), key = lambda item: item[1], reverse=True)}
    scores = list(scores.items())
    scores = [[qid] + list(tup) for tup in scores]
    print(f'{qid} done!')
    return scores


def bm25(queries, inverted_index, no_passages, transposed_inverted_index, remove_stopwords):
    # Get BM25 parameters
    N = no_passages
    avg_dl = sum([sum(list(transposed_inverted_index[pid].values())) for pid in transposed_inverted_index]) / no_passages
    
    # Get results for each query in parallel
    start_time = time.time()
    queries_list = queries.values.tolist()
    partial_bm25 = partial(get_candidates_scores_bm25, inverted_index, transposed_inverted_index, avg_dl, N, remove_stopwords)
    with concurrent.futures.ProcessPoolExecutor(max_workers=12) as executor:
            bm25_results = executor.map(partial_bm25, queries_list)
    
    task_completion_time = time.time() - start_time
    print("BM25: All tasks done in %s seconds" % (task_completion_time))

    # Save results in bm25.csv
    bm25_results = [result_df_entry for query_lvl_entries in bm25_results for result_df_entry in query_lvl_entries]
    bm25_df = pd.DataFrame(bm25_results, columns = ['qid', 'pid', 'score'])
    bm25_df.to_csv('bm25.csv', sep=',', index=False, header=False)


def get_bm25_scores():
    # Get passages
    candidate_passages_df = pd.read_csv('./validation_data.tsv', sep='\t')
    passages = candidate_passages_df.drop(columns=['qid', 'queries', 'relevancy'])
    passages.drop_duplicates(inplace=True)
    no_passages = len(passages)

    # Get queries and their candidates
    queries = pd.read_csv('./validation_data.tsv', sep='\t')
    queries = queries.drop(columns=['pid', 'passage', 'relevancy'])
    queries.drop_duplicates(inplace=True)
    query_passage_mapping = candidate_passages_df.drop(columns=['queries', 'passage', 'relevancy'])
    query_passage_mapping = query_passage_mapping.groupby('qid')['pid'].apply(list)
    queries['candidates'] = query_passage_mapping[queries['qid']].values

    # Read inverted index computed in Task 2
    remove_stopwords = True
    if remove_stopwords:
        with open('task1_inverted_index_no_stopwords.json') as inverted_index_json:
            inverted_index = json.load(inverted_index_json)
    else:
        with open('task1_inverted_index.json') as inverted_index_json:
            inverted_index = json.load(inverted_index_json)
    
    # Transpose inverted index
    transposed_inverted_index = defaultdict(dict)
    for term in inverted_index:
        for pid in inverted_index[term]:
            transposed_inverted_index[int(pid)].update({term : inverted_index[term][pid]})

    # Apply bm25
    bm25(queries, inverted_index, no_passages, transposed_inverted_index, remove_stopwords)


if __name__ == '__main__':
    # Compute the inverted index needed for BM25
    inv_idx_path = 'task1_inverted_index_no_stopwords.json'
    if not os.path.exists(inv_idx_path):
        print('Computing the inverted index...')
        get_inverted_index()

    # Get BM25 scores
    bm25_path = 'bm25.csv'
    if not os.path.exists(bm25_path):
        print('\nComputing the BM25 scores...')
        get_bm25_scores()

    # Compute BM25 performance
    validation_data = pd.read_csv('./validation_data.tsv', sep='\t')
    bm25_ranking = pd.read_csv('./bm25.csv', sep=',', header=None, names=['qid', 'pid', 'score'])
    ranking = pd.merge(bm25_ranking, validation_data, how='left', on=['qid', 'pid']).drop(columns=['queries', 'passage'])
    map = mean_average_precision(ranking)
    mndcg = mean_ndcg(ranking)

    # Print performance
    print('\nPerformance of the BM25 algorithm')
    print(f'Mean AP: {map}')
    print(f'Mean NDCG: {mndcg}')