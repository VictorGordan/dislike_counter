import os
import pickle
from datetime import datetime

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.auth.transport.requests



def main():
    youtube = authentificate_user()

    playlist = uploads_playlist_id(youtube)
    videos = playlist_videos_ids(youtube, playlist)
    update_ratings(youtube, videos)

def update_ratings(youtube, videos):
    """Updates the ratings of all videos by appending at the beginning of the
    description of each video the like/dislike stats for the video"""
    count = 0
    print('Updating video ratings...')
    for vid in videos:
        request = youtube.videos().list(
            part="snippet, statistics",
            id=vid
        )
        video = request.execute()
        title = video['items'][0]['snippet']['title']
        description = video['items'][0]['snippet']['description']
        likes = int(video['items'][0]['statistics']['likeCount'])
        dislikes = int(video['items'][0]['statistics']['dislikeCount'])

        ratio = int(10 * likes / (likes + dislikes))
        rate_bar = ratio * '🟦' + (10 - ratio) * '🟥' + '\n'
        likes = str(likes) + (7 - len(str(likes))) * ' '
        dislikes = str(dislikes) + (7 - len(str(dislikes))) * ' '
        rate_count = '👍 ' + likes + '👎 ' + dislikes + '\n'
        time = datetime.utcnow().strftime("%b/%d/%Y at %H:%M UTC")
        update = 'Last updated on ' + time

        new_description = ''
        if description[0] != '👍':
            new_description = rate_count + rate_bar + update + '\n\n' + description
        else:
            description = description.split("\n",3)[3]
            new_description = rate_count + rate_bar + update + '\n' + description

        request = youtube.videos().update(
            part="snippet",
            body={
              "id": vid,
              "snippet": {
                "categoryId": 22,
                "description": new_description,
                "title": title
              }
            }
        )
        request.execute()

        count += 1
        done = count / len(videos) * 100
        progress_bar = int(done / 2) * '█' + (50 - int(done / 2)) * '░'
        done_perc = f' {done:.2f}% '
        progress_bar = progress_bar[:21] + done_perc + progress_bar[29:]
        print(progress_bar, end='\r')
    print('Finished updating ratings!                        ')

def pinned_comments_ids(youtube, videos):
    """Returns a list of IDs coresponding to all pinned comments in 'videos'

    Note: if there are no pinned comments then this will retrieve the latest
    comment, so make sure all videos have a pinned comment"""
    comms = []
    print('Retrieving IDs of all pinned comments...')
    for vid in videos:
        request = youtube.commentThreads().list(part='snippet', videoId=vid)
        response = request.execute()
        comms.append(response['items'][0]['snippet']['topLevelComment']['id'])
        
        done = len(comms) / len(videos) * 100
        progress_bar = int(done / 2) * '█' + (50 - int(done / 2)) * '░'
        done_perc = f' {done:.2f}% '
        progress_bar = progress_bar[:21] + done_perc + progress_bar[29:]
        print(progress_bar, end='\r')
    print('Retrieved IDs of all pinned comments...            ')
    return comms

def playlist_videos_ids(youtube, playlistID):
    """Returns a list with the IDs of all the videos present in a playlist which
    is recognized using the playlistID input"""
    videos = []
    nextPage = ''
    while (nextPage != None):
        request = youtube.playlistItems().list(
        part='snippet', 
        playlistId=playlistID,
        maxResults=50,
        pageToken=nextPage)
        ids = request.execute()
        for vid in ids['items']:
            videos.append(vid['snippet']['resourceId']['videoId'])
        nextPage = ids.get('nextPageToken')
    print('Retrieved IDs of all the videos in the "uploads" playlist...')
    return videos

def uploads_playlist_id(youtube):
    """Returns the ID of the 'uploads' playlist of your channel"""
    request = youtube.channels().list(part='contentDetails', mine=True)
    channel = request.execute()
    print('Retrieved ID of "uploads" playlist...')
    return channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def authentificate_user():
    """Takes care of user authentification process"""
    # # Disable OAuthlib's HTTPS verification when running locally.
    # # *DO NOT* leave this option enabled in production.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    api_service_name = 'youtube'
    api_version = 'v3'
    credentials = ''

    # The code below is from
    # https://gist.github.com/CoreyMSchafer/ea5e3129b81f47c7c38eb9c2e6ddcad7
    if os.path.exists('token.pickle'):
        print('Loading Credentials From File...')
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(google.auth.transport.requests.Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                scopes=['https://www.googleapis.com/auth/youtube.force-ssl'])

            flow.run_local_server(port=8080, prompt='consent',
                                  authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)

    return build(api_service_name, api_version, credentials=credentials)


if __name__ == '__main__':
    main()
