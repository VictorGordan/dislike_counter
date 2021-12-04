import os
import pickle

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import google.auth.transport.requests

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def main():
    youtube = authentificate_user()

    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        mine=True
    )
    response = request.execute()

    print(response)



def authentificate_user():
    # # Disable OAuthlib's HTTPS verification when running locally.
    # # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    credentials = ''

    # Authentification code from https://gist.github.com/CoreyMSchafer/ea5e3129b81f47c7c38eb9c2e6ddcad7
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
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                scopes=[
                    'https://www.googleapis.com/auth/youtube.readonly'
                ]
            )

            flow.run_local_server(port=8080, prompt='consent',
                                  authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)

    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)


if __name__ == "__main__":
    main()
