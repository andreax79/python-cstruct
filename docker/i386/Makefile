PROJECT=cstruct
BASENAME=test-i386
IMAGE_NAME=${PROJECT}-${BASENAME}

.PHONY: help build push all

help:
	@echo "- make build        Build docker image"
	@echo "- make test         Build and run tests"
	@echo "- make shell        Run interactive shell"

.DEFAULT_GOAL := help

build:
	@DOCKER_BUILDKIT=1 docker build --tag ${IMAGE_NAME}:latest .

test: build
	@docker run --rm -it \
		--mount type=bind,source=$$PWD/../..,target=/app \
		--hostname=$(BASENAME) \
		${IMAGE_NAME} \
		pytest

shell:
	@docker run --rm -it \
		--mount type=bind,source=$$PWD/../..,target=/app \
		--hostname=$(BASENAME) \
		${IMAGE_NAME} \
		bash -i

all: build
