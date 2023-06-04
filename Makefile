TITLE=@ echo 
PR=poetry run
COVERAGE=$(PR) coverage
PYTEST=PYTHONPATH=. $(PR) pytest --cov=p2g --cov-append
GOLDEN=p2g/tests/golden
OXRST=~/.emacs.d/straight/build/ox-rst/ox-rst.el
######################################################################

top: .poetry_and_deps_installed requirements.txt doc examples 

P2G_SRC=$(wildcard p2g/*.py)

######################################################################
# Build machinary

download_poetry:
	echo 		 "downloading poetry, ^C to stop"
	sleep 3
	curl -sSL https://install.python-poetry.org | python3 -

requirements.txt: pyproject.toml
	poetry export -f requirements.txt --output requirements.txt

.poetry_and_deps_installed:
	if [ ! $$(which poetry) ] ; then make download_poetry; fi
	poetry env use 3.11
	poetry install
	touch $@

######################################################################
# Examples.

examples: p2g/examples/vicecenter.nc p2g/examples/probecalibrate.nc

%.nc:%.py
	$(PR) p2g gen $< -o $@

######################################################################
# Doc and machine generated headers.

doc: p2g/doc/readme.rst p2g/doc/haas.org p2g/doc/haas.txt p2g/haas.py README.rst   AUTHORS.rst

p2g/doc/readme.rst: p2g/doc/readme.org p2g/doc/haas.org

p2g/haas.py: p2g/makestdvars.py 
	poetry run p2g stdvars --py=$@ 

p2g/doc/haas.txt: p2g/makestdvars.py
	poetry run p2g stdvars --txt=$@ 

p2g/doc/haas.org: p2g/makestdvars.py
	poetry run p2g stdvars --org=$@ 

AUTHORS.rst: p2g/doc/authors.rst
	cp  $< $@

README.rst: p2g/doc/readme.rst
	cp  $< $@

LICENSE.rst: p2g/doc/license.rst
	cp  $< $@

p2g/doc/%.rst: p2g/doc/%.org
	emacs $< --batch -l $(OXRST) -f org-rst-export-to-rst --kill

######################################################################
# release:
VERSION := $(shell poetry version -s )
.PHONY: 
bump: bump-inc | bump-install

.PHONY:
bump-install:
	echo __version__ = '"'$(shell poetry version -s)'"'  > p2g/version.py
	git tag $$(poetry version -s)
	git commit -a -m "bumped $$(poetry version -s)"
.PHONY:
bump-inc:
	poetry version patch
	grep "^version" pyproject.toml 
build:
	cp p2g/doc/readme.rst README.rst
	poetry build 

bcheck: build
	pip install --force dist/*gz
	type p2g
	$(PR)	p2g test	


release:
	 poetry publish --build -r testpypi 


test-standard:
	$(V)	$(PYTEST) 


# force some errors, kick the tyres.
test-fails:
	$(V) echo FAIL  > $(GOLDEN)/error_xfail_force_fail.nc
	$(V) echo XFAIL > $(GOLDEN)/meta_simple_xfail1.nc
	$(TITLE) Test things which should fail
	$(PYTEST) p2g/tests/test_error.py -m forcefail  > err 2>&1 || (exit 0)
 

test-cli:
	$(COVERAGE) run --append -m  p2g --debug test  > /dev/null 2> /dev/null

.PHONY:
coverage-reset:
	rm -f .coverage
.PHONY:
coverage-convert:
	$(COVERAGE) lcov
.PHONY:
coverage-report:
	$(COVERAGE) report


.NOTPARALLEL:
test: top coverage-reset test-cli test-fails   test-standard coverage-convert




newtests:
	git add p2g/tests/golden/*.nc
	git add p2g/tests/*.py

######################################################################
# linty stuff
isort:
	$(TITLE) isort
	$(V)	isort .
ssort:
	$(TITLE) ssort
	$(V)	echo p2g/*.py | xargs $(PR) ssort

autoflake:
	$(TITLE) Autoflake
	$(V) $(PR) autoflake --ignore-init-module-imports  --remove-all-unused-imports  -i -v $(P2G_SRC)

mypy:
	$(TITLE) mypy
	$(V) - $(PR) mypy p2g

flake8:
	$(TITLE) flake8
	$(V) - $(PR) flake8p p2g | cat

pylint:
	$(TITLE) pylint
	$(V) - $(PR) pylint p2g

ruff:
	$(TITLE) ruff
	$(V) - NO_COLOR=1 $(PR) ruff check  p2g
sf:
	$(TITLE) sf
	$(V) - python 	/home/sac/w/nih/snakefood/main.py . p2g


clean:
	git clean -fdx

cleanup: isort ssort autoflake

lint: mypy  flake8 pylint  ruff

checkdeps:
	$(PR) deptry .




# copy test results to goldens
gold:
	find tests -name "*.new"  | sed "s/\([^.]*\).new/mv \1.new \1.nc/g" | bash
# for the ones which must fail
	echo fail > p2g/tests/golden/meta_simple_xfail.nc
	echo fail > p2g/tests/golden/error_force_fail.nc




