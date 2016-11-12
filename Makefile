# Run/deploy slack-systemctl
.PHONY: run
run: settings.yaml settings_slackbot.yaml .installed_requirements
	venv/bin/python slackbot/rtmbot.py -c settings_slackbot.yaml

# Configuration files, can be generated through helpful user interface
settings.yaml settings_slackbot.yaml: | .installed_requirements
	venv/bin/python generate_settings_file.py "$@"

SYSTEMD_UNITFILE = slack-systemctl.service
$(SYSTEMD_UNITFILE) : templates/$(SYSTEMD_UNITFILE) | .installed_requirements
	venv/bin/python generate_unit_file.py "$@"

# Deploying unit/job files, must be run as sudo
# The SystemD unit file
/etc/systemd/system/$(SYSTEMD_UNITFILE): $(SYSTEMD_UNITFILE)
	cp "$<" "$@"

.PHONY: deploy
deploy-systemd: /etc/systemd/system/$(SYSTEMD_UNITFILE)
	systemctl enable $(SYSTEMD_UNITFILE)

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

# Remove any local user-files from the folder
.PHONY: wipe
wipe:
	rm -rf venv settings.yaml settings_slackbot.yaml .installed_requirements slack-systemctl.service


