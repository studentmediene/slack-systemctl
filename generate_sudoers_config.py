import argparse
import yaml

def get_command_alias(units):
    commands = []
    for unit, unit_commands in units.items():
        for command in unit_commands:
            commands.append('systemctl "{command}" "{unit}"'\
                .format(command=command, unit=unit))
    return "Cmnd_Alias SLACK_SYSTEMCTL_CMDS = {commands}"\
        .format(commands=", ".join(commands))

def get_user_specification(user):
    return "{user} ALL = NOPASSWD: SLACK_SYSTEMCTL_CMDS".format(user=user)


def parse_config(configfile):
    with open(configfile) as f:
        doc = yaml.load(f)
    unit = doc["unit"]
    allowed_commands = [cmd.lower() for cmd in doc["allowed_commands"]]
    return {unit: allowed_commands}

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate configuration for the sudoers file."
    )

    parser.add_argument(
        "user",
        help="The user the application shall run as."
    )

    args = parser.parse_args()
    return {"user": args.user}

def main():
    args = parse_args()
    units = parse_config("settings.yaml")
    print("Place the following somewhere in the sudoers file:\n")
    print(get_command_alias(units))
    print(get_user_specification(args['user']))

if __name__ == "__main__":
    main()

