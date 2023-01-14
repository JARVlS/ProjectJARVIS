# https://www.kdnuggets.com/2020/07/spam-filter-python-naive-bayes-scratch.html

# https://scikit-learn.org/stable/supervised_learning.html#supervised-learning
# - naive bayes https://scikit-learn.org/stable/modules/naive_bayes.html
# - neural networks https://scikit-learn.org/stable/modules/neural_networks_supervised.html#classification
# - nearest neighbors https://scikit-learn.org/stable/modules/neighbors.html - https://www.youtube.com/watch?v=FghB26KmQG0&list=PLNmsVeXQZj7qoIUw0MBYQ9qJffZAVdRWC&index=10
# - svm https://scikit-learn.org/stable/modules/svm.html#classification

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from nltk.stem.snowball import GermanStemmer
from nltk.tokenize import word_tokenize
import string
import json

corpus = [
    'Das ist das erste Dokument.',
    'Dieses Dokument ist das zweite Dokument.',
    'Und das ist das dritte.',
    'Ist dies das erste Dokument?',
]

# Corpus einlesen
with open("./json_data/learn_list.json", encoding="utf-8") as f:
    learn_data: dict = json.load(f)

corpus = []
y = []
i = 0
for command, sentences in learn_data.items():
    for sentence in sentences:
        corpus.append(sentence)
        y.append(i)
    i += 1

# unser eigener Tokenizer
# https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string

stemmer = GermanStemmer()

def nltk_tokenizer(sentence: str):
    words = word_tokenize(sentence)
    #return [word for word in words if word not in string.punctuation] - does not make that a big difference
    return [
        stemmer.stem(word) 
        for word in words 
        if word not in string.punctuation
    ]

# print(nltk_tokenizer('Dieses Dokument ist das zweite Dokument.'))

# unser Dokument-zu-Matrix-Transformierer
# https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
# https://de.wikipedia.org/wiki/Tf-idf-Ma%C3%9F

vectorizer = CountVectorizer(
    tokenizer=nltk_tokenizer, # wir nutzen unseren NLTK-Stemmer
    min_df=2, # nur Wörter, die 2x oder öfter vorkommen (damit Rötteln usw entfällt)
    max_df=0.8 # sperre Wörter aus, die in 80% aller Dokumente vorkommen (oder öfter)
)
#vectorizer = TfidfVectorizer(tokenizer=nltk_tokenizer)

X = vectorizer.fit_transform(corpus)
M = X.toarray()
#print(vectorizer.get_feature_names())

from sklearn.naive_bayes import GaussianNB, ComplementNB, MultinomialNB

gnb = GaussianNB()
gnb.fit(M, y)

cnb = ComplementNB()
cnb.fit(M, y)

mnb = MultinomialNB()
mnb.fit(M, y)

T = vectorizer.transform([
    # 'Google bitte nach Zimtsternen',
    # 'Was sagt Wikipedia zu Burg Rötteln',
    # "Gibt es auf Youtube Ergebnisse zu Quantenphysik",
    # "Hallo wie geht es dir heute so",
    # "Google Harmonie",
    # "Hallo Jarvis starte doch bitte eine Suche auf Youtube nach Iron Man",
    "Zeig mir doch mal das Wikipedia Ergebnis zu youtube",
    "Welche Ergebnisse liefert eine Suche auf Youtube nach Grippe",
    "ausschalten"
]).toarray()

# print(T)
# print(vectorizer.inverse_transform(T))
print(list(learn_data.keys())[gnb.predict(T)[2]])
# print(gnb.predict_proba(T))
print(list(learn_data.keys())[cnb.predict(T)[2]])
print(list(learn_data.keys())[mnb.predict(T)[2]])
# print(cnb.predict_proba(T)) # - print probabilities 

# print(vectorizer.get_feature_names())
# print(X.toarray())
# vectorizer2 = CountVectorizer(analyzer='word', ngram_range=(2, 2))
# X2 = vectorizer2.fit_transform(corpus)
# print(vectorizer2.get_feature_names())