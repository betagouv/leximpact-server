uninstall:
	@# Uninstall all installed libraries of your current Python workspace.
	@# Handy when testing the instructions described in the README.md file.
	pip freeze | grep -v "^-e" | xargs pip uninstall -y

install:
	@# Install libraries as described in the requirements.txt file.
	pip install --upgrade pip
	pip install -r requirements.txt

run:
	python ./interface_reform/app.py

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
