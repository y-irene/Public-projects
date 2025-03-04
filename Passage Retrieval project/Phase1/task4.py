import json
import pandas as pd
from math import log
from collections import defaultdict
from task1 import get_passage_vocabulary
from collections import Counter
import time
import concurrent.futures
from functools import partial


def query_likelihood_lidstone_correction(transposed_inverted_index, v_len, epsilon, 
                                         remove_stopwords, query):
    # Get query information
    qid = query[0]
    query_text = query[1]
    candidate_passages = query[2]

    # Get query term frequency
    query_term_frequency = dict(Counter(get_passage_vocabulary(remove_stopwords, query_text)))

    scores = {}
    for pid in candidate_passages:
        passage_model = transposed_inverted_index[pid]
        # Get document length
        d_len = sum(list(passage_model.values()))

        # Compute score
        score = 0
        for q_term in query_term_frequency:
            tf = passage_model.get(q_term, 0)
            score += (query_term_frequency[q_term] * log((tf + epsilon) / (d_len + epsilon * v_len)))
        scores[pid] = score
    
    # Get 100 most relevant passages
    scores = {k: v for k, v in sorted(scores.items(), key = lambda item: item[1], reverse=True)}
    scores = list(scores.items())[:100]
    scores = [[qid] + list(tup) for tup in scores]
    return scores


def query_likelihood_dirichlet_smoothing(transposed_inverted_index, inverted_index, collection_size, miu, remove_stopwords, query):
    # Get query information
    qid = query[0]
    query_text = query[1]
    candidate_passages = query[2]

    # Get query term frequency
    query_term_frequency = dict(Counter(get_passage_vocabulary(remove_stopwords, query_text)))
    # Get query terms frequency in entire corpus
    tfs_w_c = {term: sum(inverted_index.get(term, {}).values())
               for term in query_term_frequency}

    scores = {}
    for pid in candidate_passages:
        passage_model = transposed_inverted_index[pid]
        # Get document length
        N = sum(passage_model.values())
        # Compute coefficients
        coef_1 = N / (N + miu)
        coef_2 = miu / (N + miu)

        # Compute passage score
        score = 0
        for q_term in query_term_frequency:
            # Get query term frequency in document
            tf_w_d = passage_model.get(q_term, 0)
            # Get query term frequency in corpus
            tf_w_c = max(tfs_w_c[q_term], 1)
            score += (query_term_frequency[q_term] * log((coef_1 * (tf_w_d / N)) + (coef_2 * (tf_w_c / collection_size))))
        scores[pid] = score
    
    # Get 100 most relevant passages
    scores = {k: v for k, v in sorted(scores.items(), key = lambda item: item[1], reverse=True)}
    scores = list(scores.items())[:100]
    scores = [[qid] + list(tup) for tup in scores]
    return scores


if __name__ == '__main__':
    candidate_passages_df = pd.read_csv('candidate-passages-top1000.tsv', sep='\t', header=None, names=['qid', 'pid', 'query', 'passage'])
    passages = candidate_passages_df.drop(columns=['qid', 'query'])
    passages.drop_duplicates(inplace=True)
    queries = pd.read_csv('test-queries.tsv', sep='\t', header=None, names=['qid', 'query'])
    query_passage_mapping = candidate_passages_df.drop(columns=['query', 'passage'])
    query_passage_mapping = query_passage_mapping.groupby('qid')['pid'].apply(list)
    queries['candidates'] = query_passage_mapping[queries['qid']].values

    # Read inverted index
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
    
    queries_list = queries.values.tolist()

    # Query likelihood language model with Laplace smoothing
    v_len = len(inverted_index) # Vocabulary length
    start_time = time.time()
    partial_query_likelihood_laplce_smoothing = partial(query_likelihood_lidstone_correction, 
                                                        transposed_inverted_index, v_len, 1, remove_stopwords)
    with concurrent.futures.ProcessPoolExecutor(max_workers=12) as executor:
            laplce_smoothing_results = executor.map(partial_query_likelihood_laplce_smoothing, queries_list)
    
    task_completion_time = time.time() - start_time
    print("Laplace smoothing: All tasks done in %s seconds" % (task_completion_time))

    laplce_smoothing_results = [result_df_entry 
                                for query_lvl_entries in laplce_smoothing_results 
                                for result_df_entry in query_lvl_entries]
    laplce_df = pd.DataFrame(laplce_smoothing_results, columns = ['qid', 'pid', 'score'])
    laplce_df.to_csv('laplace.csv', sep=',', index=False, header=False)

    # Query likelihood language model with Lidstone correction
    start_time = time.time()
    partial_query_likelihood_lidstone_correction = partial(query_likelihood_lidstone_correction, 
                                                            transposed_inverted_index, v_len, 0.1, remove_stopwords)
    with concurrent.futures.ProcessPoolExecutor(max_workers=12) as executor:
            lidstone_correction_results = executor.map(partial_query_likelihood_lidstone_correction, queries_list)
    
    task_completion_time = time.time() - start_time
    print("Lidstone correction: All tasks done in %s seconds" % (task_completion_time))

    lidstone_correction_results = [result_df_entry 
                                    for query_lvl_entries in lidstone_correction_results 
                                    for result_df_entry in query_lvl_entries]
    lidstone_df = pd.DataFrame(lidstone_correction_results, columns = ['qid', 'pid', 'score'])
    lidstone_df.to_csv('lidstone.csv', sep=',', index=False, header=False)

    # Query likelihood language model with Dirichlet smoothing
    collection_size = sum([inverted_index[term][pid] for term in inverted_index for pid in inverted_index[term]])
    start_time = time.time()
    partial_query_likelihood_dirichlet_smoothing = partial(query_likelihood_dirichlet_smoothing, 
                                                           transposed_inverted_index, inverted_index, 
                                                           collection_size, 50, remove_stopwords)
    with concurrent.futures.ProcessPoolExecutor(max_workers=12) as executor:
            dirichlet_smoothing_results = executor.map(partial_query_likelihood_dirichlet_smoothing, queries_list)
    
    task_completion_time = time.time() - start_time
    print("Dirichlet smoothing: All tasks done in %s seconds" % (task_completion_time))

    dirichlet_smoothing_results = [result_df_entry 
                                   for query_lvl_entries in dirichlet_smoothing_results 
                                   for result_df_entry in query_lvl_entries]
    dirichlet_df = pd.DataFrame(dirichlet_smoothing_results, columns = ['qid', 'pid', 'score'])
    dirichlet_df.to_csv('dirichlet.csv', sep=',', index=False, header=False)
    