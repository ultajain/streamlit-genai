import streamlit as st
import google.generativeai as genai
import youtube_helper as yh
import hmac


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


st.title("Summarize youtube video")
youtube_link = st.text_input("Enter YouTube Video Link")
length = st.slider('Number of words in summary', 100, 1000, 250, 50, "%d words", label_visibility="collapsed")
get_summary = st.button("Get Summary")

if youtube_link and get_summary:
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

