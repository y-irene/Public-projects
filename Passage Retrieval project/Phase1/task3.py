import json
import pandas as pd
from math import log10, log
from collections import defaultdict
from task1 import get_passage_vocabulary
from collections import Counter
import numpy as np
import time
import concurrent.futures
from functools import partial


def get_candidates_scores_td_idf(passages_tf_idf, IDF, remove_stopwords, query):
    # Query information
    qid = query[0]
    query_text = query[1]
    candidate_passages = query[2]

    # Compute query normalised TF
    query_term_frequency = dict(Counter(get_passage_vocabulary(remove_stopwords, query_text)))
    query_term_frequency = {term: query_term_frequency[term] / sum(query_term_frequency.values())
                            for term in query_term_frequency}
    
    # Compute query TF-IDF
    query_tf_idf = {term: query_term_frequency[term] * IDF[term] 
                    for term in query_term_frequency if term in IDF}

    # Get query terms set
    query_terms = set(query_tf_idf.keys())
    # Get query TF-IDF representation norm
    q_norm = np.linalg.norm(np.array(list(query_tf_idf.values())))

    # Get passage scores
    scores = {}
    for pid in candidate_passages:
        passage_tf_idf = passages_tf_idf[pid]
        # Get passage TF-IDF representation norm
        p_norm = np.linalg.norm(np.array(list(passage_tf_idf.values())))
        # Get common words between query and passage
        common_terms = query_terms.intersection(set(passage_tf_idf.keys()))
        # Get cosine similarity
        q_common_terms = np.array([query_tf_idf[t] for t in common_terms])
        p_common_terms = np.array([passage_tf_idf[t] for t in common_terms])
        scores[pid] = np.dot(q_common_terms, p_common_terms) / (q_norm * p_norm)
    
    # Get 100 most relevant passages
    scores = {k: v for k, v in sorted(scores.items(), key = lambda item: item[1], reverse=True)}
    scores = list(scores.items())[:100]
    scores = [[qid] + list(tup) for tup in scores]
    return scores


def tf_idf_cosine_similarity(queries, inverted_index, no_passages, 
                             transposed_inverted_index, remove_stopwords):
    # Compute IDF
    IDF = {term : log10(no_passages / len(inverted_index[term])) 
           for term in inverted_index}
    
    # Passages normalised TF
    passages_tf = {pid: {term: transposed_inverted_index[pid][term] / sum(transposed_inverted_index[pid].values())
                         for term in transposed_inverted_index[pid]} 
                         for pid in transposed_inverted_index}

    # Passages TF-IDF
    passages_tf_idf = {pid: {term: passages_tf[pid][term] * IDF[term] 
                             for term in passages_tf[pid]} 
                             for pid in passages_tf}
    
    # Get results for each query in parallel
    start_time = time.time()
    queries_list = queries.values.tolist()
    partial_tf_idf_cosine_similarity = partial(get_candidates_scores_td_idf, 
                                               passages_tf_idf, IDF, 
                                               remove_stopwords)
    with concurrent.futures.ProcessPoolExecutor(max_workers=12) as executor:
            tf_idf_cos_sim_results = executor.map(partial_tf_idf_cosine_similarity, 
                                                  queries_list)
    task_completion_time = time.time() - start_time
    print("TF-IDF: All tasks done in %s seconds" % (task_completion_time))

    # Save results in tfidf.csv
    tf_idf_cos_sim_results = [result_df_entry 
                              for query_lvl_entries in tf_idf_cos_sim_results 
                              for result_df_entry in query_lvl_entries]
    tf_idf_cos_sim_df = pd.DataFrame(tf_idf_cos_sim_results, 
                                     columns = ['qid', 'pid', 'score'])
    tf_idf_cos_sim_df.to_csv('tfidf.csv', sep=',', index=False, header=False)


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
    
    # Get 100 most relevant passages
    scores = {k: v for k, v in sorted(scores.items(), key = lambda item: item[1], reverse=True)}
    scores = list(scores.items())[:100]
    scores = [[qid] + list(tup) for tup in scores]
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


if __name__ == '__main__':
    # Get passages
    candidate_passages_df = pd.read_csv('candidate-passages-top1000.tsv', sep='\t', header=None, names=['qid', 'pid', 'query', 'passage'])
    passages = candidate_passages_df.drop(columns=['qid', 'query'])
    passages.drop_duplicates(inplace=True)
    no_passages = len(passages)
    
    # Get queries and their candidates
    queries = pd.read_csv('test-queries.tsv', sep='\t', header=None, names=['qid', 'query'])
    query_passage_mapping = candidate_passages_df.drop(columns=['query', 'passage'])
    query_passage_mapping = query_passage_mapping.groupby('qid')['pid'].apply(list)
    queries['candidates'] = query_passage_mapping[queries['qid']].values

    # Read inverted index computed in Task 2
    remove_stopwords = True
    if remove_stopwords:
        with open('inverted_index_no_stopwords.json') as inverted_index_json:
            inverted_index = json.load(inverted_index_json)
    else:
        with open('inverted_index.json') as inverted_index_json:
            inverted_index = json.load(inverted_index_json)

    # Transpose inverted index
    transposed_inverted_index = defaultdict(dict)
    for term in inverted_index:
        for pid in inverted_index[term]:
            transposed_inverted_index[int(pid)].update({term : inverted_index[term][pid]})

    # Solve task
    tf_idf_cosine_similarity(queries, inverted_index, no_passages, transposed_inverted_index, remove_stopwords)
    bm25(queries, inverted_index, no_passages, transposed_inverted_index, remove_stopwords)
