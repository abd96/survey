import streamlit as st


def empty():
    """TODO: Docstring for empty.
    :returns: TODO

    """

    st.title(' ')


def show(container):
    """TODO: Docstring for show.
    :returns: TODO

    """

    with open('intro.md', 'r') as f:
        intro = f.read()
    container.title(intro)
