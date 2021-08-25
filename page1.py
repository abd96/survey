import streamlit as st
from utils import *
import random
from streamlit.report_thread import get_report_ctx
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import firestore
import outro

from streamlit.script_runner import RerunException
from google.api_core.exceptions import NotFound


def update_selection(k):
    """TODO: Docstring for update_selection.: returns: TODO

    """

    st.session_state.current_selections[k] = not st.session_state.current_selections[k]


def connect_firebase():
    """TODO: Docstring for connect_firebase.
    :returns: TODO

    """
    firebase_config = {
            'apiKey': st.secrets['apiKey'],
            'authDomain': st.secrets['authDomain'],
            'projectId': st.secrets['projectId'],
            'storageBucket': st.secrets['storageBucket'],
            'messagingSenderId': st.secrets['messagingSenderId'],
            'appId': st.secrets['appId'],
            'databaseURL': st.secrets['databaseURL']

            }
    cred = credentials.Certificate({
            'type': st.secrets['type'],
            'project_id': st.secrets['project_id'],
            'private_key_id': st.secrets['private_key_id'],
            'private_key': st.secrets['private_key'],
            'client_email': st.secrets['client_email'],
            'client_id': st.secrets['client_id'],
            'auth_uri': st.secrets['auth_uri'],
            'token_uri': st.secrets['token_uri'],
            'auth_provider_x509_cert_url': st.secrets['auth_provider_x509_cert_url'],
            'client_x509_cert_url': st.secrets['client_x509_cert_url']
            })

    default_app = None
    if not firebase_admin._apps:
        default_app = firebase_admin.initialize_app(
            cred, {'databaseURL': firebase_config['databaseURL']})
        st.session_state.firebase_app_exists = True
    else:
        default_app = firebase_admin.get_app()

    return firestore.client()


def get_session_id():
    """TODO: Docstring for get_session_id.
    :returns: TODO

    """
    ctx = get_report_ctx()
    return ctx.session_id


def cache_data():
    key_title = loadJSON('key_title.json')
    recs = loadJSON('all_methods_recs.json')
    return recs, key_title


@st.cache(allow_output_mutation=True, show_spinner=False)
def loading_data(random_index):
    all_methods = ['ARD', 'lucene', 'doc2vec_standard',
                   'bert_sw_cls_sum', 'tfidf', 'fasttext', 'lda_100_sym']
    method_recs, key_title = cache_data()

    #random_index = random.randint(0, len(method_recs['ARD']))
    st.session_state.ids.append(random_index)
    random_key = list(method_recs['ARD'].keys())[random_index]

    metadata = getMetaData()

    query_title = key_title[random_key]
    query_description = metadata.loc[metadata.title == query_title, 'description'].tolist()[
        0]

    recs = {}
    for k, v in method_recs.items():
        if k in all_methods:
            recs[k] = dict(list(method_recs[k][random_key].items())[1:6])
    return query_title, query_description, random_key, recs


def save_selections(k):
    """TODO: Docstring for save_selections.
    :returns: TODO

    """

    st.caching.clear_cache()
    db = connect_firebase()
    ref = db.collection('survey_data').document(get_session_id())
    entry = {
        k: st.session_state.current_selections
    }
    try:

        ref.update(entry)
    except NotFound as _:
        ref.set(entry)
    st.session_state.current_selections = {}


def close():
    """TODO: Docstring for close.
    :returns: TODO

    """

    st.session_state.end = True
    # SAVE CURRENT DATA FIRST
    st.caching.clear_cache()
    st.session_state.current_selections = {}
    try:
        raise RerunException(st.script_request_queue.RerunData(None))
    finally:
        st.session_state.outro = True


def reload():
    """TODO: Docstring for reload.
    :returns: TODO

    """
    st.caching.clear_cache()
    st.session_state.iscache = False
    st.session_state.current_selections = {}

    raise RerunException(st.script_request_queue.RerunData(None))


def show():
    """TODO: Docstring for show.: returns: TODO

    """
    if 'current_selections' not in st.session_state:
        st.session_state.current_selections = {}
    if 'end' not in st.session_state:
        st.session_state.end = False
    if 'outro' not in st.session_state:
        st.session_state.outro = False
    if 'ids' not in st.session_state:
        st.session_state.ids = []
    if 'iscache' not in st.session_state:
        st.session_state.iscache = True
    if 'random_index' not in st.session_state:
        st.session_state.random_index = -1

    if st.session_state.outro:
        outro.show()
    if st.session_state.iscache:
        choices = list(range(0, 300))
        st.session_state.random_index = random.choice(
            [x for x in choices if x not in st.session_state.ids])
        st.session_state.iscache = False
    else:
        random_index = st.session_state.random_index

    query_title, query_description, query_key, recs = loading_data(st.session_state.random_index)

    if isinstance(query_description, float):
        query_description = 'Nicht Verfügbar'
    if not st.session_state.end:
        st.title(str(query_title) + "\n" + str(query_description))
        st.write('`Welche der folgenden Sendungen passen zu diesem Thema ?`')

    cols = st.columns([4, 5, 4])
    i = 0
    for method_name, method_topn in recs.items():
        for k, v in method_topn.items():
            title = v['title']
            description = v['description']
            if isinstance(description, float):
                description = 'Nicht Verfügbar'
            try:
                if not st.session_state.end:
                    checked = cols[i].checkbox(label=str(title), help=str(
                        description), key=k, on_change=update_selection, args=(k, ))
                    i += 1
                    if i == 3:
                        i = 0
                    st.session_state.current_selections[k] = checked
            except st.errors.DuplicateWidgetID as e:
                pass

    col4, col5, col6 = st.columns([3, 2, 3])
    col4, col5, col6 = st.columns([3, 2, 3])
    col4, col5, col6 = st.columns([3, 2, 3])
    col4, col5, col6 = st.columns([3, 2, 3])

    if not st.session_state.end:

        if col4.button('Auswahl bestätigen und neue Sendung anzeigen'):
            save_selections(query_key)
            reload()

        if col4.button('Auswahl bestätigen und beenden'):
            # TODO
            save_selections(query_key)
            close()
