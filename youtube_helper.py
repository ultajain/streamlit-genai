from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


def extract_transcript_and_thumbnail(video_url):
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            raise ValueError("Video ID not found in the YouTube URL " + video_url)
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        thumbnail = f"http://img.youtube.com/vi/{video_id}/0.jpg"

        return transcript, thumbnail

    except Exception as e:
        raise e


def extract_video_id(youtube_url):
    parsed_url = urlparse(youtube_url)
    # Standard url
    if parsed_url.netloc == 'www.youtube.com' and parsed_url.path == '/watch':
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]
    # shortened youtu.be URL
    elif parsed_url.netloc == 'youtu.be':
        return parsed_url.path.strip('/')
    else:
        return None
