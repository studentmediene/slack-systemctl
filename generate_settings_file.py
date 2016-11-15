import jinja2
import argparse
import os.path
import readline
import subprocess


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

parser.add_argument(
    "--log-dir",
    help="Directory to store logs in."
)

def create_completer_func(choices):
    def completer_func(text, state):
        results = [t for t in choices if t.startswith(text)]
        if len(results) <= state:
            return None
        else:
            return results[state]
    return completer_func

def fetch_unit_list():
    output = subprocess.check_output(
        ["systemctl", "list-units", "--plain", "--no-pager", "--no-legend", "-t", "service"]
    ).decode("utf-8")
    lines = output.split("\n")
    units = [line.split()[0] for line in lines if line.split()]
    return units

def create_insert_func(text_to_insert):
    def insert_func():
        readline.insert_text(text_to_insert)
        readline.redisplay()
    return insert_func


parsed = parser.parse_args()
choice = parsed.application
log_dir = parsed.log_dir
systemd_configfile = os.path.join(os.path.dirname(__file__), "settings.yaml")
slackbot_configfile = os.path.join(os.path.dirname(__file__), "settings_slackbot.yaml")

choices = dict()


if choice == "settings.yaml":
    units = dict()
    add_more_units = True
    while add_more_units:
        unit = dict()
        # UNIT
        print("Which unit in systemd will you connect Slack to? (Try out tab completion!)")
        # Prepare readline
        readline.set_completer_delims(" \t\n\"\\'`@$><=;|&{(")
        readline.set_completer(create_completer_func(fetch_unit_list()))
        unit['unit'] = input("> ")

        # ALLOWED COMMANDS
        print("Which systemctl commands shall be available to Slack?")
        commands = {"status": True, "start": False, "stop": False,
                    "restart": False}
        finished = False
        readline.set_completer(create_completer_func(sorted(commands.keys())))
        while not finished:
            print("\n".join(["[" + ("X" if commands[cmd] else " ") + "] " + cmd
                             for cmd in sorted(commands.keys())]))
            print("Toggle which command? (Leave blank when done)")
            answer = input("> ").strip().lower()
            if answer in commands:
                commands[answer] = not commands[answer]
            elif not answer:
                finished = True
            else:
                print("Didn't recognize '%s'" % answer)
        unit['allowed_commands'] = [cmd for cmd in commands if commands[cmd]]

        # KEYWORD
        readline.set_completer(lambda text, state: None)
        print("What must all messages for interacting with this unit start with?")
        print("It should be something that you don't start a message with by accident.")
        default_keyword = "." + (unit['unit'].split(".")[0])
        print("Default: %s" % default_keyword)
        readline.set_pre_input_hook(create_insert_func(default_keyword))
        keyword = input("> ") or default_keyword
        readline.set_pre_input_hook(None)

        # HELP
        print("Describe this unit. End the description with a blank line.")
        help_lines = []
        answer = input("> ")
        while answer:
            help_lines.append(answer)
            answer = input("> ")
        unit['help'] = "\n".join(help_lines)

        # SLACK_CHANNEL
        print("On which channel in Slack should messages be posted?")
        print("Leave blank to post to whichever channel the user posted in.")
        unit['slack_channel'] = input("> ")

        # Add unit
        units[keyword] = unit

        # More units?
        print("Do you want to connect Slack to more units? [yN]")
        add_more_units = True if input("> ").lower().strip() in ("y", "yes") else False
    choices['units'] = units

else:
    # SLACK
    print("Slack API Token?")
    choices['slack_token'] = input("> ")

    # LOGFILE
    choices['logfile'] = log_dir + "/application.log"

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
