.PHONY: test run deploy rollback

test:
	python3 -m unittest discover -s tests

run:
	python3 -m notes.server

deploy:
	./tools/ship.sh $(ENV)

rollback:
	./tools/ship.sh $(ENV) --previous
