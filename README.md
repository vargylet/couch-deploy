# Couch Deploy
A tiny app that will pull and redeploy your docker containers when a GitHub webhook is received. You just have to push an update to your repository and the app does the rest.

# Requirements
## Structure
To use this application you need the following structure of your docker compose files.
- A GitHub repository where you store all docker compose files in one folder per application.
- Docker Compose files must adhere to the naming convention `docker-compose.yml`.

## Technical Requirements
- python >= 3.11
- flask >= 2.3.3
- gunicorn >= 21.2.0

I recommend running this application behind a reverse proxy.

## Configuration
`config.template.json` shows the structure of the config that's required to run the app. Here's an example.
```
{
    "log_level": "INFO",
    "path": "3fc9b689459d738f8c88a3a48aa9e33542016b7a4052e001aaa536fca74813cb",
    "webhook_secret": "40e27b64010c2f41685a04e25ba1c621aeb6b0d03e933c72f6be68de07ccebe6",
    "local_path": "/home/johndoe",
    "folders_to_trigger_on": ["paperless-ngx", "bookstack", "miniflux"]
}
```
- `log_level` - Default is `INFO`. Can be changed to `DEBUG`, `WARNING`, or `CRITICAL`.
- `path` - This is the path that's used in the url. It can be anything you like.
- `webhook_secret` - The webhook secret you choose when configuring the GitHub webhook.
- `local_path` - The path where the folder of the repo is located.
- `folders_to_trigger_on` - A list of the folders that the script will act on.

# Install
I will assume you have the Technical Requirements in place.

```
# Clone this repository.
git clone

# Configure a GitHub webhook if you haven't already.

# Copy and update config.template.json with your editor of choice. See documentation above.
cp config.template.json config.json
nano config.json

# Choose your port and start the application.
gunicorn -w 1 -b 0.0.0.0:<PORT_NUMBER> app:app
```
