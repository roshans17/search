NAMES: ROSHAN SAPKOTA AND ARYAN PATIDAR

KNOWN BUGS: none.

HOW TO INTERACT: 
    
    To run the program, please run the indexer first. In order to run the indexer,
please write this command into your terminal: [python3 index.py <NameOfYourFile.xml> <TitlesFilePath> <DocsFilePath> <WordsFilePath>].
Depending on your xml file size, the indexer will take some time to parse your code. Though, we must admit, our implementation
utilizes great design practices in order to minimize your wait time and subsequently maximizing your user experience. After the indexer 
has ran, please run the querier into your terminal using: [python3 query.py [--pagerank] <titleIndex> <documentIndex> <wordIndex>]. 
After the querier has ran, you will then be able to search. To quit out of the program please type ":quit". 

HOW THE CODE WORKS: 


    INDEX: The indexer will take in various xml files from the wiki file that is passed in by the user. It will then 
parse through xml files and store the title, words, and links from the file into respective dictionaries. This data will then 
be easily accessible to help give the best search results. For example, the program will take the dictionary that 
stores details about links found in the wiki to run the pagerank algorithim. Some of these dictionaries will then be written into a file 
which then will be parsed through by the querier. We utilize many dictionaries in the indexer because we are storing all this data 
to be able to have access to them when the user is running the program. Since dictionaries can access its data in constant time, 
and the fact that we hope to maximize run-time for user experience, this data structure was concluded by us to be the most optimal.  


    QUERY: (ARYAN)




ADDITIONAL FEATURES: We have error handling (need to add more).


TESTING: We split up our testing plan into two distinct categories: unit testing and systems testing. Unit testing mostly consists 
of tests that will ensure that our data is being parsed correctly and that our calculations for pagerank and term relevance are correct.
To do this we utilize wikis that were supplied to us and created by ourselves (BostonCelticsWiki and PageRankOwnExample). Individual comments 
about the purpose of the respective tests are supplied in the testing file, but in an essence, these tests are methodically designed in a way to 
catch edge cases present in wikis: for example we test for cases that look at how links with pipes and meta-titles are populated into links and words
dictionaries, ensure that the sum of the values of pagerank equals 1, examine if stopping and stemming is occuring, and if the weights needed for 
pagerank are consistently the same. 

(ADD ABOUT SYSTEMS TESTING --- ARYAN)