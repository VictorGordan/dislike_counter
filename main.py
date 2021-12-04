import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.auth.transport.requests



def main():
    youtube = authentificate_user()

    playlist = uploads_playlist_id(youtube)
    videos = playlist_videos_ids(youtube, playlist)

    print(videos)


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

    return videos

def uploads_playlist_id(youtube):
    """Returns the ID of the 'uploads' playlist of your channel"""
    request = youtube.channels().list(part='contentDetails', mine=True)
    channel = request.execute()
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
                scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
            )

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
