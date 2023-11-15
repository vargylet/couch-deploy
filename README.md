<div align="center" width="100%">
    <img src="./static/couch-deploy-wide.jpg" width="400" alt="Couch Deploy logo" />
</div>

# Couch Deploy
Push updated docker-compose files to your GitHub repo, and watch as the app automatically redeploys your Docker containers with new versions. All from the couch!

## 📃 Structural Requirements
To use this application you need the following structure of your docker compose files.
- A GitHub repository where you store all docker compose files in one folder per application.
- Docker Compose files must adhere to the naming convention `docker-compose.yml`.

Example structure for repository:
```
<Repository>
|-- <Folder1>
|   |-- docker-compose.yml
|
|-- <Folder2>
|   |-- docker-compose.yml
|
```

## 💾 Technical Requirements
- Python 3.9.2 or later
- [Requirements.txt](requirements.txt)
- Gunicorn (recommended)

I also recommend running this application behind a reverse proxy of your choice.

## ⌨️ App Configuration
Here's an example of what `app_config.yml` could look like. You can use `config/template_app_config.yml` as your own starting point with minimal changes.
```
log_level: INFO              # DEBUG, INFO, WARNING, CRITICAL   
notification_level: SUCCESS  # INFO, SUCCESS, WARNING, FAILURE
path: couch-deploy           # Makes the endpoint available at <DOMAIN>/couch-deploy
webhook_secret: abcd1234     # The secret shared with the GitHub webhook.
local_path: /home/johndoe    # Local path to the repo on server. No trailing slash!
folders_to_trigger_on:
  - paperless-ngx            # Add each container folder you want the service to act on.
  - bookstack
  - miniflux
```

## 📣 Notification Configuration
Notifications are sent using [Apprise](https://github.com/caronc/apprise). You can find all supported platforms and how to configure them [in their repo](https://github.com/caronc/apprise#supported-notifications). Add your config in `config/notification.yml` to get started. See `config/template_notifications.yml` for some examples.

## 🚂 Install
```
# Clone this repository.
git clone

# Checkout the latest version if you want a stable version.
git checkout vX.Y.Z

# Configure a webhook over at GitHub, if you haven't already.

# Copy and update config.template.json with your editor of choice. See documentation above.
cp template_app_config.yml app_config.yml
nano app_config.yml

# Choose your port and start the application.
gunicorn -w 1 -b 0.0.0.0:<PORT_NUMBER> app:app
```

## 💡 Feedback
Please feel free to create an issue if you have feedback or issues.