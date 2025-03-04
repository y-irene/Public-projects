from task1 import get_passage_vocabulary
import pandas as pd
from collections import Counter, defaultdict
import concurrent.futures
import time
import json
from functools import partial


def get_passage_inverted_index(remove_stop_words, passage_info):
     # Get passage information
     passage_id = passage_info[0]
     passage = passage_info[1]
     # Get passage vocabulary (from Task 1) and term frequency
     passage_voc = dict(Counter(get_passage_vocabulary(remove_stop_words, passage)))
     # Get passage inverted index
     inv_idx_entry = {term : {passage_id : passage_voc[term]} for term in passage_voc}
     return inv_idx_entry


if __name__ == '__main__':
     passages_df = pd.read_csv('candidate-passages-top1000.tsv', sep='\t', header=None, names=['qid', 'pid', 'query', 'passage'])
     passages_df.drop(columns=['qid', 'query'], inplace=True)
     passages_df.drop_duplicates(inplace=True)
     passages_info = passages_df.values.tolist()

     # Remove stopwords
     remove_stop_words = True

     # Get inverted index for each passage
     start_time = time.time()
     get_passage_inverted_index_partial = partial(get_passage_inverted_index, remove_stop_words)
     with concurrent.futures.ProcessPoolExecutor(max_workers=12) as executor:
          pc_inv_idx = executor.map(get_passage_inverted_index_partial, passages_info)
     task_completion_time = time.time() - start_time
     print("All tasks done in %s seconds" % (task_completion_time))
     
     # Combine results from all passages
     start_time = time.time()
     pc_inv_idx = list(pc_inv_idx)
     inverted_index = defaultdict(dict)
     for doc in pc_inv_idx:
          for term in doc:
               inverted_index[term].update(doc[term])

     # Store inverted index in json file
     if remove_stop_words:
          with open("inverted_index_no_stopwords.json", "w") as f:
               json.dump(inverted_index, f, indent=4)
     else:
          with open("inverted_index.json", "w") as f:
               json.dump(inverted_index, f, indent=4)

     task_completion_time = time.time() - start_time
     print("Results combined and saved in %s seconds" % (task_completion_time))

