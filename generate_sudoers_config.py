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
    print("Place the following somewhere in the sudoers file:\n")
    print(get_command_alias(units, args['systemctl']))
    print(get_user_specification(args['user']))

if __name__ == "__main__":
    main()

