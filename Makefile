PR=poetry run
COVERAGE=$(PR) coverage
PYTEST=PYTHONPATH=. $(PR) pytest --cov=p2g --cov-append
GOLDEN=p2g/tests/golden
OXRST=~/.emacs.d/straight/build/ox-rst/ox-rst.el
######################################################################

top: .poetry_and_deps_installed requirements.txt examples  wip

P2G_SRC=$(wildcard p2g/*.py)

######################################################################
# Build machinary
.PHONY:
download_poetry:
	echo "downloading poetry, ^C to stop"
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
	echo __version__ = '"v'$(shell poetry version -s)'"'  > p2g/version.py
	git tag v$$(poetry version -s)
	git commit -a -m "bumped v$$(poetry version -s)"
.PHONY:
bump-inc:
	poetry version patch
	grep "^version" pyproject.toml 
build: doc
	cp p2g/doc/readme.rst README.rst
	poetry build 

bcheck: build
	pip install --force dist/*gz
	type p2g
	$(PR)	p2g test	


release:
	 poetry publish --build -r testpypi 


test-standard:
	$(V) echo FAIL  > $(GOLDEN)/test_error_test_forcefail0.nc
	$(V) echo XFAIL > $(GOLDEN)/test_meta_test_simple_xfail1.nc
	$(V) $(PYTEST)  


 

test-cli:
	$(COVERAGE) run --append -m  p2g --debug test  > /dev/null 2> /dev/null

.PHONY:
coverage-reset:
	rm -f .coverage
.PHONY:
coverage-convert:
	$(COVERAGE) lcov --include=p2g/*.py 
.PHONY:
coverage-report:
	$(COVERAGE) report  --include=p2g/*.py 


.PHONY:
test: |  top  coverage-reset   test-cli test-standard  coverage-convert 




newtests:
	git add p2g/tests/golden/*.nc
	git add p2g/tests/*.py

######################################################################
# linty stuff
isort:
	$(V)	isort .
ssort:
	$(V)	echo p2g/*.py | xargs $(PR) ssort

autoflake:
	$(V) $(PR) autoflake --ignore-init-module-imports  --remove-all-unused-imports  -i -v $(P2G_SRC)

mypy:
	$(V) - $(PR) mypy p2g | cat

flake8:
	$(V) - $(PR) flake8p p2g | cat

pylint:
	$(V) - $(PR) pylint p2g

ruff:
	$(V) - NO_COLOR=1 $(PR) ruff check  p2g
sf:
	$(V) - python 	/home/sac/w/nih/snakefood/main.py . p2g


clean:
	git clean -fdx

cleanup: isort ssort autoflake

lint: mypy  flake8 pylint  ruff

checkdeps:
	$(PR) deptry .





# Build my wips
DSTDIR=/home/sac/vf3/_nc_
SRCDIR=/home/sac/vf3/progs/p2g/p2g/examples

wip:   $(DSTDIR)/.mark-probecalibrate


VPATH=$(SRCDIR):$(DSTDIR)
$(DSTDIR)/.mark-%: %.py
	poetry run p2g --debug --out="$(DSTDIR)/<time>-$*.nc"  gen $<
#	touch $@





