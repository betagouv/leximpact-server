.PHONY: server

uninstall:
	@# Uninstall all installed libraries of your current Python workspace.
	@# Handy when testing the instructions described in the README.md file.
	pip freeze | grep -v "^-e" | xargs pip uninstall -y

install:
	@# Install libraries as described in the requirements.txt file.
	pip install --upgrade pip
	pip install --editable .[dev] --upgrade

format-style:
	@# Do not analyse .gitignored files.
	@# `make` needs `$$` to output `$`. Ref: http://stackoverflow.com/questions/2382764.
	autopep8 `git ls-files | grep "\.py$$"`
	black `git ls-files | grep "\.py$$"`

run:
	FLASK_ENV=development PORT=5000 python ./server/app.py

test:
	flake8 `git ls-files | grep "\.py$$"`
	pytest

stress:
	./tests/stress/benchmark.sh

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
