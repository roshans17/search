import argparse
import string
import math
import sys
from tokenize import Ignore
import xml.etree.ElementTree as et
import re

from math import sqrt
from xml.dom.minidom import Element
from attr import NOTHING
from nltk.corpus import stopwords
from pytest import File
STOP_WORDS = set(stopwords.words('english'))
from nltk.stem import PorterStemmer
nltk_test = PorterStemmer()
from file_io import write_title_file, write_docs_file, write_words_file

class Index:
    def __init__(self, xml: str):
        self.tree = et.parse(xml)
        self.root = self.tree.getroot()
        # titles_dict 
        self.title_dict = {}
        # words_dict
        self.words_dict = {}
        # links_dict (maps all the links that a given document has)
        self.links_dict = {}
        # internal_titles_dict
        self.internal_titles_dict = {}
        # storage_dict_pr for PageRank
        self.storage_dict_pr = {}
        # curr_dict_pr for PageRank
        self.curr_dict_pr = {}
        # stores the value of the maximum word count 
        self.max_word_dict = {}
        # tracks the number of pages
        self.pageTracker = 0

        self.title_parse()
        self.word_parse()
        self.page_rank()

    def title_parse(self):
        """
        Parses through the titles for each respective page and populates the ID as its key and name as its value
        Also populates an internal titles dictionary that will be used in Page Rank to map the title of a document 
        to its respective ID
        :param self
        :return: n/a
        """
        for child in self.root: 
            self.title_dict[int(child.find('id').text.strip())] = child.find('title').text.strip()
            self.internal_titles_dict[child.find('title').text.strip().lower()] = int(child.find('id').text.strip())
            self.pageTracker +=1

    def word_parse(self):
        """ 
        Parses through each document, tokenzises the text, removes whitespace, removes stop and stem words
        and calls a helper function that will deal with links and add the parsed text to the words_dict
        :param self
        :return: n/a
        """
        for child in self.root:
            curr_word_list = self.tokenize(child)
            titleList = self.tokenize_title(child)
            curr_word_list = curr_word_list + titleList
            doc_id = int(child.find('id').text.strip())
            curr_word_list = self.stop_stem(curr_word_list)
            self.link(doc_id, curr_word_list)

    def tokenize(self, child: Element):
        """
        Utilizes regex to tokenize the text
        :param self: an element (child from the XML file)
        :return: tokenized text
        """
        n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        cool_tokens = re.findall(n_regex, child.find('text').text.strip())
        return cool_tokens
    
    def tokenize_title(self, child: Element):
        """
        Utilizes regex to tokenize the title
        :param self: an element (child from the XML file)
        :return: tokenized text 
        """
        n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        cool_tokens = re.findall(n_regex, child.find('title').text.strip())
        return cool_tokens

    def stop_stem(self, curr_word_list: list):
        """
        Removes stop and stem words from the text
        :param self: list of words that need to be cleaned of stop and stem words
        :return: an updated list of strings without stop and stem words
        """
        updated_word_list = []
        for word in curr_word_list:
                lower_case_words = word.lower()
                if lower_case_words not in STOP_WORDS:
                    removed_stem_word = nltk_test.stem(lower_case_words)
                    updated_word_list.append(removed_stem_word)
        return updated_word_list
     
    def link(self, doc_id: int, word_list: list):
        """
        Parses through the links within each document and populates them into both the words 
        dictionary and the links dictionary
        Any text that is not a link will also be stored in the words dictionary
        :param self
        :param doc_id: the ID of the document
        :param word_list: the list of words to be parsed through
        :return: n/a
        """
        self.links_dict[doc_id] = set()
        n_regex = '''[a-z]+[a-z]'''
        link_regex = '''\[\[[^\[]+?\]\]'''
        for word in word_list:
            link = re.match(link_regex, word)
            if link: 
                # accounting for potential pipes in links
                if '|' in link[0]: 
                    split_word_list = word.split('|')
                    link_to_add = split_word_list[0].replace('[[', "")
                    word_to_add = split_word_list[1].replace(']]', "")
                    word_to_add = re.findall(n_regex, word_to_add)
                    word_to_add = self.stop_stem(word_to_add)
                    self.populate_links_dict(doc_id, link_to_add)
                    for word in word_to_add:
                        self.populate_words_dict(doc_id, word)
                else:
                    link = word.replace(']]',"")
                    link_to_add = link.replace('[[', "")
                    self.populate_links_dict(doc_id, link_to_add)
                    word_to_add = re.findall(n_regex, word)
                    word_to_add = self.stop_stem(word_to_add)
                    for word in word_to_add:
                        self.populate_words_dict(doc_id, word)
            # if it is not a link, we will populate to words dictionary but not links dictionary
            else:
                self.populate_words_dict(doc_id, word)
    
    def is_in_corpus(self, link_to_add : string):
        """
        Checks whether a link to be added is in the corpus
        :param self
        :param link_to_add: the link to be added
        :return: a boolean representing whether or not the link is in the corpus
        """
        return link_to_add in self.internal_titles_dict

    def populate_words_dict(self, doc_id: int, word_to_add: string):
        """
        Populates the words dictionary
        :param self
        :param doc_id: the ID of the document
        :param word_to_add: the word to be added
        :return: n/a
        """
        if (word_to_add in self.words_dict):
            try:
                self.words_dict[word_to_add][doc_id] = self.words_dict[word_to_add][doc_id] + 1
            # if the word exists but the document ID is not in the inner dictionary, catch the KeyError that 
            # it throws and make its value 1
            except KeyError:
                self.words_dict[word_to_add][doc_id] = 1
        else: 
            self.words_dict[word_to_add] = {doc_id : 1}
    
    def populate_links_dict(self, doc_id : int, link_to_add : string):
        try:
            self.links_dict[doc_id].add(self.internal_titles_dict[link_to_add])
        except KeyError:
            pass
    
    def sum_of_dicts(self):
        """
        Computes the sum of the dictionaries
        :param self
        :return: the sum of the dictionaries
        """
        total = 0
        for doc_id in self.curr_dict_pr:
            total = total + (self.curr_dict_pr[doc_id] - self.storage_dict_pr[doc_id])**2
        return sqrt(total)
    
    def calculate_weights(self, k: int, j: int):
        """
        Computes the weights of the links between two pages
        :param self
        :param k: a page 
        :param j: a page
        :return: the value of the weight between the pages
        """
        links = self.links_dict[k]
        weights_value = 0
        if links == set() or (len(links) == 1 and k in links):
            if k == j:
                weights_value = .15/self.pageTracker
            else:
                weights_value = (.15/self.pageTracker) + .85/(self.pageTracker-1)
        elif j in links:
                weights_value = (.15/self.pageTracker) + .85/len(links)
        else: 
            weights_value = .15/self.pageTracker
        return weights_value

    def page_rank(self):
        """
        Implements the PageRank algorithm
        :param self
        :return: mapping of document IDs to their page ranks
        """
        for doc_id in self.title_dict:
            self.storage_dict_pr[doc_id] = 0
            self.curr_dict_pr[doc_id] = (1/self.pageTracker)
        while self.sum_of_dicts() > 0.001:
            self.storage_dict_pr = self.curr_dict_pr.copy()
            for j in self.curr_dict_pr:
                self.curr_dict_pr[j] = 0
                for k in self.curr_dict_pr:
                    self.curr_dict_pr[j] = self.curr_dict_pr[j] + self.calculate_weights(k, j) * self.storage_dict_pr[k]
        return self.curr_dict_pr

# writes in the arguments when the file is run
if __name__ == "__main__":
    try:
        ID = Index(sys.argv[1])
        write_title_file(sys.argv[2], ID.title_dict)
        write_docs_file(sys.argv[3], ID.curr_dict_pr)
        write_words_file(sys.argv[4], ID.words_dict)
    except IndexError:
        raise IndexError('Missing file and or too many files! Please try again.')
    except FileNotFoundError:
        raise FileNotFoundError('File Not Found! Please try again.')