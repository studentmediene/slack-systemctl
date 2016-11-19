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

import argparse
import yaml

def get_command_alias(units, systemctl):
    commands = set()
    for unit, unit_commands in units.items():
        for command in unit_commands:
            # Warning: Make sure the following line is up-to-date to whatever
            # is run in slackbot/plugins/systemd.py!
            commands.add('{systemctl} --no-ask-password {command} {unit}'\
                .format(systemctl=systemctl, command=command, unit=unit))
    return "Cmnd_Alias SLACK_SYSTEMCTL_CMDS = {commands}"\
        .format(commands=", ".join(commands))

def get_user_specification(user):
    return "{user} ALL = NOPASSWD: SLACK_SYSTEMCTL_CMDS".format(user=user)


def parse_config(configfile):
    with open(configfile) as f:
        doc = yaml.load(f)
    return {unit['unit']: unit['allowed_commands'] for unit in doc.values()}

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate configuration for the sudoers file."
    )

    parser.add_argument(
        "user",
        help="The user the application shall run as."
    )

    parser.add_argument(
        "systemctl_path",
        help="Absolute path of systemctl."
    )

    args = parser.parse_args()
    return {"user": args.user, "systemctl": args.systemctl_path}

def main():
    args = parse_args()
    units = parse_config("settings.yaml")
    print("# Configuration for slack-systemctl. Generated automatically by `sudo make deploy`.")
    print(get_command_alias(units, args['systemctl']))
    print(get_user_specification(args['user']))

if __name__ == "__main__":
    main()

