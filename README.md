# Couch Deploy
A tiny app that will pull and redeploy your docker containers when a GitHub webhook is received. You just have to push an update to your repository.

# Requirements
## Structure
To use this application you need the following structure of your docker compose files.
- A GitHub repository where you store all docker compose files in one folder per application.
- The docker compose files have to be named like this: `docker-compose.yml`.

## Technical Requirements
- python >= 3.11
- pip
- flask >= 2.3.3
- gunicorn >= 21.2.0

I recommend running this application behind a reverse proxy.

## Configuration
`config.json` holds the config that's required to run the app. Here's an example.
```
{
    "path": "3fc9b689459d738f8c88a3a48aa9e33542016b7a4052e001aaa536fca74813cb",
    "webhook_secret": "40e27b64010c2f41685a04e25ba1c621aeb6b0d03e933c72f6be68de07ccebe6",
    "local_path": "/home/johndoe",
    "folders_to_trigger_on": ["paperless-ngx", "bookstack", "miniflux"]
}
```
- `path` - This is the path that's used in the url. It can be anything you like.
- `webhook_secret` - The webhook secret provided by GitHub when you configure a webhook.
- `local_path` - The path where the folder of the repo is located.
- `folders_to_trigger_on` - A list of folders that the script will act on. Maybe you don't run all your containers at the same server.

# Install
I will assume you have the Technical Requirements installed.

```
# Clone this repository.
git clone

# Configure a GitHub webhook if you haven't already.

# Configure config.json with your editor of choice. See documentation above.
nano config.json

# Choose your port and start the application.
gunicorn -w 1 -b 0.0.0.0:<PORT_NUMBER> app:app
```