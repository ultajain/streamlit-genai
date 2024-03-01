from typing import List

import streamlit as st
import google.generativeai as genai
from streamlit.runtime.uploaded_file_manager import UploadedFile

import youtube_helper as yh
from llm_helper import GeminiLLM
import hmac

st.set_page_config(page_title="GenAI Tools", page_icon="🚀")

st.markdown(
    """
    <style>
    div[class^="block-container"] {
        padding-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


class FileData:
    def __init__(self, pdfs):
        self.pdfs = pdfs
        ids = [f.file_id for f in pdfs]
        self.hash = ''.join(ids)
        print("Hash", self.hash)


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    st.subheader("Login with password")
    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

genai.configure(api_key=st.secrets['gemini_api_key'])

prompt = """You are Youtube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within {} words. The transcript is given here :-\n{}"""


@st.cache_data
def extract_yt_transcript(video_url):
    print("Fetching transcript from youtube for url: " + video_url)
    return yh.extract_transcript_and_thumbnail(video_url)


@st.cache_data
def generate_gemini_content(video_url, transcript, length):
    print(f"Summarizing video transcript for url {video_url}, length {length}")
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt.format(length, transcript))
    return response.text


@st.cache_resource(hash_funcs={FileData: lambda x: x.hash})
def load_faq_model(filedata: FileData):
    print(f"Loading pdf doc model")
    faq_model = GeminiLLM(st.secrets['gemini_api_key'])
    faq_model.index_documents(filedata.pdfs)
    return faq_model


tab1, tab2 = st.tabs(["Summarize YT video", "Query PDF files"])

with tab1:
    st.title("Summarize youtube video")

    with st.form("my_form"):
        youtube_link = st.text_input("Enter YouTube Video Link")
        length = st.slider('Number of words in summary', 100, 1000, 250, 50, "%d words", label_visibility='collapsed')
        get_summary = st.form_submit_button('Get Summary')

    if get_summary:
        try:
            transcript, thumbnail = extract_yt_transcript(youtube_link)
            st.image(thumbnail, use_column_width=True)
            summary = generate_gemini_content(youtube_link, transcript, length)
            st.markdown("## Summary")
            st.write(summary)
            with st.expander("See complete transcript"):
                st.write(transcript)
        except Exception as e:
            print("Error while loading youtube summary: {}", e)
            st.error("Unable to fetch data :(")

with tab2:
    st.title("Query uploaded PDF files")

    model = None

    with st.container(border=True):
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit button",
                                    accept_multiple_files=True)
        if st.button("Submit"):
            st.session_state['docs_submitted'] = True

    if 'docs_submitted' in st.session_state and st.session_state['docs_submitted'] and pdf_docs:
        with st.spinner("Processing..."):
            model = load_faq_model(FileData(pdf_docs))
        user_question = st.text_input("Ask a Question from the PDF Files")
        if user_question:
            st.write(model.answer_user_query(user_question))
