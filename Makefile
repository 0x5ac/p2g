
top: | install-tools  prepare-dist
	$(HR)
	$(TITLE) 
	$(TITLE) 


PATH=$(HOME)/.local/bin:/usr/bin
SRC_DIR=./p2g
DOC_DIR=./doc
EXAMPLE_DIR=./examples
TESTS_DIR=./tests
EMACS?=emacs
POETRY=poetry 
PR=$(POETRY) run
P2G_SCRIPT=$(POETRY) run p2g

THIS_VERSION=$(shell $(P2G_SCRIPT) version)
NEXT_VERSION=$(shell $(P2G_SCRIPT) version  --bump 3)

#PG=python -m 
COVERAGE=$(PR) coverage

PYTEST=$(PR) pytest

OX_GFM_DIR=~/.emacs.d/straight/build/ox-gfm


TITLE=@ echo
MAYLOG=@
HR=@echo  "********************************************************"
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

LINTABLE_SRC=$(SRC) $(GENERATED_SRC) $(TESTS)
COMPILED_EXAMPLES=$(EXAMPLE_DIR)/vicecenter.nc \
                  $(EXAMPLE_DIR)/probecalibrate.nc

COMPILED_DOC=\
	$(DOC_DIR)/haas.org				\
	$(DOC_DIR)/haas.txt				\
	$(DOC_DIR)/readme.txt				\
	readme.md \
	license.md					\
	authors.md

CONTROL_FILES=Makefile pyproject.toml .scrutinizer.yml 
ALL_SRC_FOR_DIST=$(CONTROL_FILES) $(COMPILED_EXAMPLES)  $(COMPILED_DOC) $(GENERATED_SRC) $(SRC)


.PHONY:
compile: $(ALL_SRC_FOR_DIST) 

######################################################################
# Init environment


.PHONY:
install-tools: .poetry_installed .deps_installed


.deps_installed:
	$(HR)
	$(TITLE)
	$(TITLE)  Install dependencies.
	$(POETRY) -q install
	$(MAYLOG)	touch $@


.PHONY:
install-poetry:
	$(HR)
	$(TITLE)
	$(TITLE) Install poetry using pip.
	pip install -q --force-reinstall --user --upgrade poetry
	pip install -q --force-reinstall --user --upgrade tox


.poetry_installed:
	$(HR)
	$(MAYLOG) if [ ! $$(which poetry) ] ; then make install-poetry ; fi
	$(MAYLOG) 	touch $@
	$(TITLE)
	$(TITLE) Poetry installed in $$(which poetry)


######################################################################
# examples
%.nc:%.py 
	$(P2G_SCRIPT) gen $^  $@

######################################################################
# Doc and machine generated headers.

$(SRC_DIR)/haas.py: $(SRC_DIR)/makestdvars.py 
	$(P2G_SCRIPT)  stdvars --py=$@ 

$(DOC_DIR)/haas.txt: p2g/makestdvars.py
	$(P2G_SCRIPT)  stdvars --txt=$@ 

$(DOC_DIR)/haas.org: $(SRC_DIR)/makestdvars.py 
	$(P2G_SCRIPT) stdvars --org=$@ 

HAVE_EMACS=$(and  $(shell which $(EMACS)),$(wildcard $(OX_GFM_DIR)/*),1)

VPATH=$(DOC_DIR)


ifeq ($(HAVE_EMACS),1)
ELCOMMON=  --directory $(OX_GFM_DIR)					\
           -q 								\
           --batch                                                      \
           --eval  "(require 'ox-ascii)"				\
           --eval "(require 'ox-gfm)"					\
           --eval "(setq org-confirm-babel-evaluate nil)"		\
           --eval "(setq default-directory \"$(realpath $(@D))\")"
%.md: %.org
	$(HR)
	$(TITLE) Build md from org
	$(TITLE)
	emacs  $<  $(ELCOMMON) --eval   "(org-gfm-export-to-markdown)"
	rm -f $*.md.tmp

%.txt: %.org
	$(HR)
	$(TITLE) Build txt from org
	$(TITLE)
	emacs  $< $(ELCOMMON) --eval       "(org-ascii-export-to-ascii)"

else

%.md: %.org
	$(HR)
	$(TITLE) edit makefile - emacs not setup
	$(MAYLOG)	touch $@
%.txt: %.org
	$(HR)
	$(TITLE) edit makefile - emacs not setup
	$(MAYLOG) touch $@
endif

######################################################################
# release:
#   first check for sanity.

.PHONY:
test: .tests_ok

.tests_ok: $(ALL_SRC_FOR_DIST)
	$(HR)
	$(TITLE) Run pytest and coverage.
	$(PYTEST)
	$(COVERAGE) lcov -q
	$(MAYLOG) touch $@
	$(TITLE) Tests passed.
	$(HR)
gitrel-part2:
	# need two parts otherwise version is wrong.
	make clean
	make
	git commit -m 'release' -a
	git tag v$(shell $(POETRY) version -s)
	git push --tag github

gitrel:
	make bump
	make gitrel-part2


gitci:
	# need new shells because version changes.
	make bump-version
	make prepare-dist
	git commit -m 'new patch' -a
	git push github
.PHONY:
bump-version:
	$(HR)
	$(TITLE) Update version numbers.
	$(TITLE) "From $(THIS_VERSION)"
	$(TITLE) "To   $(NEXT_VERSION)"
	sed -i $(SRC_DIR)/__init__.py -e 'sX^VERSION.*XVERSION = "$(NEXT_VERSION)"Xg'
	sed -i $(DOC_DIR)/readme.org -e 'sX^\*\*\* Version.*X*** Version $(NEXT_VERSION)Xg'
	$(POETRY) version $(NEXT_VERSION)
	# need in another shell because version env change.
	make prepare-dist



.PHONY:
build: clean compiled-doc lint
	$(POETRY) build 

.PHONY:
publish:dist/p2g-$(THIS_VERSION).tar.gz
	$(POETRY) publish 

.PHONY:
prepare-dist: compile test lint dist/p2g-$(THIS_VERSION).tar.gz


dist/p2g-$(THIS_VERSION).tar.gz: 
	$(HR)
	$(TITLE) Make dist
	$(TILE)
	@ # want to distribute docs, so copy
	@ # somewhere safe.
	@ rm -rf  $(SRC_DIR)/doc  $(EXAMPLE_DIR)/doc
	@ cp -a $(DOC_DIR) $(EXAMPLE_DIR) $(SRC_DIR)
	$(POETRY) build
	@ rm -rf  $(SRC_DIR)/doc $(SRC_DIR)/examples

 

######################################################################
# linty stuff
.PHONY:
pyright: $(LINTABLE_SRC)
	 $(PR)  pyright p2g 
.PHONY:
mypy: $(LINTABLE_SRC)
	 $(PR) mypy p2g 
.PHONY:
flake8: $(LINTABLE_SRC)
	 $(PR) flake8p p2g  |cat
.PHONY:
pylint: $(LINTABLE_SRC)
	 $(PR) pylint p2g 
.PHONY:
ruff: $(LINTABLE_SRC)
	 $(PR) ruff check  p2g | cat

.PHONY:
#lint: pyright mypy  flake8 pylint  ruff  deptry  pytype
lint:
	echo lint

######################################################################
# cleanup stuff

.PHONY:
isort:$(LINTABLE_SRC)
	$(PR) isort $^ 
.PHONY:
ssort:$(LINTABLE_SRC)
	$(PR) ssort  $^
.PHONY:
autoflake:$(LINTABLE_SRC)
	 $(PR) autoflake --ignore-init-module-imports  --remove-all-unused-imports  -i -v $^


cleanup: isort ssort autoflake

######################################################################


.PHONY:
clean:
	if [  $$(which p2g) ] ; then rm -f $$(which p2g); fi
	git clean -fdx
	rm -f $(COMPILED_EXAMPLES)

.PHONY:


.PHONY:
deptry:
	$(PR) deptry .



.PHONY:
pytype: $(LINTABLE_SRC)
	@# needs python < 3.11 
	@#	pytype p2g


# remove poetry and env and try from scratch
.PHONY:

TMPDIR=/tmp/p2g
ab-initio: kill-env
	rm -rf $(TMPDIR) 
	git clone hub:repos/vf3/p2g $(TMPDIR)
	make -C $(TMPDIR)


kill-env:
	pip -q uninstall -y p2g poetry
	rm -rf ~/.cache/pypoetry/cache
	rm -rf ~/.cache/pypoetry/virtualenvs
	if [  $$(which poetry) ] ; then rm -f $$(which poetry); fi
	if [  $$(which poetry) ] ; then rm -f $$(which poetry)  ; fi

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



