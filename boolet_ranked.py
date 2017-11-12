#!/usr/bin/env python
import sys
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import os.path
import json

CRAN_COLL = '/home/mscuser/Desktop/python_project_1/cran.all.1400'
SYMBOLS = '1234567890!@#$%^&*()[]{};\':".,<>/?`~-=+'
INDEX_FILE = '/home/mscuser/Desktop/python_project_1/index-file.json'

def ext_docs(cran_file=CRAN_COLL):

	"""Parse the document body and title fields of the Cranfield collection.
	Arguments:
		cran_file: (str) the path to the Cranfield collection file
	Return:
		body_kwds, title_kwds: where body_kwds and title_kwds are
		dictionaries of the form {docId: [words]}.
	"""
	id = -1
	t_start = False
	b_start = False
	body_kwds = {}
	title_kwds = {}
	with open(cran_file) as f:
		# read file line by line
		for line in f:
			if line.startswith('.I'):
				id = int(line.split()[1])
				t_start = False
				b_start = False
			if line.startswith('.T'):
				t_start = True;
				line = next(f)
			if line.startswith('.W'):
				b_start = True;
				line = next(f)
			for t in line.split():
				# case of title, fill title_kwds
				if t_start:
					if line.startswith('.A') or line.startswith('.B'):
						t_start = False
						break
					else:
						title_kwds.setdefault(id, []).append(t)
				#case of body, fill body_kwds
				if b_start:
					body_kwds.setdefault(id, []).append(t)
	return title_kwds, body_kwds


def pre_process(lst):

	"""Pre-process the list of words provided.
	Arguments:
		lst-> (list of str) A list of words or terms
	Return:
		a shorter list of pre-processed words
	"""
	# Get list of stop-words and instantiate a stemmer:
	stop_words = set(stopwords.words('english'))
	stemmer = PorterStemmer()
	# Make all lower-case:
	lst = map(lambda x: x.lower(), lst)
	# Remove symbols:
	lst = map(lambda x: x.strip(SYMBOLS), lst)
	lst = [(''.join([c if c not in SYMBOLS else '' for c in x])) for x in lst]
	# Remove words <= 3 characters:
	lst = [x for x in lst if len(x) > 3]
	# Remove stopwords:
	lst = [x for x in lst if x not in stop_words]
	# Stem terms:
	lst = map(lambda x: stemmer.stem(x), lst)
	return lst

def create_inv_index(bodies, titles):

	"""Create a single inverted index for the dictionaries provided. Treat
	all keywords as if they come from the same field. In the inverted index
	retail document and term frequencies per the form below.
	Arguments:
		bodies: A dictionary of the form {doc_id: [terms]} for the terms found
		in the body (.W) of a document
		titles: A dictionary of the form {doc_id: [terms]} for the terms found
		in the title (.T) of a document
	Return:
		index: a dictionary {docId: [df, postings]}, where postings is a
		dictionary {docId: tf}.
		E.g. {'word': [3, {4: 2, 7: 1, 9: 3}]}
				^       ^   ^        ^
				term    df  docid    tf
	"""
	result = {}
	for key in (bodies.viewkeys() | titles.keys()):
		if key in bodies: result.setdefault(key, []).extend(bodies[key])
		if key in titles: result.setdefault(key, []).extend(titles[key])
	index = {}
	for key, value in result.items():
		for string in value:
			index.setdefault(string, []).append(key)
	postings = {}
	for key, value in index.items():
		postings = {x:value.count(x) for x in value}
		index[key] = [len(value), postings]
	return index


def write_inv_index(index, outfile = INDEX_FILE):

	"""Write the given inverted index in a file.
	Arguments:
		index: an inverted index of the form {'term': [df, {doc_id: tf}]}
		outfile: (str) the path to the file to be created
	"""

	with open(outfile, 'w') as file:
		json.dump(index, file)

def load_inv_index(filename = INDEX_FILE):

	"""Load an inverted index from the disk. The index is assumed to be stored
	in a text file.
	Arguments:
		filename: the path of the inverted index file
		Return:
			a dictionary containing all keywords and their posting dictionaries
	"""

	with open(filename) as file:
		data = json.load(file)
	return data

def eval_conj(index, terms):
	"""Evaluate the conjunction given in list of terms. In other words, the
	list of terms represent the query `term1 AND term2 AND ...`
	The documents satisfying this query will have to contain ALL terms.
	Arguments:
		index: an inverted index
		terms: a list of terms of the form [str]
	Return:
		lst: a list of docIds
	"""

	t = ()
	counter = 0
	lst = []
	# in case list of terms has many terms
	if len(terms) > 1:
		# read list term by term
		for i in terms:
			counter += 1
			#for the first time
			if counter == 1:
				if i in index:
					inner_dict = index[i][1]
					# insert into lst all the ids of the word
					for k,v in inner_dict.iteritems():
						lst.append(k)
					counter += 1
			# for every other time
			else:
				if i in index:
					new_list = []
					inner_dict = index[i][1]
					# insert into new_lst all the ids of the word
					for k,v in inner_dict.iteritems():
						new_list.append(k)
					# keep only the same elements of 2 lists
					lst = set(lst) & set(new_list)
		lst = map (int, lst)
	# in case list of terms has only one term
	if len(terms) == 1:
		if terms[0] in index:
			inner_dict = index[terms[0]][1]
			for k,v in inner_dict.iteritems():
				lst.append(k)
				lst = map(int, lst)
	return lst


def eval_disj(list):

	"""Evaluate the conjunction results provided, essentially ORing the
	document IDs they contain. In other words the resulting list will have to
	contain all unique document IDs found in the partial result lists.
	Arguments:
		list: results as they return from `eval_conj()
	Return:
		result: a list of docId
	"""
	result = []
	lst = [i for sub in list for i in sub]
	for i in lst:
		if i not in result:
			result.append(i)
	return result

def main():

	"""Main function create index from a file CRAN_COLL. It exports the index in a file and it load it in data dictionary.
	Parse user queries from stdin where words on each line are ANDed, while whole lines between them are
	ORed. Match the user query to the Cranfield collection. The output is a space-separated list of sorted document IDs.
	"""

	data= {}
	check = True
	result = []
	lst = []
	and_lst = []

	# fills index from body_kwds and title_kwds
	title_kwds, body_kwds = ext_docs(CRAN_COLL)
	for key, value in title_kwds.items():
		title_kwds[key] = pre_process(value)
	for key, value in body_kwds.items():
		body_kwds[key] = pre_process(value)
	index = create_inv_index(body_kwds, title_kwds)

	# check if index_file exists or need to be created
	while check:
		if os.path.exists(INDEX_FILE):
			data = load_inv_index(INDEX_FILE)
			check = False
		else:
			write_inv_index(index, INDEX_FILE)

	# read input and fill a list of lists
	for line in sys.stdin:
		lst.append(line.split())
	# for each sublist, create p_list and give it as an argument to eval_conj
	for sublst in lst:
		p_lst = pre_process(sublst)
		and_lst.append(eval_conj(data, p_lst))
	# we give the result of eval_conj as an input to eval_disj
	result = eval_disj(and_lst)
	#sort IDs
	print sorted(result)

if __name__ == '__main__':
	main()
