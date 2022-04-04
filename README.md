# Usage Tutorial

First make sure to add: client_secrets.json in your working directory
.It should look something like this
```json
{
    "installed":
    {
        "client_id":"FILL OUT",
        "project_id":"FILL OUT",
        "auth_uri":"https://accounts.google.com/o/oauth2/auth",
        "token_uri":"https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
        "client_secret":"FILL OUT",
        "redirect_uris":["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
    }
}
```

Simply run the "main.py" file. A new tab should then open in your browser asking you for access to your YouTube channel. You need to accept all the stuff it asks you for. Then the script will automatically add the like/dislike stats to the description of all your video. Enjoy :)
