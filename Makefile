OLLAMA_CONTAINER ?= ollama
MODEL_BASE        = mistral-small3.2:24b-instruct-2506-q4_K_M
MODEL_NAME        = mistral-small3.2:24b-48k
VM               ?= user@10.0.0.163
NANOBOT_DIR      = ~/.nanobot/workspace

.PHONY: pull create-model recreate-model status restart logs scp help

## Pull the base model from ollama registry (~15GB download)
pull:
	docker exec $(OLLAMA_CONTAINER) ollama pull $(MODEL_BASE)

## Create the named model with custom parameters (run after pull)
create-model:
	docker cp Modelfile $(OLLAMA_CONTAINER):/tmp/Modelfile
	docker exec $(OLLAMA_CONTAINER) ollama create $(MODEL_NAME) -f /tmp/Modelfile
	@echo "Model '$(MODEL_NAME)' ready. Set \"model\": \"$(MODEL_NAME)\" in nanobot config."

## Re-create model (use after editing Modelfile)
recreate-model:
	docker exec $(OLLAMA_CONTAINER) ollama rm $(MODEL_NAME) 2>/dev/null || true
	$(MAKE) create-model

## Full setup from scratch
setup: pull create-model

## Show loaded models
status:
	docker exec $(OLLAMA_CONTAINER) ollama list

## Restart ollama container
restart:
	docker restart $(OLLAMA_CONTAINER)

## Tail ollama container logs
logs:
	docker logs -f $(OLLAMA_CONTAINER)

## SCP all workspace files to the VM (VM=user@IP)
scp:
	ssh $(VM) "mkdir -p $(NANOBOT_DIR)/interview-prep/data/algo $(NANOBOT_DIR)/interview-prep/data/aiml $(NANOBOT_DIR)/interview-prep/data/sql $(NANOBOT_DIR)/skills/interview-prep"
	scp workspace/USER.md $(VM):$(NANOBOT_DIR)/USER.md
	scp workspace/AGENTS.md $(VM):$(NANOBOT_DIR)/AGENTS.md
	scp workspace/SOUL.md $(VM):$(NANOBOT_DIR)/SOUL.md
	scp workspace/interview-prep/data/progress.json $(VM):$(NANOBOT_DIR)/interview-prep/data/progress.json
	scp workspace/interview-prep/data/design_patterns.json $(VM):$(NANOBOT_DIR)/interview-prep/data/design_patterns.json
	scp workspace/interview-prep/data/data_structures.json $(VM):$(NANOBOT_DIR)/interview-prep/data/data_structures.json
	scp workspace/interview-prep/data/neetcode_core.json $(VM):$(NANOBOT_DIR)/interview-prep/data/neetcode_core.json
	scp workspace/interview-prep/data/behavioral.json $(VM):$(NANOBOT_DIR)/interview-prep/data/behavioral.json
	scp workspace/interview-prep/data/system_design.json $(VM):$(NANOBOT_DIR)/interview-prep/data/system_design.json
	scp workspace/interview-prep/data/attempts.json $(VM):$(NANOBOT_DIR)/interview-prep/data/attempts.json
	scp workspace/interview-prep/data/algo/*.json $(VM):$(NANOBOT_DIR)/interview-prep/data/algo/
	scp workspace/interview-prep/data/aiml/*.json $(VM):$(NANOBOT_DIR)/interview-prep/data/aiml/
	scp workspace/interview-prep/data/sql/*.json $(VM):$(NANOBOT_DIR)/interview-prep/data/sql/
	scp workspace/memory/MEMORY.md $(VM):$(NANOBOT_DIR)/memory/MEMORY.md
	scp cron/jobs.json $(VM):~/.nanobot/cron/jobs.json
	scp rotate_session.py $(VM):~/rotate_session.py
	scp skills/interview-prep.md $(VM):$(NANOBOT_DIR)/skills/interview-prep/SKILL.md
	@echo "All files synced to $(VM)"

help:
	@echo ""
	@echo "Usage:"
	@echo "  make setup          Pull base model and create interview-prep model"
	@echo "  make pull           Pull base model only"
	@echo "  make create-model   Create named model from Modelfile"
	@echo "  make recreate-model Rebuild named model after Modelfile changes"
	@echo "  make status         List loaded models"
	@echo "  make restart        Restart ollama container"
	@echo "  make logs           Tail ollama logs"
	@echo "  make scp            SCP all workspace files to VM"
	@echo ""
	@echo "Override container name: make setup OLLAMA_CONTAINER=my-ollama"
	@echo "Override VM target:      make scp VM=mayu@10.0.0.163"
	@echo ""
