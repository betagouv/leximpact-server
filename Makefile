#!/bin/bash

.PHONY: server

COLOR_CYAN='\033[0;36m'
COLOR_STOP='\033[0m'

uninstall:
	@# Uninstall all installed libraries of your current Python workspace.
	@# Handy when testing the instructions described in the README.md file.
	pip freeze | grep -v "^-e" | xargs pip uninstall -y

install:
	@# Install libraries as described in the requirements.txt file.
	pip install --upgrade pip
	pip install --editable .[dev] --upgrade

clean:
	find . -name '*.pyc' -exec rm \{\} \;

check-style:
	@# Do not analyse .gitignored files.
	@# `make` needs `$$` to output `$`. Ref: http://stackoverflow.com/questions/2382764.
	flake8 `git ls-files | grep "\.py$$"`

check-types:
	@# Do not analyse .gitignored files.
	@# `make` needs `$$` to output `$`. Ref: http://stackoverflow.com/questions/2382764.
	mypy `git ls-files | grep "\.py$$"`

format-style:
	@# Do not analyse .gitignored files.
	@# `make` needs `$$` to output `$`. Ref: http://stackoverflow.com/questions/2382764.
	autopep8 `git ls-files | grep "\.py$$"`

migrate:
	python repo/create_db.py
	alembic -x env=development upgrade head
	alembic -x env=test upgrade head

run:
	FLASK_ENV=development PORT=5000 python ./server/app.py

test: clean check-style check-types
	pytest
	@echo -e ${COLOR_CYAN}"Comparaison des calculs DGCL et LexImpact..."${COLOR_STOP}
	python ./tests/dotations/compare_with_dgcl.py

stress-server:
	./tests/server/stress/server.sh

stress-test:
	./tests/server/stress/benchmark.sh

simpop:
	python ./Simulation_engine/simulate_pop_from_reform.py

simpop_profile:
	python -m cProfile -o tests.cprof ./Simulation_engine/simulate_pop_from_reform.py

simpop_stats:
	python -c "import pstats; p = pstats.Stats('tests.cprof'); p.strip_dirs().sort_stats('tottime').print_stats(20)"

simpop_callers:
	python -c "import pstats; p = pstats.Stats('tests.cprof'); p.strip_dirs().sort_stats('tottime').print_callers(5)"

simpop_callees:
	python -c "import pstats; p = pstats.Stats('tests.cprof'); p.strip_dirs().sort_stats('tottime').print_callees(5)"

simpop_snakeviz:
	snakeviz tests.cprof
