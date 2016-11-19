# slack-systemctl
Control one or multiple SystemD unit files from Slack

This project is affiliated with neither Slack Technologies, Inc. nor the SystemD
project.

Using slack-systemctl, you may restart a service from the comfort of Slack.
It saves you the trouble of logging in through ssh and manually executing a
command, and is especially useful if you don't have a computer handy.

## Features

* Let your team restart or check a service on the go, without having to pull
  out a laptop.
* Relatively easy to set up.
* Can be used with any service in SystemD, old or new.
* Define which services slack-systemctl shall have access to, and what
  it can do with each of them (status, start, stop, restart).
* Uses sudo to limit what can be done, so you don't need to give more
  privileges than necessary.
* Built-in support for help messages, if you don't remember how to use
  a specific unit.

## Usage

### Setup

The bot runs from the host on which the service(s) you want to control, run.
You may run slack-systemctl from multiple computers (with the same user, even),
but all messages will be parsed by all instances, so make sure you pick unique
keywords.

On the host:

1. Run `git clone URL`.
2. Run `cd slack-systemctl`.
3. Run `make setup` and follow the prompts.
4. Run `make sudoers`.
5. Run `sudo visudo` and paste the output of the previous command somewhere in the configuration. Save and close.
6. Run `sudo make deploy`.
7. Run `sudo systemctl start slack-systemctl` to start the program
   (it should start automatically on startup).
8. Make sure you invite the Slack bot user to the channels you want it to participate in.
   You can do so with the `/join` command in Slack.

### Changing the configuration

1. Change the configuration file(s) (not the ones in templates).
2. Update the sudoers file if you changed what units and commands are permitted:
   
   1. Run `make sudoers`.
   2. Run `sudo visudo` and replace the existing section on slack-systemctl with the output of the previous command. Save and close.
3. Restart the application: `sudo systemctl restart slack-systemctl`

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

The application monitors the Slack channels the bot is invited to, and reacts to a keyword. Upon receiving a message with
the keyword, it will try to determine whether it is allowed to perform the action before running 
`sudo --non-interactive systemctl COMMAND UNIT`. However, instead of granting the application full root privileges, the sudoers
file is used to grant the application permission to execute only those commands users are allowed to execute. This means that even
if the application is compromised, it does not grant the attacker access to the entire server.

### Security

The design of slack-systemctl, explained above, means that no matter how vulnerable the slackhq/rtmbot might end up being,
attackers will only gain access to whatever combinations of units and commands that you, as
the system administrator, has given to the dedicated slack-systemctl user in the sudoers configuration.
However, if malicious code is among the allowed services, an attacker may use slack-systemctl to start up
and run that service. This means that you must take great care when deciding which services shall be
allowed.

Communication with Slack is done through HTTPS, which means that it is less likely that someone reads
it. However, Slack will have access to the bot, and by extension the American government. If this is
principally difficult to swallow, controlling services through Slack is probably not something you'd
want.

To protect against insiders stopping or restarting services without anyone knowing, slack-systemctl will
always respond to a channel you've chosen. By making that a public channel, you ensure that you will
know about it when someone interacts with one of the services. You will not be able to see who did it,
though.

A user's input is escaped when running the shell commands, but they are not escaped when
outputting to Slack. This means that a crafty user can screw up the formatting of the post.
Although it won't look good, since Slack doesn't provide any means to do anything bad
from a message text, this doesn't really impose a risk to anyone.

slack-systemctl hasn't really seen much of any use yet, and as such plenty of bugs are sure to exist,
some of which may compromise the security. You should be aware of the risks involved,
and limit the units and allowed commands so that even in a worse case scenario,
your organization will experience minimal losses. There is no reason to give access
to apache2 (httpd), for example, because 1) you'd much rather use `apache2ctl graceful` anyway to
restart the web server, and 2) whenever you need to restart the web server, you're likely
connected through SSH already. One use case may be making it possible to restart a service
that often ends up hanging or not working, like liquidsoap in our case, and another one could
be a service that you don't want to run all the time, but only at demand.

Please note that no warranties are given, see LICENSE.

### requirements.txt

This project has adapted the [pip workflow suggested by Kenneth Reitz](https://www.kennethreitz.org/essays/a-better-pip-workflow#theworkflow).
In short, `requirements-to-freeze.txt` is where you put the explicit requirements of the project,
used primarily during development, and `requirements.txt` is what you use when 
deploying the application, generated by `pip freeze`. Run `make freeze` to create 
`requirements.txt`, but remember to check that the currently installed pip
packages work first.
