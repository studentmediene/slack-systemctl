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
import os.path
import jinja2

parser = argparse.ArgumentParser(
    description="Generate unit file for systemd"
)

parser.add_argument(
    "user",
    help="User to run the application as."
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
    output.write(template.render(path=path, user=args.user))
finally:
    output.close()
