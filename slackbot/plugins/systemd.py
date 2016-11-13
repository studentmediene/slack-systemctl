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
    units = doc

    with open(slackbotfile) as f:
        doc2 = yaml.load(f)
    token = doc2["SLACK_TOKEN"]

    return units, token


def send_to_slack(message, channel):
    if channel:
        options = {
            "as_user": True,
            "channel": channel,
            "token": TOKEN,
            "text": message,
        }
        r = requests.get("https://slack.com/api/chat.postMessage", params=options,
                         timeout=10.0)
        r.raise_for_status()
        r.close()
    else:
        outputs.append(message)


UNITS, TOKEN = parse_config("settings.yaml", "settings_slackbot.yaml")

outputs = []


def process_message(data):
    global outputs
    to_output = []
    channel = ""
    try:
        # Did we match anything at all? (Most messages won't match, so don't spend time figuring out what matched)
        if data['text'].startswith(UNITS.keys()):
            # Which unit did we match? Compare to the longest key firsts, to ensure we don't match a substring of another unit.
            keyword = [keyword for keyword in sorted(UNITS.keys(), key=len, reverse=True) if data['text'].startswith(keyword)][0]
            unit = UNITS[keyword]
            channel = unit['slack_channel']
            # Was any command given, other than help?
            if data['text'].strip() in (keyword, keyword + ' help'):
                # Print help
                to_output.append("\n".join([
                    "Usage: `%s [%s]`" % (keyword, '|'.join(unit['allowed_commands'])),
                    unit['help'],
                ]))
            else:
                # Figure out which command
                command = data['text'].strip().split(' ')[1].lower()
                # Legal command?
                if command in [cmd.lower() for cmd unit['allowed_commands']]:
                    # Warning: Make sure you update generate_sudoers_config.py if you
                    # make changes to the following line. Any changes must then be applied
                    # manually by the user to the sudoers file when deploying.
                    final_cmd = ["sudo", "--non-interactive", "systemctl", "--no-ask-password", command, unit['unit']]
                    try:
                        # Run the command
                        result = subprocess.check_output(
                            final_cmd,
                            stderr=subprocess.STDOUT
                        )
                        returncode = 0
                    except subprocess.CalledProcessError as e:
                        result = e.output
                        returncode = e.returncode
                    # Formulate response on Slack
                    stdout_str = result.decode("utf-8")
                    output_line = ("\n\nOutput:\n```%s```" % stdout_str) if stdout_str \
                        else "" if returncode==0 else "\n\nNo output."
                    output_command = "`systemctl {command} {unit}`"\
                        .format(command=command, unit=unit['unit'])
                    status_msg = "Successfully executed " if returncode == 0 \
                        else "Error ({returncode}): could not run ".format(returncode=returncode)
                    to_output.append("{status_msg}{cmd}{output}".format(
                        status_msg=status_msg,
                        cmd=output_command,
                        output=output_line))
                else:
                    to_output.append("Did not recognize %s.\nWrite `%s help` for"
                                     " usage." % (command, keyword))
    except Exception as e:
        # Make sure we output the error on Slack
        to_output.append(str(e))
    for text in to_output:
        send_to_slack(text, channel)
