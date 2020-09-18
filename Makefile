TAG=`python3 setup.py --version`

lint:
	@printf "==> linting...\n"
	@python3 -m flake8 --select=DUO pymstodo

tag:
	@printf "==> tagging...\n"
	@git tag -a "v$(TAG)" -m "Release $(TAG)"

pub:
	@printf "==> git push...\n"
	@git push origin "v$(TAG)"
	@git push

run: lint tag pub
	@printf "\nPublished at %s\n\n" "`date`"

.DEFAULT_GOAL := run
.PHONY: lint tag pub run
