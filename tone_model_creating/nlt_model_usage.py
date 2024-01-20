import pickle
import re
import string

from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
from nltk.tag import pos_tag


def remove_noise(tweet_tokens, stop_words=()):
    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens, lang='rus'):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|' \
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', token)
        token = re.sub("(@[A-Za-z0-9_]+)", "", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens


def get_tone(texts):
    stop_words = stopwords.words('russian')
    path = open('tone_model_creating/my_classifier.pickle', 'rb')
    loaded_classifier = pickle.load(path)
    path.close()
    ress = []
    for text in texts:
        cleared_tokens = remove_noise(word_tokenize(text[1]))
        ress.append([text[0], loaded_classifier.classify(dict([token, True] for token in cleared_tokens))])

    return ress

if __name__ == "__main__":
    classifier = NaiveBayesClassifier
    f = open('my_classifier.pickle', 'rb')
    classifier = pickle.load(f)
    f.close()
    test = ""
    while test != "end":
        test = input("enter text:\n")
        print(get_tone(test))
