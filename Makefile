TAG=`python3 setup.py --version`

lint:
	@printf "==> linting...\n"
	@python3 -m flake8 --select=DUO pymstodo

pub:
	@printf "==> publishing...\n"
	@git commit -am "v$(TAG)"
	@git tag -a "v$(TAG)" -m "Release $(TAG)"
	@git push --atomic origin master "v$(TAG)"

run: lint pub
	@printf "\nPublished at %s\n\n" "`date`"

.DEFAULT_GOAL := run
.PHONY: lint pub run
