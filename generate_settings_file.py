import jinja2
import argparse
import os.path


parser = argparse.ArgumentParser(
    description="Generate settings.yaml or settings_slackbot.yaml"
)

parser.add_argument(
    "application",
    nargs="?",
    choices=["settings.yaml", "settings_slackbot.yaml"],
    default="settings.yaml",
    help="The kind of settings file you want to create."
)

parsed = parser.parse_args()
choice = parsed.application
systemd_configfile = os.path.join(os.path.dirname(__file__), "settings.yaml")
slackbot_configfile = os.path.join(os.path.dirname(__file__), "settings_slackbot.yaml")

choices = dict()


if choice == "settings.yaml":
    # UNIT
    print("Which unit in systemd will you connect Slack to?")
    choices['unit'] = input("> ")

    # ALLOWED COMMANDS
    print("Which systemctl commands shall be available to Slack?")
    commands = {"status": True, "start": False, "stop": False,
                "restart": False}
    finished = False
    while not finished:
        print("\n".join(["[" + ("X" if commands[cmd] else " ") + "] " + cmd
                         for cmd in commands]))
        print("Toggle which command? (Leave blank when done)")
        answer = input("> ").strip().lower()
        if answer in commands:
            commands[answer] = not commands[answer]
        elif not answer:
            finished = True
        else:
            print("Didn't recognize '%s'" % answer)
    choices['allowed_commands'] = [cmd for cmd in commands if commands[cmd]]

    # KEYWORD
    print("What must all messages for this Slackbot start with?")
    print("It should be something that you don't write by accident.")
    default_keyword = "." + choices['unit']
    print("Default: %s" % default_keyword)
    choices['keyword'] = input("> ") or default_keyword

    # HELP
    print("Describe this Slackbot. End the description with a blank line.")
    help_lines = []
    answer = input("> ")
    while answer:
        help_lines.append(answer)
        answer = input("> ")
    choices['help'] = "\n".join(help_lines)

    # SLACK_CHANNEL
    print("On which channel in Slack should messages be posted?")
    choices['slack_channel'] = input("> ")

else:
    # SLACK
    print("Slack API Token?")
    choices['slack_token'] = input("> ")

    # LOGFILE
    print("Where would you like the logfile to be?")
    print("Must be writable by the user SlackBot will run as.")
    choices['logfile'] = input("> ")

print("Generating the file...")

# Generate the files!
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
if choice == "settings.yaml":
    template = env.get_template("settings.yaml")
    with open(systemd_configfile, "w") as f:
        f.write(template.render(**choices))

else:
    template = env.get_template("settings_slackbot.yaml")
    with open(slackbot_configfile, "w") as f:
        f.write(template.render(**choices))
