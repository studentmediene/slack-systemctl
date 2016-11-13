# User to run as
TARGET_USER = slack-systemctl
# Directory to write logs to
LOG_DIR = "/var/log/slack-systemctl"

# Run/deploy slack-systemctl
.PHONY: run
run: settings.yaml settings_slackbot.yaml
	./confirm_is_run_as.sh $(TARGET_USER)
	./confirm_file_permissions.sh
	venv/bin/python slackbot/rtmbot.py -c settings_slackbot.yaml

# Configuration files, can be generated through helpful user interface
settings.yaml settings_slackbot.yaml: | .installed_requirements
	venv/bin/python generate_settings_file.py "$@" --log-dir $(LOG_DIR)

SYSTEMD_UNITFILE = slack-systemctl.service
$(SYSTEMD_UNITFILE) : templates/$(SYSTEMD_UNITFILE) | .installed_requirements
	venv/bin/python generate_unit_file.py "$@"

# Just test that make is run as root. Succeeds if it is, fails if not.
.PHONY: is_root
is_root:
	@test `id -u` -eq 0

# Deploying unit file, must be run as sudo
/etc/systemd/system/$(SYSTEMD_UNITFILE): $(SYSTEMD_UNITFILE) is_root
	cp "$<" "$@"

.PHONY: deploy
deploy: /etc/systemd/system/$(SYSTEMD_UNITFILE) $(LOG_DIR) is_root
	systemctl enable $(SYSTEMD_UNITFILE)

$(LOG_DIR): is_root
	mkdir $(LOG_DIR)
	chown $(TARGET_USER): $(LOG_DIR)
	chmod 755 $(LOG_DIR)

# Virtual environment
venv:
	virtualenv -p python3 venv

# This file is used just to make sure we adopt to changes in 
# requirements.txt. Whenever they change, we install the packages
# again and touch this file, so its modified date is set to now.
.installed_requirements: requirements.txt slackbot/requirements.txt | venv
	. venv/bin/activate && pip install -r requirements.txt
	touch .installed_requirements

# Make the application ready for deployment
.PHONY: setup
setup: .installed_requirements settings.yaml settings_slackbot.yaml
	id -u $(TARGET_USER) > /dev/null 2>&1 || (echo "Setting up the user, which requires root privileges." && sudo adduser --system --no-create-home --group --disabled-login $(TARGET_USER))

.PHONY: sudoers
sudoers: .installed_requirements settings.yaml
	@venv/bin/python generate_sudoers_config.py $(TARGET_USER) `which systemctl`

# Remove any local user-files from the folder
.PHONY: wipe
wipe:
	rm -rf venv settings.yaml settings_slackbot.yaml .installed_requirements slack-systemctl.service


