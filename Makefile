# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help


.PHONY: build
build: ## Build docker images
	docker-compose build

.PHONY: test
test: ## Run automated tests
	docker-compose up -d --force-recreate qgisserver \
		&& docker-compose run --rm tester pytest /tests

.PHONY: clean
clean: ## Stop and remove containers
	docker-compose down -v
