import argparse
import os.path
import jinja2

parser = argparse.ArgumentParser(
    description="Generate unit file for systemd"
)

parser.add_argument(
    "output",
    nargs="?",
    type=argparse.FileType("w", encoding="UTF-8"),
    help="Where to output the file. Use - for stdout (default).",
    default="-"
)

args = parser.parse_args()
output = args.output
try:
    path = os.path.dirname(os.path.realpath(__file__))

    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    template = env.get_template(
        "slack-systemctl.service"
    )
    output.write(template.render(path=path))
finally:
    output.close()
