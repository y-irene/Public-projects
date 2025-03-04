from tqdm import tqdm
import pandas as pd

train_data = pd.read_csv('train_data.tsv', sep='\t')

# Sample subset
keep = 0.1
random_state = 14

# Keep all relevant documents
train_data_sample = train_data[train_data['relevancy'] == 1]

# Get all non relevant entries
train_data_non_relevant = train_data[train_data['relevancy'] == 0]
# Get all query ids with non relevant entries
qids = train_data_non_relevant['qid'].unique().tolist()
# Compute weight for each query
num_entries_per_query = train_data_non_relevant.groupby(by='qid').size()

for qid in tqdm(qids):
    num_select = int(num_entries_per_query[qid] * keep)
    query_entries = train_data_non_relevant[train_data_non_relevant['qid'] == qid]
    query_entries_sampled = query_entries.sample(n= num_select, random_state=random_state)
    train_data_sample = pd.concat([train_data_sample, query_entries_sampled], ignore_index=False)

# Sort sampled data by index
train_data_sample.sort_index(inplace=True)

# Save sampled data
train_data_sample.to_csv("train_data_sample.tsv", index=None, sep='\t')