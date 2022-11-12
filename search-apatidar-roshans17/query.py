import sys
import math

from nltk.stem import PorterStemmer
from file_io import read_title_file, read_docs_file, read_words_file

class Query:
    def __init__(self):
        # maps the document IDs to the document titles
        self.ids_to_titles = {}
        # maps the document IDs to the document Euclidean distances
        self.ids_to_max_euclidean = {}
        # maps the document IDs to the document page ranks
        self.ids_to_page_ranks = {}
        # maps each word to a map of document IDs and document frequencies of that word
        self.words_to_doc_relevance = {}

        # indicator to use PageRank
        self.use_page_rank = False

    def fill_euclidean(self):
        """
        Fills the mapping of the document Euclidean distances
        :param self
        :param results: the list of results
        :return: n/a
        """
        for word in self.words_to_doc_relevance:
            for page_id in self.words_to_doc_relevance[word]:
                if page_id not in self.ids_to_max_euclidean:
                    self.ids_to_max_euclidean[page_id] = 0
                self.ids_to_max_euclidean[page_id] = max(self.ids_to_max_euclidean[page_id], self.words_to_doc_relevance[word][page_id])

    def print_results(self, results: list):
        """
        Prints the results of the search query
        :param self
        :param results: the list of results
        :return: n/a
        """
        for i in range(min(len(results), 10)):
            print(f"{i+1} {self.ids_to_titles[results[i][0]]}")

    def query(self, user_input: str):
        """
        Handles a search query and prints out the results
        :param self
        :param user_input: the search query of the user
        :return: n/a
        """
        sep_words = user_input.split(" ")
        nltk_test = PorterStemmer()
        stemmed_user_input = [nltk_test.stem(w) for w in sep_words]
        results = self.relevance_doc_matcher(stemmed_user_input)
        if self.use_page_rank:
            results = {k: v * self.ids_to_page_ranks[k] for (k, v) in results.items()}
        if len(results) == 0:
            print("no results found")
        else:
            sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
            self.print_results(sorted_results)

    def tf_calculator(self, doc_id: int, count: float):
        """
        Computes the term frequency of a document
        :param self
        :param doc_id: the ID of the document that we are calculating the term frequency of
        :param count: the number of times that the word appears in the document
        :return: term frequency
        """
        most = self.ids_to_max_euclidean[doc_id]
        return count/most

    def idf_calculator(self, pg_count: float):
        """
        Computes the inverse document frequency of a document
        :param self
        :param pg_count: the number of pages that contain the word
        :return: inverse document frequency
        """
        total_pages = len(self.ids_to_titles)
        return math.log(total_pages/pg_count)

    def get_relevance(self, input_word: str):
        """
        Gets the relevance of a given word for all documents in which that word appears
        :param self
        :param input_word: the word in the search query
        :return: a mapping of document IDs to their relevance scores
        """
        products = {}
        doc_frequency = self.words_to_doc_relevance.get(input_word)
        if doc_frequency:
            for id in doc_frequency:
                product = self.tf_calculator(id, doc_frequency[id]) * self.idf_calculator(len(doc_frequency))
                products[id] = product
            return products
        else:
            return {}

    def add_relevance(self, scores: dict, old_scores: dict):
        """
        Adds the relevance scores of each word
        If the word already exists in the mapping, its score is added to the existing score
        :param scores: the updated relevance scores of the word
        :param old_scores: the old relevance scores of the word
        :return: a mapping of document IDs to their updated relevance scores
        """
        for (id_num, score) in scores.items():
            if id_num in old_scores:
                old_scores[id_num] += score
            else:
                old_scores[id_num] = score
        return old_scores

    def relevance_doc_matcher(self, queried_words: list):
        """
        Maps document IDs to their relevance scores using helper functions
        :param self
        :param queried_words: the list of words in the search query
        :return: a mapping of document IDs to their updated relevance scores
        """
        scores = {}
        for word in queried_words:
            word_score = self.get_relevance(word)
            scores = self.add_relevance(word_score, scores)
        return scores

query = Query()

# parses the arguments when the file is run and runs a query REPL of the specified indices
if __name__ == "__main__":
    if len(sys.argv) - 1 == 4 and sys.argv[1] == '--pagerank':
        query.use_page_rank = True
        read_title_file(sys.argv[2], query.ids_to_titles)
        read_docs_file(sys.argv[3], query.ids_to_page_ranks)
        read_words_file(sys.argv[4], query.words_to_doc_relevance)
    if len(sys.argv) - 1 == 3:
        query.use_page_rank = False
        read_title_file(sys.argv[1], query.ids_to_titles)
        read_docs_file(sys.argv[2], query.ids_to_page_ranks)
        read_words_file(sys.argv[3], query.words_to_doc_relevance)
    
    query.fill_euclidean()

    while (True):
        print("search>", end="")
        user_input = input()
        if user_input == ":quit":
            break
        query.query(user_input)