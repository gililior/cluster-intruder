from app import init, hello_page, main
import streamlit as st


if __name__ == '__main__':
    init("10k")
    if st.session_state.cur_page == 0:
        hello_page()
    else:
        main("10k-large.csv")
