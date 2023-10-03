import streamlit as st
import pandas as pd


def change_difficulty():
    st.session_state['csv_path'] = f"eliyas_intruder_test_{st.session_state['difficulty']}.csv"
    st.session_state['df'] = pd.read_csv(st.session_state['csv_path'])
    st.session_state.i = 0
    st.session_state.update_iteration = True


def next_sample():

    st.info(f"correct answer was {st.session_state.current_row['title_intruder']}")
    st.session_state.i += 1
    st.session_state.update_iteration = True


def main():
    # Page title and description
    st.header("Clustering Evaluation - Identify The Intruder")

    st.selectbox("difficulty", ["easy", "hard"], key="difficulty", on_change=change_difficulty)

    if 'df' not in st.session_state:
        st.session_state['df'] = pd.read_csv(f"eliyas_intruder_test_{st.session_state['difficulty']}.csv")

    if 'i' not in st.session_state:
        st.session_state.i = 0
        st.session_state.update_iteration = True

    if st.session_state.update_iteration:
        st.session_state.update_iteration = False
        st.session_state.current_row = st.session_state.df.iloc[st.session_state.i]

    st.progress(value=st.session_state.i+1)

    st.write("WHICH SENTENCE DOES NOT BELONG TO THE GROUP?\n\n"
             "if you are not sure, you can choose more than one option")

    for index_in_test in range(9):
        sentence = st.session_state.current_row[f"sentence_{index_in_test}_text"]
        # st.session_state.ilocs[iloc] = sentence
        st.checkbox(sentence, value=False, key=f"index_in_test_{index_in_test}")

    st.button(label="submit", on_click=next_sample)


if __name__ == '__main__':
    main()