import fasttext
import fasttext.util
from icu_tokenizer import Tokenizer, Normalizer
from string import punctuation
from unidecode import unidecode
import re
from tqdm.auto import tqdm
import numpy as np
import pandas as pd
from spacy.lang.en import stop_words


embedding_vector_size = 100
normalizer = Normalizer(lang='en', norm_puncts=True)
tokenizer = Tokenizer(lang='en')
ft = fasttext.load_model('cc.en.300.bin')
fasttext.util.reduce_model(ft, embedding_vector_size)
ft.get_dimension()


def get_tokenized_text(passage):
    # Unidecode
    new_passage = unidecode(passage)
    # Lowercase everything
    new_passage = new_passage.lower().strip()
    # Remove dots from abbreviations
    new_passage = re.sub(r"\b(?:[a-z]\.)+\b", lambda m: m.group().replace('.', ''), new_passage)
    # Normalize text
    global normalizer
    new_passage = normalizer.normalize(new_passage)
    # Tokenize text
    global tokenizer
    tokens = tokenizer.tokenize(new_passage)
    # Remove only punctuation tokens and stop words
    tokens = [token for token in tokens if (not all(char in punctuation for char in token)) and (token not in stop_words.STOP_WORDS)]
    return tokens


def get_passage_embedding_representation(passage):
    # Get tokens
    tokens = get_tokenized_text(passage)
    # Get embeddings for each word
    global ft
    word_embeddings = np.array([ft.get_word_vector(token) for token in tokens])
    # Get passage representation by averaging all words
    passage_embedding = np.average(word_embeddings, axis=0)
    return passage_embedding


def covert_data_to_np(data, labels=True):
    num_samples = data.shape[0]
    X = []
    data_list = data.values.tolist()
    for row in tqdm(data_list):
        query = row[2]
        passage = row[3]
        query_embedding = get_passage_embedding_representation(query)
        passage_embedding = get_passage_embedding_representation(passage)
        querry_passage_sample = np.concatenate((query_embedding, passage_embedding), axis=0)
        X.append(querry_passage_sample)
    X = np.array(X)
    if labels:
        y = data['relevancy'].to_numpy().reshape((num_samples, 1))
        data = np.concatenate((X, y), axis = 1)
    else:
        data = X
    return data


if __name__ == '__main__':
    # Get embeddings representation for the training data
    print('Computing embeddings for training data...')
    data = pd.read_csv('train_data_sample.tsv', sep='\t')
    embeddings_data = covert_data_to_np(data)
    with open(f'T2_train_data_no_stopwords_{embedding_vector_size}.npy', 'wb') as f:
        np.save(f, embeddings_data)
    print('Done!\n')

    # Get embeddings representation for the validation data
    print('Computing embeddings for validation data...')
    data = pd.read_csv('validation_data.tsv', sep='\t')
    embeddings_data = covert_data_to_np(data)
    with open(f'T2_validation_data_no_stopwords_{embedding_vector_size}.npy', 'wb') as f:
        np.save(f, embeddings_data)
    print('Done!\n')

    # Get embeddings representation for the test data
    print('Computing embeddings for test data...')
    data = pd.read_csv('candidate_passages_top1000.tsv', sep='\t', header=None)
    test_embeddings_data = covert_data_to_np(data, labels=False)
    with open(f'T2_test_data_no_stopwords_{embedding_vector_size}.npy', 'wb') as f:
        np.save(f, test_embeddings_data)
    print('Done!')