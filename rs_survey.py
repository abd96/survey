import intro
import page1
import streamlit as st


pages = {
    'Intro': intro,
    'Umfrage': page1
}
if 'started' not in st.session_state:
    st.session_state.started = False
#
# st.sidebar.title('Navigation')
#selection = st.sidebar.radio('Seite wechseln zu', list(pages.keys()))
#page = pages[selection]
# page.show()
intro_container = st.empty()
button_container = st.empty()
pages['Intro'].show(intro_container)

if button_container.button('Weiter zur Umfrage'):
    st.session_state.started = True

if st.session_state.started:
    intro_container.empty()
    button_container.empty()
    pages['Umfrage'].show()
