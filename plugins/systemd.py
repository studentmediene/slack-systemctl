"""
MIT License

Copyright (c) 2016 Radio Revolt, the Student Radio of Trondheim

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
import logging

from rtmbot.core import Plugin


def parse_config(configfile, slackbotfile):
    with open(configfile) as f:
        doc = yaml.load(f)
    units = doc

    with open(slackbotfile) as f:
        doc2 = yaml.load(f)
    token = doc2["SLACK_TOKEN"]

    return {keyword.lower(): properties for keyword, properties in units.items()}, token


def send_to_slack(self, message, channel):
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


UNITS, TOKEN = parse_config("settings.yaml", "settings_slackbot.yaml")



KEYWORDS = list(UNITS.keys())


class SystemD(Plugin):

    def process_message(self, data):
        logging.debug("SystemD plugin is handling message '%s'." % data['text'])
        global outputs
        to_output = []
        channel = ""
        try:
            # Did we match?
            user_splitted_text = data['text'].split()
            keyword = user_splitted_text[0].lower() if user_splitted_text else ""
            if keyword in KEYWORDS:
                unit = UNITS[keyword]
                channel = unit['slack_channel']
                logging.debug("Matched message with unit '%s'" % keyword)
                # Was any command given, other than help?
                if data['text'].lower().strip() in (keyword, keyword + ' help'):
                    # Print help
                    to_output.append("\n".join([
                        "Usage: `%s [%s]`" % (keyword, '|'.join(unit['allowed_commands'] + ['help'])),
                        unit['help'],
                    ]))
                else:
                    # Figure out which command
                    command = data['text'].strip().split(' ')[1].lower()
                    # Legal command?
                    if command in [cmd.lower() for cmd in unit['allowed_commands']]:
                        # Warning: Make sure you update generate_sudoers_config.py if you
                        # make changes to the following line. Any changes must then be applied
                        # manually by the user to the sudoers file when deploying.
                        final_cmd = ["sudo", "--non-interactive", "systemctl", "--no-ask-password", command] +  unit['unit'].split()
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
            else:
                logging.debug(data['text'] + " does not start with any of " + str(KEYWORDS))
        except Exception as e:
            # Make sure we output the error on Slack
            logging.warn("An error occurred: %s" % str(e))
            to_output.append(str(e))
        if not channel:
            channel = data['channel']
        for text in to_output:
            logging.debug("Sending string '%s' to Slack on channel '%s'" % (text, channel))
            send_to_slack(self, text, channel)
