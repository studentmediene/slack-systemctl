# Slack systemd Control
Control a unit file from Slack

## Usage

### Setup

1. Run `git clone URL`.
2. Run `cd FOLDER`.
1. Run `make setup` and follow the prompts.
2. Run `sudo make deploy`.
3. Run `sudo systemctl start slack-systemctl` to start the program
   (it should start automatically on startup).

### Slack-usage

You use a special keyword to communicate with slack-systemctl regarding
a specific unit. That is, one keyword per unit. Write `KEYWORD help` for
a usage description.

Note that the reply from the slackbot will be posted to a specific channel,
no matter where the original message was sent. The reason for this is to
ensure that no one turns off a service in secret.

## Development

### Overview

![Overview of the application structure](overview.png)

### Quick explaination

The application is split into two parts: one which interfaces with Slack and runs as a non-privileged user, and one
which interfaces with the first part and runs as a privileged user. This seperation means that even if the first part
is compromised, the attacker has not gained root access to the server.

Both parts check whether the given action is allowed, by reading the configuration files, even though only the second part
needs to do this check. The reason for doing the check twice is that there is no reason to invoke the second part if the action 
is not allowed, and you must check at the second part in order to have function level access control.

The second part is not run as a service; rather, a unique user is set up for this task only. You can log in as this user on ssh, but ssh is set up so that you'll just execute a command when logging in (no login shell). That command is the second part of the application. That user is allowed to run commands as sudo, and can therefore run the `systemctl` command needed to perform the action requested by Slack.
