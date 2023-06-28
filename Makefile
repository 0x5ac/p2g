SRC_DIR=./p2g
DOC_DIR=./doc
EXAMPLE_DIR=./examples
TESTS_DIR=./tests
EMACS?=emacs
POETRY=poetry 
PR=$(POETRY) run
PG=$(POETRY) run
#PG=python -m 
COVERAGE=$(PR) coverage

PYTEST=$(PR) pytest --cov=$(SRC_DIR) --cov-append
OX_GFM_DIR=~/.emacs.d/straight/build/ox-gfm


ECHO=@ echo
######################################################################

GENERATED_SRC=$(SRC_DIR)/haas.py

SRC=$(SRC_DIR)/axis.py				\
    $(GENERATED_SRC)				\
    $(SRC_DIR)/builtin.py			\
    $(SRC_DIR)/coords.py			\
    $(SRC_DIR)/err.py				\
    $(SRC_DIR)/gbl.py				\
    $(SRC_DIR)/goto.py				\
    $(SRC_DIR)/__init__.py			\
    $(SRC_DIR)/lib.py				\
    $(SRC_DIR)/__main__.py			\
    $(SRC_DIR)/main.py				\
    $(SRC_DIR)/makestdvars.py			\
    $(SRC_DIR)/nd.py				\
    $(SRC_DIR)/op.py				\
    $(SRC_DIR)/ptest.py				\
    $(SRC_DIR)/scalar.py				\
    $(SRC_DIR)/stat.py				\
    $(SRC_DIR)/symbol.py				\
    $(SRC_DIR)/vector.py				\
    $(SRC_DIR)/visible.py			\
    $(SRC_DIR)/walkbase.py			\
    $(SRC_DIR)/walkexpr.py			\
    $(SRC_DIR)/walkfunc.py			\
    $(SRC_DIR)/walk.py


TESTS=$(TESTS_DIR)/*.py

COMPILED_EXAMPLES=$(EXAMPLE_DIR)/vicecenter.nc \
                  $(EXAMPLE_DIR)/probecalibrate.nc

COMPILED_DOC=\
	$(DOC_DIR)/haas.org				\
	$(DOC_DIR)/haas.txt				\
	$(DOC_DIR)/readme.txt				\
	readme.md \
	license.md					\
	authors.md

ALL_FOR_DIST= $(COMPILED_EXAMPLES)  $(COMPILED_DOC) $(GENERATED_SRC) $(SRC)

top: poetry-install $(ALL_FOR_DIST)
	$(ECHO) Ready for build dist.
######################################################################
# Init environment


.PHONY:
poetry-install: .poetry_and_deps_installed
	$(ECHO) Poetry installed.

.poetry_and_deps_installed: readme.md
	$(POETRY) install
	touch $@



######################################################################
# Examples.
.PHONY:
compiled-examples: 
	$(ECHO) Examples ready.

%.nc:%.py 
	$(PG) p2g gen $<  $@

######################################################################
# Doc and machine generated headers.

$(SRC_DIR)/haas.py: $(SRC_DIR)/makestdvars.py 
	$(PG) p2g stdvars --py=$@ 

$(DOC_DIR)/haas.txt: p2g/makestdvars.py
	$(PG) p2g stdvars --txt=$@ 

$(DOC_DIR)/haas.org: $(SRC_DIR)/makestdvars.py
	$(PG) p2g stdvars --org=$@ 

HAVE_EMACS=$(and  $(shell which $(EMACS)),$(wildcard $(OX_GFM_DIR)/*),1)

VPATH=$(DOC_DIR)

ifeq ($(HAVE_EMACS),1)
ELCOMMON=  --directory $(OX_GFM_DIR)					\
           -q 								\
           --batch 							\
           --eval  "(require 'ox-ascii)"				\
           --eval "(require 'ox-gfm)"					\
           --eval "(setq org-confirm-babel-evaluate nil)"		\
           --eval "(setq default-directory \"$(realpath $(@D))\")"
%.md: %.org
	emacs  $<  $(ELCOMMON) --eval   "(org-gfm-export-to-markdown)"
	rm -f $*.md.tmp

%.txt: %.org
	emacs  $< $(ELCOMMON) --eval       "(org-ascii-export-to-ascii)"

else

%.md: %.org
	@ echo
	@ echo "edit makefile - emacs not setup"
	@ echo
	touch $@
%.txt: %.org
	@ echo
	@ echo "edit makefile - emacs not setup"
	@ echo
	touch $@
endif

######################################################################
# release:
VERSION=$(shell cat pyproject.toml | grep "^version =" | sed 's:version = "\(.*\)":\1:g')

.PHONY:
bump-tag:
	git tag $(shell $(POETRY) version -s)
.PHONY: 
bump: | bump-inc  bump-install  bump-tag

.PHONY:

bump-install:
	sed -i $(SRC_DIR)/__init__.py -e 'sX^VERSION.*XVERSION = "$(shell $(POETRY) version -s)"Xg' 

.PHONY:
bump-inc:
	$(POETRY) version patch


.PHONY:
build: clean compiled-doc lint
	$(POETRY) build 

.PHONY:
bcheck: build
	pip install --force dist/*gz
	type p2g
	$(PR)	p2g test	> test.output 2>&1
	diff -u test.output.prev test.output
	cp test.output test.output.prev


.PHONY:
publish:dist/p2g-$(VERSION).tar.gz
	$(POETRY) publish 

.PHONY:
dist: dist/p2g-$(VERSION).tar.gz
	$(ECHO) Dist made.


dist/p2g-$(VERSION).tar.gz: pyproject.toml   $(ALL_FOR_DIST)
	@ # want to distribute examples  and docs, so copy
	@ # somewhere safe.
	@ rm -rf  $(SRC_DIR)/doc $(SRC_DIR)/examples
	@ cp -a $(DOC_DIR) $(EXAMPLE_DIR) $(SRC_DIR)
	$(POETRY) build
	@ rm -rf  $(SRC_DIR)/doc $(SRC_DIR)/examples

.PHONY:
test-standard:
	$(PYTEST) 

.PHONY:
coverage-reset:
	rm -f .coverage
.PHONY:
coverage-convert:
	$(COVERAGE) lcov -q
.PHONY:
coverage-report:
	$(COVERAGE) report

.PHONY:
test: | top coverage-reset     test-standard coverage-convert


######################################################################
# linty stuff
.PHONY:
isort:
	$(PR) isort $(SRC) $(TESTS)
.PHONY:
ssort:
	 $(PR) ssort $(SRC) $(PRECIOUS_SRC)  $(TESTS)
.PHONY:
autoflake:
	 $(PR) autoflake --ignore-init-module-imports  --remove-all-unused-imports  -i -v $(SRC)   $(TESTS)
.PHONY:
pyright:
	 $(PR)  pyright p2g 
.PHONY:
mypy:
	 $(PR) mypy p2g 
.PHONY:
flake8:
	 $(PR) flake8p p2g  |cat
.PHONY:
pylint:
	 $(PR) pylint p2g 
.PHONY:
ruff:
	 $(PR) ruff check  p2g | cat
.PHONY:
clean:
	git clean -fdx
	rm -f $(COMPILED_EXAMPLES)
ifeq ($(HAVE_EMACS),1)
	rm -f $(COMPILED_DOC) 
endif

.PHONY:
cleanup: isort ssort autoflake

.PHONY:
checkdeps:
	$(PR) deptry .


.PHONY:
lint: pyright mypy  flake8 pylint  ruff  checkdeps





# Build my wips
mall:
	 sed 'sXfrom.*import \(.*\)X"\1\",Xg' p2g/__init__.py
verbose:
	poetry run pytest tests/test_vars.py  -vvvv --capture=tee-sys
.PHONY:
sf:
	 python 	/home/sac/w/nih/snakefood/main.py . p2g

DSTDIR=/home/sac/vf3/_nc_
NSRC_DIR=/home/sac/vf3/progs/p2g/examples

wip:  wip-probe

wip-probe: $(DSTDIR)/.mark-probecalibrate

