import numpy as np

'''
Average Precision
'''
def average_precision(relevancy):
    n = len(relevancy)
    avg_precision = 0
    for k in range(1, n + 1):
        precision_k = sum(relevancy[:k]) / k
        avg_precision += (precision_k * relevancy[k - 1])
    avg_precision = avg_precision / sum(relevancy)
    return avg_precision

def mean_average_precision(data):
    data_sorted = data.sort_values(by=['qid', 'score'], ascending=[True, False])
    qids = data_sorted['qid'].unique()
    average_precisions = []
    for qid in qids:
        relevancy = data_sorted[data_sorted['qid'] == qid]['relevancy'].tolist()
        average_precisions.append(average_precision(relevancy))
    return np.mean(np.array(average_precisions))

'''
NDCG
'''
def ndcg(relevancy):
    sorted_relevancy = np.sort(relevancy)[::-1]
    ranks = np.array(range(1, len(relevancy) + 1))
    idcg = np.sum(sorted_relevancy / np.log2(ranks + 1))
    dcg = np.sum(relevancy / np.log2(ranks + 1))
    ndcg = dcg / idcg
    return ndcg

def mean_ndcg(data):
    data_sorted = data.sort_values(by=['qid', 'score'], ascending=[True, False])
    qids = data_sorted['qid'].unique()
    ndcgs = []
    for qid in qids:
        relevancy = data_sorted[data_sorted['qid'] == qid]['relevancy'].tolist()
        ndcgs.append(ndcg(relevancy))
    return np.mean(np.array(ndcgs))