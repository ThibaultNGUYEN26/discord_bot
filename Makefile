# Define variables
SSH_USER = ec2-user
SSH_KEY = discord_bot_key.pem
EC2_IP = 15.237.187.176
SCRIPT = main.py
OUTPUT_LOG = output.log
PROJECT_DIR = discord_bot
IMAGE_NAME = discord-bot

# Default target: Help
help:
	@echo "Usage:"
	@echo "  make ssh            - Run the ssh EC2 instance AWS"
	@echo "  make run            - Run the script in background"
	@echo "  make status         - Check the running script"
	@echo "  make stop           - Stop the running script"
	@echo "  make build          - Build the Docker image"
	@echo "  make docker-run     - Run the bot using Docker"
	@echo "  make docker-stop    - Stop the Docker container"
	@echo "  make clean          - Remove Docker images"

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

# Docker-related targets
build:
	docker build -t $(IMAGE_NAME) .

docker-run: docker-stop
	docker run --rm -d \
		-v $(PWD)/dispo.txt:/app/dispo.txt \
		-v $(PWD)/game_list.txt:/app/game_list.txt \
		--env-file .env --name $(IMAGE_NAME) $(IMAGE_NAME)

docker-status:
	docker ps | grep $(IMAGE_NAME)

docker-stop:
	-docker stop $(IMAGE_NAME)

clean:
	docker rmi $(IMAGE_NAME)

.PHONY: help ssh run status stop push build docker-run docker-status docker-stop clean
