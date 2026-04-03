
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


