
import numpy as np
import streamlit as st
import pandas as pd
import random
import gspread
import string


SAMPLE_SIZE = 10


def init(ws_name):
    if 'column_map' not in st.session_state:
        column_map = {'A': 'username', 'B': 'gold_cluster', 'C': 'answer_iloc',
                      'D': 'is_correct', 'E': 'intruder_iloc'}
        for i in range(SAMPLE_SIZE-1):
            index_letter = i + 5
            letter = string.ascii_uppercase[index_letter]
            column_map[letter] = f"orig_cluster_{i}"
        st.session_state['column_map'] = column_map

    column_map = st.session_state['column_map']
    if "ws" not in st.session_state:
        gc = gspread.service_account("credentials.json")
        sh = gc.open("intruder-cluster")
        st.session_state.ws = sh.worksheet(ws_name)
        st.session_state.first_row_index = len(st.session_state.ws.col_values(1)) + 1
        for column in column_map:
            st.session_state.ws.update(column + str(st.session_state.first_row_index),
                                       column_map[column])
        st.session_state.i = 0
        st.session_state.cur_page = 0


def register_results():
    st.session_state.i += 1
    results = {"gold_cluster": int(st.session_state.current_cluster)}
    answer = st.session_state.radio
    correct = st.session_state.radio == st.session_state.df.loc[st.session_state.intruder_index]["title_text"]
    for i, iloc in enumerate(st.session_state.indices_cluster):
        results[f"orig_cluster_{i}"] = int(iloc)
        if st.session_state.df.loc[iloc]["title_text"] == answer:
            results["answer_iloc"] = int(iloc)
    results["intruder_iloc"] = int(st.session_state.intruder_index)
    results["is_correct"] = correct
    if correct:
        results["answer_iloc"] = results["intruder_iloc"]
    results["username"] = st.session_state.username

    next_row_ind = len(st.session_state.ws.col_values(1)) + 1
    column_map = st.session_state.column_map
    for letter in column_map:
        st.session_state.ws.update(letter + str(next_row_ind), results[column_map[letter]])


def main(csv_path):
    # Page title and description
    st.header("Clustering Evaluation - Identify The Intruder")

    if 'df' not in st.session_state:
        st.session_state['df'] = pd.read_csv(csv_path)

    if 'clusters' not in st.session_state:
        clusters = set(st.session_state.df["community"].unique())
        if -1 in clusters:
            clusters.remove(-1)
        clusters = sorted(list(clusters))
        random.shuffle(clusters)
        st.session_state.clusters = clusters
        st.session_state.group_by_cluster = st.session_state.df.groupby("community").groups
        st.session_state.i = 0
        st.session_state.current_cluster = None

    clusters = st.session_state.clusters
    if st.session_state.i == 0 or st.session_state.current_cluster != st.session_state.clusters[st.session_state.i]:
        st.session_state.current_cluster = clusters[st.session_state.i]
        random_cluster = random.choice([c for c in clusters if c != st.session_state.current_cluster])
        df_cluster = st.session_state.df.loc[st.session_state.group_by_cluster[st.session_state.current_cluster]]
        from_cluster = random.sample(list(df_cluster.index), k=SAMPLE_SIZE-1)
        st.session_state.indices_cluster = from_cluster
        sentences = df_cluster.loc[from_cluster]["title_text"].tolist()
        assert len(df_cluster.loc[from_cluster]["community"].unique()) == 1
        df_random = st.session_state.df.loc[st.session_state.group_by_cluster[random_cluster]]
        st.session_state.intruder_index = random.choice(df_random.index)
        sentences.append(df_random.loc[st.session_state.intruder_index]["title_text"])
        random.shuffle(sentences)
        st.session_state.sentences = sentences

    st.progress(value=st.session_state.i / len(st.session_state.clusters))

    label = "WHICH SENTENCE DOES NOT BELONG TO THE CLUSTER?"
    st.radio(label, [label] + st.session_state.sentences, key="radio",
             on_change=register_results, label_visibility="hidden")


def hello_page():
    st.header("Clustering Evaluation - Identify The Intruder")
    st.markdown('Hello! Please enter your username')
    st.text_input('Username', key='username_box')
    st.button('Next', key='next_button0', on_click=record_name)


def record_name():
    if len(st.session_state.username_box) == 0:
        st.error('You must enter a valid username')
    else:
        st.session_state.username = st.session_state.username_box
        next_page()


def next_page():
    st.session_state.cur_page += 1

