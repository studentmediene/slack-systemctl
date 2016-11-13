"""
MIT License

Copyright (c) 2016 Radio Revolt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import yaml
import requests
import subprocess


def parse_config(configfile, slackbotfile):
    with open(configfile) as f:
        doc = yaml.load(f)
    unit = doc["unit"]
    allowed_commands = [cmd.lower() for cmd in doc["allowed_commands"]]
    keyword = doc["keyword"]
    help_message = doc["help"]
    channel = doc["slack_channel"]

    with open(slackbotfile) as f:
        doc2 = yaml.load(f)
    token = doc2["SLACK_TOKEN"]

    return unit, allowed_commands, keyword, help_message, channel, token


def send_to_slack(message):
    options = SLACK_OPTIONS
    options['text'] = message
    r = requests.get("https://slack.com/api/chat.postMessage", params=options,
                     timeout=10.0)
    r.raise_for_status()
    r.close()


UNIT, ALLOWED_COMMANDS, KEYWORD, HELP, CHANNEL, TOKEN = parse_config("settings.yaml",
                                                               "settings_slackbot.yaml")

SLACK_OPTIONS = {
    "as_user": True,
    "channel": CHANNEL,
    "token": TOKEN,
}

outputs = []


def process_message(data):
    global outputs
    to_output = []
    if data['text'].startswith(KEYWORD):
        if data['text'].strip() in (KEYWORD, KEYWORD + ' help'):
            to_output.append("\n".join([
                "Usage: `%s [%s]`" % (KEYWORD, '|'.join(ALLOWED_COMMANDS)),
                HELP,
            ]))
        else:
            command = data['text'].strip().split(' ')[1].lower()
            if command in ALLOWED_COMMANDS:
                # Run the command
                result = subprocess.run(
                    # Warning: Make sure you update generate_sudoers_config.py if you
                    # make changes to the following line. Any changes must then be applied
                    # manually by the user to the sudoers file when deploying.
                    ["sudo", "--non-interactive", "systemctl", "--no-ask-password", command, UNIT],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                stdout_str = result.stdout.decode("utf-8")
                output_line = ("Output:\n```%s```" % stdout_str) if stdout_str \
                    else "No output."
                to_output.append("`%s` exited with exit code %s (0 means "
                    "OK).\n\n%s" % (" ".join(result.args), result.returncode,
                    output_line))
            else:
                to_output.append("Did not recognize %s.\nWrite `%s help` for"
                                 " usage." % (command, KEYWORD))
    for text in to_output:
        send_to_slack(text)
