
import streamlit as st
import pandas as pd
import random
import gspread
import string


SAMPLE_SIZE = 10


def init(ws_name):
    if 'column_map' not in st.session_state:
        column_map = {'A': 'username', 'B': 'gold_cluster', 'C': 'marked',
                      'D': 'is_correct', 'E': 'confidence', 'F': 'intruder_iloc'}
        for i in range(SAMPLE_SIZE-1):
            index_letter = i + 6
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
    results = {"gold_cluster": int(st.session_state.current_cluster)}
    marked = []
    for iloc in st.session_state.ilocs:
        answer_iloc = st.session_state[str(iloc)]
        if answer_iloc:
            marked.append(str(iloc))
    if len(marked) == 0:
        st.error("You must mark at least one option")
        return
    st.session_state.i += 1
    correct = str(st.session_state.intruder_index) in marked
    confidence = 1/len(marked)
    for i, iloc in enumerate(st.session_state.indices_cluster):
        results[f"orig_cluster_{i}"] = int(iloc)
    results["intruder_iloc"] = int(st.session_state.intruder_index)
    results["is_correct"] = correct
    results["confidence"] = confidence
    results["username"] = st.session_state.username

    next_row_ind = len(st.session_state.ws.col_values(1)) + 1
    column_map = st.session_state.column_map
    results["marked"] = ",".join(marked)

    for letter in column_map:
        print(letter)
        if column_map[letter] in results:
            print(column_map[letter])
            st.session_state.ws.update(letter + str(next_row_ind), results[column_map[letter]])
    st.session_state.update_iteration = True


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
        st.session_state.clusters = clusters
        st.session_state.group_by_cluster = st.session_state.df.groupby("community").groups
        st.session_state.i = 0
        st.session_state.update_iteration = True

    clusters = st.session_state.clusters
    if st.session_state.update_iteration:
        st.session_state.update_iteration = False
        st.session_state.current_cluster = random.choice(clusters)
        random_cluster = random.choice([c for c in clusters if c != st.session_state.current_cluster])
        df_cluster = st.session_state.df.loc[st.session_state.group_by_cluster[st.session_state.current_cluster]]
        from_cluster = random.sample(list(df_cluster.index),
                                     k=min(len(df_cluster), SAMPLE_SIZE-1))
        st.session_state.indices_cluster = from_cluster
        # sentences = df_cluster.loc[from_cluster]["title_text"].tolist()
        assert len(df_cluster.loc[from_cluster]["community"].unique()) == 1
        df_random = st.session_state.df.loc[st.session_state.group_by_cluster[random_cluster]]
        st.session_state.intruder_index = random.choice(df_random.index)
        ilocs = from_cluster + [st.session_state.intruder_index]
        # sentences.append(df_random.loc[st.session_state.intruder_index]["title_text"])
        random.shuffle(ilocs)
        st.session_state.ilocs = ilocs

    st.progress(value=st.session_state.i+1)

    st.write("WHICH SENTENCE DOES NOT BELONG TO THE CLUSTER?\n\n"
             "if you are not sure, you can choose more than one option")
    # st.session_state.ilocs = {}
    for iloc in st.session_state.ilocs:
        sentence = st.session_state.df.iloc[iloc]["title_text"]
        # st.session_state.ilocs[iloc] = sentence
        st.checkbox(sentence, value=False, key=iloc)

    st.button(label="submit", on_click=register_results)


# def get_iloc(sentence):
#     if sentence == st.session_state.df.iloc[st.session_state.intruder_index][
#         "title_text"]:
#         return st.session_state.intruder_index
#     else:
#         for index in st.session_state.indices_cluster:
#             if sentence == st.session_state.df.iloc[index]["title_text"]:
#                 return index


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

