# import pytest
from pytest import raises
import index

# ------------------------- UNIT TESTS -------------------------------------


# -----Index Tests------
def test_title_dict():
    # testing the length of the dictionary and if the titles are populating correctly
    ID = index.Index('BostonCelticsWiki.xml')
    assert len(ID.title_dict) == 3
    assert ID.title_dict[2] == 'Kyrie Irving'

def test_word_dict():

    # testing to make sure words all convert to lowercase
    ID = index.Index('BostonCelticsWiki.xml')
    word = ID.words_dict.popitem()
    assert word[0].islower() is True

    # testing that words that appear multiple times in the same document are being incremented in that doc_id key
    ID1 = index.Index('BostonCelticsWiki.xml')
    word2 = ID1.words_dict['jayson']
    assert word2[1] > 1

    # testing that words that appear multiple times across different documents are correctly incremented in their respective doc_id keys
    word3 = ID1.words_dict['nba']
    assert word3[1] == 1 and word3[2] == 2

    # testing that normal links (without pipes and meta-pages) populate into the word count 
    word4 = ID1.words_dict['hammer']
    assert word4[1] == 1

    # testing that meta-pages properly populate into the word count and that stemming is occuring 
    word5 = ID1.words_dict['categori']
    word6 = ID1.words_dict['comput']
    word7 = ID1.words_dict['scienc']
    assert word5[1] == 1 and word5[2] == 1 and word6[1] == 1 and word6[2] == 1 and word7[1] == 1 and word7[2] == 1
    
    # testing that links with pipes properly populate into the word count 
    word8 = ID1.words_dict['pipe']
    word9 = ID1.words_dict['kyri']
    assert word8[1] == 1 and word9 == {1:1, 2 : 1}

    # testing that links with pipes and multiple words after the pipe all properly populate into the word count and that stemming is occuring 
    word10 = ID1.words_dict['stemm']
    word11 = ID1.words_dict['nba']
    assert word10 == {2: 1} and word11[2] == 2

    #testing that various stop words are being removed
    assert "is" and "it" and "that" and "of" and "the" not in ID1.words_dict

def test_link_dict():
    # Utilizing Page Rank example 1
    # testing that the length of the inner hashset is of the correct size
    ID = index.Index('BostonCelticsWiki.xml')
    link = ID.links_dict[1]
    assert len(link) == 1

    # testing that if a document does not link to anything, its inner hashset is empty
    link1 = ID.links_dict[2]
    assert len(link1) == 0

    # testing that normal links populate with the word as their link title
    link2 = ID.links_dict[1]
    expected = {2}
    if link2 == expected:
        tracker = True
    assert tracker == True

    # testing that links with pipes populate with the content to the left of the pipe
    link3 = ID.links_dict[3]
    if 1 in link3:
        tracker2 = True
    assert tracker2 == True

    # testing that meta-pages populate with whole link and not only one word
    # utilizing self-created Page Rank example 
    ID1 = index.Index('PageRankOwnExample.xml')
    link4 = ID1.links_dict[4]
    if 1 in link4:
        tracker3 = True
    assert tracker3 == True

def test_calculate_weights():
    # Utilizing on given Page Rank example 1
    # testing that calculated weights value is correct AND that the values will not change as pageRank for-loop runs
    # also tests that docs that don't link to anything are treated as if they link to every doc except for themselves

    ID = index.Index('PageRankExample1.xml')
    assert ID.calculate_weights(1,3) == 0.475

    weights_value=[]
    for i in range(1, 4, 1):
        for j in range(1, 4, 1):
            weights_value.append(ID.calculate_weights(i,j))
    assert 0.049999999999999996 and 0.475 and 0.9 in weights_value    

    #testing that docs that only link to themselves are treated as if they link to every doc except for themselves
    ID1 = index.Index('PageRankExample3.xml')
    weights_value2=[]
    for i in range(1, 4, 1):
        for j in range(1, 4, 1):
            weights_value2.append(ID1.calculate_weights(i,j))
    assert 0.0375 and 0.3208333333333333 in weights_value2    

def test_page_rank():
    #testing the values of pagerank with various wiki files that were either created by us or given to us
    #and that the final values all add up to 1. 

    ID = index.Index('BostonCelticsWiki.xml')
    expected = {1: 0.33333333333333326, 2: 0.43264271886591577, 3: 0.23402394780075067}
    assert expected == ID.curr_dict_pr
    assert 1 - sum(ID.curr_dict_pr.values()) < .001

    ID1 = index.Index('PageRankExample1.xml')
    expected1 = {1: 0.4326427188659158, 2: 0.23402394780075067, 3: 0.33333333333333326}
    assert expected1 == ID1.curr_dict_pr
    assert 1 - sum(ID1.curr_dict_pr.values()) < .001

    ID2 = index.Index('PageRankExample2.xml')
    expected2 = {1: 0.20184346250214996, 2: 0.03749999999999998, 3: 0.37396603749279056, 4: 0.3866905000050588}
    assert expected2 == ID2.curr_dict_pr
    assert 1 - sum(ID2.curr_dict_pr.values()) < .001

    ID3 = index.Index('PageRankExample3.xml')
    expected3 = {1: 0.05242784862611451, 2: 0.05242784862611451, 3: 0.4475721513738852, 4: 0.44757215137388523}
    assert expected3 == ID3.curr_dict_pr
    assert 1 - sum(ID3.curr_dict_pr.values()) < .001

    ID4 = index.Index('PageRankOwnExample.xml')
    expected4 = {1: 0.320011728893252, 2: 0.037499999999999936, 3: 0.3095099695592642, 4: 0.33297830154748215}
    assert expected4 == ID4.curr_dict_pr
    assert 1 - sum(ID4.curr_dict_pr.values()) < .001

# ------------------------- SYSTEMS TESTS -------------------------------------