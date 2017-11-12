# information-retrieval

General:
In this assignment you will implement a basic boolean text retrieval system. This is the simplest of search engines. The document collection you will use is Cran. The boolean model allows users to search for text documents based on boolean queries, e.g. (velocity AND vorticity) OR (velocity AND boundary-layer AND approximation).
Given a boolean query provided in the standard input, your system should return the IDs of all documents that satisfy the query in the standard output as a space-separated list of document IDs.
In order to be able to respond to boolean queries, your system must:
1. Parse and clean-up the document collection, similar to the warm-up exercise.
2. Build an (inverted) index to allow for query evaluation, taking into account both the terms appear- ing in the body as well as in the titles of documents. Your inverted index should also include term and document frequencies, in the form {term: [df, {doc id: tf}]}. df is the number of documents term appears in, while tf is the number of times term appears in document with doc id.
3. Parse, pre-process (exactly as the documents) and evaluate queries.

Deliverable:
A single Python program, named boolret.py, with a main function, so as to be executable from a terminal, with the following I/O specification.
Input: A boolean query given on the standard input. Each line should represent logical conjunction (AND) between terms, while multiple lines should represent logical disjunction (OR) between line expressions. E.g., the input:
alpha beta
gamma delta epsilon
should represent the query (alpha AND beta) OR (gamma AND delta AND epsilon).
Output: A list of space-separated document IDs (integer numbers) satisfying the query, ordered by documentID. If you implement ranked retrieval (see below) rank the document ID in inverse order of score.


The Cranfield Collection
The Cranfield experimental collection can be downloaded at http://ir.dcs.gla.ac.uk/resources/test_collections/cran/ and extract it somewhere in your home folder. For this exercise you will only need to use the text collection file cran.all.1400 – ignore the rest. This file contains 1400 documents and it is structured as follows:
.I 21
.T
on heat transfer in slip flow .
.A
stephen h. maslen
.B
lewis flight propulsion laboratory, naca, cleveland, ohio
.W
on heat transfer in slip flow .
a number of authors have considered the effect of slip on the heat
transfer and skin friction in a laminar boundary layer over a flat plate .


Lines beginning with a . are used to delimit sections of interest. For each document in the file, .I is followed by the document ID, .T is followed by the title, while .W is followed by the text body. The body of each document is delimited by the next line starting with .I. You do not need to be concerned with the other delimiters.
In this exercise you first need to extract document IDs, titles and text bodies and keep associations between them.
