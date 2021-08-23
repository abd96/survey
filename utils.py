import re
import json
import yaml
import pandas as pd
from scipy import spatial
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import GermanStemmer
from dateutil.parser import parse
from spacy.lang.de import German

german_stopwords = stopwords.words('german')

german_stopwords.append('...')
gstemmer = GermanStemmer()


def readConfig(configPath):
    """ reads the config yaml file and returns vars as python dictionary

    :configPath: path to config file
    :returns: python dictionary containing data and vars from the config file.

    """
    with open(configPath) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def saveJSON(path, data):
    """TODO: Docstring for saveJSON.

    :path: TODO
    :returns: TODO

    """
    with open(path, 'w+', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)


def loadJSON(path):
    """TODO: Docstring for loadJSON.

    :path: TODO
    :returns: TODO

    """
    with open(path) as f:
        data = json.load(f)
    return data


def is_date(string, fuzzy=False):
    """
    from:
    https://stackoverflow.com/questions/25341945/check-if-string-has-date-any-format

    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def preprocess(body, path=''):
    """TODO: Docstring for preprocess.

    :body: TODO
    :path: TODO
    :returns: TODO

    """
    # Remove sentences between (..)
    body = re.sub('\(([^0-9]+)\)', '', body)

    # Remove sentences between Tages like <FONT COLOR ... >
    body = re.sub('<.*?>', '', body)

    # Remove sentences between *..* such as * Musik *
    body = re.sub('\*([^0-9]+)\*', '', body)

    body = body.replace('\n', '')

    # tokenize
    body = word_tokenize(body)

    # stemming
    body = [gstemmer.stem(token) for token in body]

    # lowercase
    body = [token.lower().replace("'", '').replace('untertitel', '')
            for token in body]

    # remove stopwords
    body = [token for token in body if token not in german_stopwords and len(
        token) > 3]  # remove stopwords

    # remove all numbers that are not year
    # TODO if it is a date string (using datetime )
    # then save only year.
    body = [token for token in body if (
        token.isdecimal() and len(token) == 4) or (not token.isdecimal())]

    body = [token.split('.')[-1] for token in body if (token.replace(
        '.', '').isdecimal() and token.count('.') in [2, 3])
        or (not token.isdecimal())]

    return body


def preprocess_bert_sliding_window(body, maximum_length, path=''):
    """TODO: Docstring for preprocess_bert_sliding_window.

    :arg1: TODO
    :returns: TODO

    """
    start_index = 0
    end_index = maximum_length

    # Remove sentences between (..)
    body = re.sub('\(([^0-9]+)\)', '', body)

    # Remove sentences between Tages like <FONT COLOR ... >
    body = re.sub('<.*?>', '', body)

    # Remove sentences between *..* such as * Musik *
    body = re.sub('\*([^0-9]+)\*', '', body)

    # tokenize
    tokens = word_tokenize(body)
    body_sents = []

    maximum_body_size = len(tokens)
    while start_index <= maximum_body_size:
        if end_index >= maximum_body_size:
            end_index = maximum_body_size - 1
        sent_tokens = tokens[start_index:end_index]
        body_sent = ' '.join(sent_tokens)
        body_sents.append(body_sent)
        start_index += int(maximum_length/2)
        end_index += int(maximum_length/2)

    for body_sent in body_sents:

        # tokenize
        body_sent = word_tokenize(body_sent)

        # remove all numbers that are not year
        body_sent = [token for token in body_sent if (
            token.isdecimal() and len(token) == 4) or (not token.isdecimal())]

        # y.m.d -> y
        body_sent = [token.split('.')[-1] for token in body_sent if (token.replace(
            '.', '').isdecimal() and token.count('.') in [2, 3])
            or (not token.isdecimal())]

        # rejoin
        body_sent = ' '.join(body_sent)
    return body_sents


def preprocess_bert(body, path=''):
    """TODO: Docstring for preprocess.

    :body: TODO
    :path: TODO
    :returns: TODO

    """

    # Remove sentences between (..)
    body = re.sub('\(([^0-9]+)\)', '', body)

    # Remove sentences between Tages like <FONT COLOR ... >
    body = re.sub('<.*?>', '', body)

    # Remove sentences between *..* such as * Musik *
    body = re.sub('\*([^0-9]+)\*', '', body)

    # Spacy sentence splitting
    nlp = German()
    nlp.add_pipe('sentencizer')
    body = nlp(body)
    body = [sent.text for sent in body.sents]

    for body_sent in body:

        # tokenize
        body_sent = word_tokenize(body_sent)

        # remove all numbers that are not year
        body_sent = [token for token in body_sent if (
            token.isdecimal() and len(token) == 4) or (not token.isdecimal())]

        # y.m.d -> y
        body_sent = [token.split('.')[-1] for token in body_sent if (token.replace(
            '.', '').isdecimal() and token.count('.') in [2, 3])
            or (not token.isdecimal())]

        # rejoin
        body_sent = ' '.join(body_sent)

    return body


def sim(vec1, vec2):
    """TODO: Docstring for sim.

    :vec1: TODO
    :vec2: TODO
    :returns: TODO

    """

    return 1 - spatial.distance.cosine(vec1, vec2)


def getTitle(path):
    """ Returns the title and the body of the broadcast file.
    Title is the first line and body is all the text
    after that title

    :path: file to open and get data (title, body) from
    :returns: (title:str, body:str)

    """
    with open(path) as f:
        lines = f.readlines()
    lines = list(filter(lambda x: x != '\n', lines))
    title = lines[0]
    body = lines[1:]
    return title.replace('\n', ''), ''.join(body)


def getMetaData():
    """ getMetaData returns title and description of all broadcasts in the database as pandas dataframe
    :returns: pandas DataFrame containing title and description  columns from metadata.csv

    """
    metadata = pd.read_csv('metadata.csv')
    metadata = metadata.iloc[:, [2, 7]]
    metadata.columns = ['title', 'description']
    return metadata
