import spacy
import concurrent.futures
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


def get_vocabulary_and_term_freq(filename, remove_stopwords):
    start_time = time.time()
    task_completion_time = 0
    with open(filename, "r") as collection:
        pc_lines = collection.readlines()

        partial_get_passage_vocabulary = partial(get_passage_vocabulary, remove_stopwords)
        with concurrent.futures.ProcessPoolExecutor(max_workers=12) as executor:
            pc_vocabularies = executor.map(partial_get_passage_vocabulary, pc_lines)

        task_completion_time = time.time() - start_time
        print("All tasks done in %s seconds" % (task_completion_time))

        pc_vocabularies = list(pc_vocabularies)
        vocabulary = [term for pc_vocab in pc_vocabularies for term in pc_vocab]
        vocabulary = Counter(vocabulary)

        with open('./vocabulary.csv','w') as vocabulary_f:
            writer=csv.writer(vocabulary_f)
            writer.writerows(sorted(vocabulary.items()))

        return vocabulary


def plot_figs(vocabulary, filename1, filename2):
    t = time.time()
    # Get normalised term frequencies
    term_frequencies = list(vocabulary.values())
    term_frequencies.sort(reverse=True)
    term_frequencies = np.array(term_frequencies)
    term_frequencies = term_frequencies / term_frequencies.sum()
    
    # Get term ranks array
    no_terms = len(term_frequencies)
    term_ranks = np.arange(1, no_terms + 1)

    # Get harmonic number
    h_number = (1 / term_ranks).sum()

    # Get Zipf's law
    zipf_law = 1 / (h_number * term_ranks)

    print("Plots computations done in", time.time() - t)

    # Plot Fig 1
    plt.plot(term_ranks, term_frequencies, label='Data', color='black')
    plt.plot(term_ranks, zipf_law, label="Zipf's law", color='blue', linestyle="dashed")
    plt.legend()
    plt.xlabel("Term frequency ranking")
    plt.ylabel("Term prob. of occurence")
    plt.savefig(filename1)
    plt.clf()

    # Plot Fig 2
    plt.xlabel("Term frequency ranking (log)")
    plt.ylabel("Term prob. of occurence (log)")
    plt.yscale('log')
    plt.xscale('log')
    plt.plot(term_ranks, term_frequencies, label='Data', color='black')
    plt.plot(term_ranks, zipf_law, label="Zipf's law", color='blue', linestyle="dashed")
    plt.legend()
    plt.savefig(filename2)
    plt.clf()


# Initialise global tokenizer
tokenizer = spacy.load("en_core_web_sm")
#Initialise global stemmer
stemmer = SnowballStemmer(language='english')


if __name__ == '__main__':
    vocabulary = get_vocabulary_and_term_freq('./passage-collection.txt', remove_stopwords=False)
    print("Vocabulary has %s terms." % (len(vocabulary)))
    plot_figs(vocabulary, "fig1.svg", "fig2.svg")
