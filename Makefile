# MIT License
# 
# Copyright (c) 2016 Radio Revolt, the Student Radio of Trondheim
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# User to run as
TARGET_USER = slack-systemctl
# Directory to write logs to
LOG_DIR = "log"

SYSTEMD_UNITFILE = slack-systemctl.service

SUDOERS_FILENAME = slack-systemctl.sudoers

SUDOERS_INSTALL_LOCATION = /etc/sudoers.d/$(SUDOERS_FILENAME)


# Run/deploy slack-systemctl
.PHONY: run
run: settings.yaml settings_slackbot.yaml venv/is_created
	./confirm_is_run_as.sh $(TARGET_USER)
	./confirm_file_permissions.sh
	. venv/bin/activate && rtmbot -c settings_slackbot.yaml

# Configuration files, can be generated through helpful user interface
settings.yaml settings_slackbot.yaml: | venv/is_created
	venv/bin/python generate_settings_file.py "$@" --log-dir $(LOG_DIR)

$(SYSTEMD_UNITFILE) : templates/$(SYSTEMD_UNITFILE) | venv/is_created
	venv/bin/python generate_unit_file.py $(TARGET_USER) "$@"

# Just test that make is run as root. Succeeds if it is, fails if not.
.PHONY: is_root
is_root:
	@test `id -u` -eq 0

# Deploying unit file, must be run as sudo
/etc/systemd/system/$(SYSTEMD_UNITFILE): $(SYSTEMD_UNITFILE) | is_root
	cp "$<" "$@"

.PHONY: deploy
deploy: /etc/systemd/system/$(SYSTEMD_UNITFILE) $(SUDOERS_INSTALL_LOCATION) $(LOG_DIR) is_root
	systemctl enable $(SYSTEMD_UNITFILE)

$(LOG_DIR): | is_root
	mkdir -p $(LOG_DIR)
	chown $(TARGET_USER): $(LOG_DIR)
	chmod 755 $(LOG_DIR)

# Virtual environment
venv/is_created:
	virtualenv -p python3 venv
	touch venv/is_created
	. venv/bin/activate && pip install -r requirements.txt

# Make the application ready for deployment
.PHONY: setup
setup: settings.yaml settings_slackbot.yaml $(SUDOERS_FILENAME)
	id -u $(TARGET_USER) > /dev/null 2>&1 || (echo "Setting up the user, which requires root privileges." && sudo adduser --system --no-create-home --group --disabled-login $(TARGET_USER))

# Sudoers file
slack-systemctl.sudoers: venv/is_created settings.yaml
	@venv/bin/python generate_sudoers_config.py $(TARGET_USER) `which systemctl` > $@

$(SUDOERS_INSTALL_LOCATION): $(SUDOERS_FILENAME) | is_root
	@# First make sure we're not about to override the default sudoers file.
	@# Then check the syntax of the generated sudoers file.
	@# Copy the generated sudoers file to the same folder as the target file.
	@# Replace the target file in one atomic action (since they are in the same folder, they are on the same device).
	test "$@" != "/etc/sudoers" && \
	visudo -c -f "$<" && \
	cp "$<" "$@.transfer" && \
	mv "$@.transfer" "$@"

# Remove any local user-files from the folder
.PHONY: wipe
wipe:
	rm -rf venv settings.yaml settings_slackbot.yaml .installed_requirements slack-systemctl.service


.PHONY: freeze
freeze: venv/is_created
	. venv/bin/activate && pip freeze -r requirements-to-freeze.txt > requirements.txt

