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

