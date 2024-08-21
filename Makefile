# Define variables
SSH_USER = ec2-user
SSH_KEY = discord_bot_key.pem
EC2_IP = 15.237.187.176
SCRIPT = main.py
OUTPUT_LOG = output.log
PROJECT_DIR = discord_bot

# Default target: Help
help:
	@echo "Usage:"
	@echo "  make ssh            - Run the ssh EC2 instance AWS"
	@echo "  make run            - Run the script in background"
	@echo "  make status         - Check the running script"
	@echo "  make stop           - Stop the running script"

ssh:
	ssh -i $(SSH_KEY) $(SSH_USER)@$(EC2_IP)

# Run the script in the background
run: stop
	ssh -i $(SSH_KEY) $(SSH_USER)@$(EC2_IP) 'cd $(PROJECT_DIR); source venv/bin/activate; git pull; nohup python3 $(SCRIPT) > $(OUTPUT_LOG) 2>&1 & disown'

# Check running scripts
status:
	ssh -i $(SSH_KEY) $(SSH_USER)@$(EC2_IP) 'ps aux | grep $(SCRIPT)'

# Stop all running processes and commit/push changes if text files updated
stop: push
	ssh -i $(SSH_KEY) $(SSH_USER)@$(EC2_IP) 'ps aux | grep $(SCRIPT) | grep -v grep | awk "{print \$$2}" | xargs -r kill'

push:
	ssh -i $(SSH_KEY) $(SSH_USER)@$(EC2_IP) 'cd $(PROJECT_DIR); source venv/bin/activate; \
	if ! git diff --quiet --exit-code dispo.txt; then \
		git add dispo.txt; \
		CHANGED=1; \
	fi; \
	if ! git diff --quiet --exit-code game_list.txt; then \
		git add game_list.txt; \
		CHANGED=1; \
	fi; \
	if [ "$$CHANGED" = "1" ]; then \
		git commit -m "Updated dispo.txt and/or game_list.txt"; \
		git push origin main; \
	else \
		echo "No changes to dispo.txt or game_list.txt."; \
	fi'

.PHONY: help ssh run status stop push
