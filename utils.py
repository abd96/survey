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


def getMetaData():
    """ getMetaData returns title and description of all broadcasts in the database as pandas dataframe
    :returns: pandas DataFrame containing title and description  columns from metadata.csv

    """
    metadata = pd.read_csv('metadata.csv')
    metadata = metadata.iloc[:, [2, 7]]
    metadata.columns = ['title', 'description']
    return metadata
