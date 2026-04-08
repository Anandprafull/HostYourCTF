
## What is HostYourCTF?

It is a Capture The Flag framework based on CTFd focusing on ease of use and customizability. It comes with everything you need to run a CTF and it's easy to customize with plugins and themes.

## Features

- Create your own challenges, categories, hints, and flags from the Admin Interface
  - Dynamic Scoring Challenges
  - Unlockable challenge support
  - Challenge plugin architecture to create your own custom challenges
  - Static & Regex based flags
    - Custom flag plugins
  - Unlockable hints
  - File uploads to the server or an Amazon S3-compatible backend
  - Limit challenge attempts & hide challenges
  - Automatic bruteforce protection
- Individual and Team based competitions
  - Have users play on their own or form teams to play together
- Scoreboard with automatic tie resolution
  - Hide Scores from the public
  - Freeze Scores at a specific time
- Scoregraphs comparing the top 10 teams and team progress graphs
- Markdown content management system
- SMTP + Mailgun email support
  - Email confirmation support
  - Forgot password support
- Automatic competition starting and ending
- Team management, hiding, and banning
- Importing and Exporting of CTF data for archival

## Install

1. Install dependencies: `pip install -r requirements.txt`
   1. You can also use the `prepare.sh` script to install system dependencies using apt.
2. Modify [HostYourCTF/config.ini](https://github.com/Anandprafulll/HostYourCTF/blob/master/CTFd/config.ini) to your liking.
3. Use `python serve.py` or `flask run` in a terminal to drop into debug mode.

You can use the auto-generated Docker images with the following command:

`docker run -p 8000:8000 -it ctfd/ctfd`

Or you can use Docker Compose with the following command from the source repository:

`docker compose up`

## Credits

- CTFd

az container create --resource-group ctfd-test-rg --name ctfd-test --image prafullanand/ctfd:latest --ports 80 --dns-name-label ctfdtest$RANDOM --location centralindia

az group create --name ctfd-test-rg --location centralindia

<!-- az container create --resource-group ctfd-test-rg --name ctfd-test --image prafullanand/ctfd:latest --ports 80 --dns-name-label ctfdtest$RANDOM --location centralindia --os-type Linux --cpu 1 --memory 1.5 -->

az container create --resource-group ctfd-test-rg --name ctfd-test --image prafullanand/ctfd:latest --ports 8000 --dns-name-label ctfdtest$RANDOM --location centralindia --os-type Linux --cpu 1 --memory 1.5

az container show --resource-group ctfd-test-rg --name ctfd-test --query ipAddress.fqdn -o tsv

Here’s how you can manage your Azure Container Instance (ACI) deployment:

**1. Change CPU or Memory:**
You cannot resize an existing container group. You must delete and recreate it with new values:
```sh
az container delete --resource-group ctfd-test-rg --name ctfd-test --yes
az container create --resource-group ctfd-test-rg --name ctfd-test --image prafullanand/ctfd:latest --ports 8000 --dns-name-label ctfdtest$RANDOM --location centralindia --os-type Linux --cpu <new_cpu> --memory <new_memory>
```
Replace `<new_cpu>` and `<new_memory>` with your desired values.

**2. Pause/Stop the Deployment:**
ACI does not support pausing or stopping containers. You must delete the container to stop billing:
```sh
az container delete --resource-group ctfd-test-rg --name ctfd-test --yes
```
To “pause,” delete it and recreate later.

**3. Restart the Container:**
You can restart a running container group:
```sh
az container restart --resource-group ctfd-test-rg --name ctfd-test
```

**4. View Logs:**
```sh
az container logs --resource-group ctfd-test-rg --name ctfd-test
```

**5. Check Status:**
```sh
az container show --resource-group ctfd-test-rg --name ctfd-test --query instanceView.state
```

sed -i 's|CTFd_URL = ".*"|CTFd_URL = "http://<your-public-azure-url>:8000/"|' import_challenges.py
sed -i 's|ADMIN_TOKEN = ".*"|ADMIN_TOKEN = "ctfd_NEW_TOKEN"|' import_challenges.py