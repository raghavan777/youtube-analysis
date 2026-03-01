from googleapiclient.discovery import build
import pandas as pd

API_KEY = "AIzaSyCLt6JRkDYwEmsLGEFq0FkaWc-MQonTFvk"

def get_channel_data(CHANNEL_ID):

    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Get channel info
    channel_request = youtube.channels().list(
        part="snippet,statistics",
        id=CHANNEL_ID
    )
    channel_response = channel_request.execute()

    if not channel_response["items"]:
        return None, None

    channel = channel_response['items'][0]

    channel_details = {
        "title": channel['snippet']['title'],
        "subscribers": channel['statistics'].get('subscriberCount', 0),
        "views": channel['statistics'].get('viewCount', 0),
        "videos": channel['statistics'].get('videoCount', 0)
    }

    # Get videos
    videos = []

    search_request = youtube.search().list(
        part="snippet",
        channelId=CHANNEL_ID,
        maxResults=50,
        order="date",
        type="video"
    )

    search_response = search_request.execute()

    for item in search_response['items']:
        videos.append(item['id']['videoId'])

    video_request = youtube.videos().list(
        part="statistics,snippet",
        id=",".join(videos)
    )

    video_response = video_request.execute()

    data = []

    for v in video_response['items']:
        views = int(v['statistics'].get('viewCount',0))
        likes = int(v['statistics'].get('likeCount',0))
        comments = int(v['statistics'].get('commentCount',0))

        engagement = (likes + comments) / views if views>0 else 0

        data.append({
            "title": v['snippet']['title'],
            "publishedAt": v['snippet']['publishedAt'],
            "views": views,
            "likes": likes,
            "comments": comments,
            "engagement": engagement
        })

    df = pd.DataFrame(data)

    return channel_details, df