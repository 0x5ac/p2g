

PATH=$(HOME)/.local/bin:/usr/bin
export TERM:=dumb
export NO_COLOR:=true
EMACS:=emacs
POETRY:=poetry
PR:=$(POETRY) run
RUN_P2G:=$(PR) p2g
RUN_MODVERSION:=$(PR) python tools/modversion.py
RUN_MAKESTDVARS:=$(PR) python tools/makestdvars.py
COVERAGE:=$(PR) coverage
PYTEST:=$(PR) pytest
OX_GFM_DIR=~/.emacs.d/straight/build/ox-gfm

# used to bracket machine generated files
# so I don't mod them by accident.
#RITEABLEOUT=if [ -f $@ ]  ; then chmod +w $@; fi
#NON_WRITEABLEOUT=chmod -w $@

VERSION_FILE=VERSION
THIS_VERSION:=$(shell cat $(VERSION_FILE))
THIS_TAG:=v$(THIS_VERSION)
# all things which depend version depend on the stamp.
VERSION_STAMP:=.stamp-version-$(THIS_VERSION)
POETRY_STAMP:=.stamp-poetry
# trick because .org is self modifying
README_STAMP=.stamp-readme-$(THIS_VERSION)


# files used, should only appear once.


P2G_GEN_SRC:= p2g/haas.py
ALL_P2G_SRC:=					\
	 p2g/axis.py				\
	 p2g/builtin.py				\
	 p2g/coords.py				\
	 p2g/err.py				\
	 p2g/gbl.py				\
	 p2g/goto.py				\
	 p2g/__init__.py			\
	 p2g/__main__.py			\
	 p2g/main.py				\
	 p2g/nd.py				\
	 p2g/op.py				\
	 p2g/scalar.py				\
	 p2g/stat.py				\
	 p2g/symbol.py				\
	 p2g/usrlib.py				\
	 p2g/vector.py				\
	 p2g/version.py				\
	 p2g/walkbase.py			\
	 p2g/walkexpr.py			\
	 p2g/walkfunc.py			\
	 p2g/walkstat.py			\
	$(P2G_GEN_SRC)

TOOL_DIR:=tools
TOOL_SRC:=\
	tools/modversion.py  \
	tools/makestdvars.py

TEST_DIR=tests
FUNC_TEST_FILES:=					\
	tests/test_assert.py				\
	tests/test_axes.py				\
	tests/test_badpytest.py				\
	tests/test_basic.py				\
	tests/test_builtins.py				\
	tests/test_comment.py				\
	tests/test_coords.py				\
	tests/test_edge.py				\
	tests/test_error.py				\
	tests/test_examples.py				\
	tests/test_expr.py				\
	tests/test_for.py				\
	tests/test_func.py				\
	tests/test_goto.py				\
	tests/test_interp.py				\
	tests/test_lib.py				\
	tests/test_linenos.py				\
	tests/test_main.py				\
	tests/test_makestdvars.py			\
	tests/test_meta.py				\
	tests/test_nt1.py				\
	tests/test_op.py				\
	tests/test_rtl.py				\
	tests/test_smoke.py				\
	tests/test_starimport.py			\
	tests/test_str.py				\
	tests/test_symtab.py				\
	tests/test_tuple.py				\
	tests/test_vars.py				\
	tests/test_vector.py

ALL_TEST_SRC:=					\
	$(FUNC_TEST_FILES)			\
	tests/conftest.py


GENERATED_DOC:=					\
	doc/haas.org				\
	doc/haas.txt				\
	doc/readme.txt				\
	doc/readme.md				\
	doc/readme.org				\
	readme.md				\
	license.org				\
	authors.org

ALL_DOC:=   doc/readme.in			\
            doc/thanksto.txt                    \
	    doc/license.org			\
	    doc/authors.org			\
	$(GENERATED_DOC)

COMPILED_EXAMPLES:=examples/vicecenter.nc	\
		   examples/probecalibrate.nc

EXAMPLE_SRC:=					\
	examples/csearch.py			\
	examples/defs.py			\
	examples/probecalibrate.py		\
	examples/vicecenter.py

ALL_EXAMPLES:=$(EXAMPLE_SRC) $(COMPILED_EXAMPLES)
DIST_FILE=dist/p2g-$(THIS_VERSION).tar.gz

ALL_GENERATED_FILES:=$(GENERATED_DOC) $(P2G_GEN_SRC) $(COMPILED_EXAMPLES)


top:  announce					\
      $(POETRY_STAMP)				\
      $(VERSION_STAMP)				\
      $(ALL_GENERATED_FILES)			\
      test					\
      lint					\
      $(DIST_FILE) 
finally: \
     sanity

release: sanity
######################################################################


ALL_PY=$(ALL_P2G_SRC) $(TOOL_SRC) $(ALL_TEST_SRC)
LINTABLE_SRC=$(ALL_P2G_SRC) $(TOOL_SRC)
CONTROL_FILES=Makefile pyproject.toml .scrutinizer.yml


mps:
	echo $(ALL_TEST_SRC)

.PHONY:
announce:
	@	echo "running for version " $(THIS_VERSION)




TITLE=@ echo
MAYLOG=@
HR=@echo  "********************************************************"
######################################################################

VERSIONED_FILES=p2g/__init__.py pyproject.toml doc/readme.in

IN_DIST:=$(ALL_EXAMPLES)  $(ALL_DOC) $(ALL_P2G_SRC)

######################################################################
# convenience rules, for maintenance only
#
.PHONY:
examples: $(COMPILED_EXAMPLES)
doc:  $(GENERATED_DOC)
version-update: $(VERSION_STAMP)
poetry: $(POETRY_STAMP)

######################################################################
######################################################################
# Init environment

$(VERSION_STAMP): VERSION $(POETRY_STAMP)
	$(RUN_MODVERSION) --truth VERSION --list $(VERSIONED_FILES)
	touch $@


$(POETRY_STAMP):
	$(HR)
	if [ ! $(shell which poetry) ] ; then \
	   curl -sSL https://install.python-poetry.org | python3 ; \
	fi
	type poetry
	$(TITLE)
	$(TITLE) Poetry installed in $$(which poetry)
	$(POETRY) install
	$(POETRY) update
	$(POETRY) export > requirements.txt
	$(MAYLOG) touch $@

######################################################################
# examples

%.nc:%.py  $(ALL_P2G_SRC)
	$(RUN_P2G) $<  $@

######################################################################
# machine generated code

p2g/haas.py: tools/makestdvars.py $(POETRY_STAMP)
	$(WRITEABLEOUT)
	$(RUN_MAKESTDVARS)  --py=$@
	$(NON_WRITEABLEOUT)
doc/haas.txt: tools/makestdvars.py $(POETRY_STAMP)
	$(WRITEABLEOUT)
	$(RUN_MAKESTDVARS)  --txt=$@
	$(NON_WRITEABLEOUT)

doc/haas.org: $(TOOL_DIR)/makestdvars.py $(POETRY_STAMP)
	$(WRITEABLEOUT)
	$(RUN_MAKESTDVARS)  --org=$@
	$(NON_WRITEABLEOUT)
######################################################################
#
# doc
#
# emacs may not be installed, so after running with -, touch the
# output,  so next make stage will run using existing output files.



ELCOMMON=					\
	--directory $(OX_GFM_DIR)		\
        --chdir /tmp \
	-q --batch				\
	--load $(abspath tools/org-to-x.el)	\
         $(abspath $<)

%.md:%.org
	$(WRITEABLEOUT)
	- $(EMACS) $(ELCOMMON) --eval '(to-markdown "$(abspath $@)")'
	# fix the initial table of contents.
	$(PR) python tools/repairmd.py --src $@ --dst $@
	rm -f $@.tmp
	$(NON_WRITEABLEOUT)

%.txt: %.org
	$(WRITEABLEOUT)
	-  $(EMACS) $(ELCOMMON)  --eval '(to-txt "$(abspath $@)")' 
	$(NON_WRITEABLEOUT)

%.md:doc/%.md
	$(WRITEABLEOUT)
	cp $< $@
	$(NON_WRITEABLEOUT)

%.org:doc/%.org
	$(WRITEABLEOUT)
	cp $< $@
	$(NON_WRITEABLEOUT)

%.org:%.in $(VERSION_FILE)
	$(WRITEABLEOUT)
	-  $(EMACS) $(ELCOMMON)   --eval '(to-org "$(abspath $@)")'
	# refill in from generated, touch so stamps are ok
	cp $@ $<
	touch $@
	$(NON_WRITEABLEOUT)


#######################################################################
# lints

.PHONY:
vulture:.stamp-vulture

.stamp-vulture:  $(LINTABLE_SRC)
	 $(PR) vulture $(LINTABLE_SRC)
	touch $@
##########
.PHONY:
pyright:.stamp-pyright

.stamp-pyright:   $(LINTABLE_SRC)
	 $(PR) pyright $(LINTABLE_SRC)
	touch $@
##########
.PHONY:
mypy:.stamp-mypy

.stamp-mypy:    $(LINTABLE_SRC)
	 $(PR) mypy $(LINTABLE_SRC)
	touch $@
##########
.PHONY:
flake8:.stamp-flake8

.stamp-flake8:   $(LINTABLE_SRC)
	$(PR) flake8p $(LINTABLE_SRC)
	touch $@
##########
.PHONY:
pylint:.stamp-pylint

.stamp-pylint:   $(LINTABLE_SRC)
	 $(PR) pylint $(LINTABLE_SRC)
	touch $@
##########
.PHONY:
ruff:.stamp-ruff

.stamp-ruff:   $(LINTABLE_SRC)
	$(PR) ruff check $(LINTABLE_SRC)
	touch $@
##########
.PHONY:
deptry:.stamp-deptry

.stamp-deptry:
	$(PR) deptry .
	touch $@
##########
.PHONY:
pytype:.stamp-pytype

.stamp-pytype:   $(LINTABLE_SRC)
	@# needs python < 3.11
	touch $@
	@#	pytype p2g $(LINTABLE_SRC)
##########
.PHONY:
lint: pyright mypy pytype pylint vulture ruff   flake8


######################################################################
# Tests

test: .stamp-tests

.stamp-tests:  $(ALL_P2G_SRC) $(ALL_TEST_SRC)
	$(HR)
	$(TITLE) Run pytest and coverage.
	PYTHONPATH=. COLUMNS=80 $(PYTEST)
	$(COVERAGE) lcov -q
	$(MAYLOG) touch $@
	$(TITLE) Tests passed.
	$(HR)


######################################################################
# make a release : build the distribution .tar for pip
# test it for sanity


# want to distribute docs and examples, so copy
# into src tree

$(DIST_FILE): $(IN_DIST)
	$(HR)
	$(TITLE) Make dist
	rm -rf  p2g/doc
	rm -rf  p2g/examples
	cp -a doc p2g
	cp -a examples p2g
	$(POETRY) build
	rm -rf  p2g/doc p2g/examples

######################################################################$
sanity:  .stamp-sanity

.stamp-sanity: $(DIST_FILE) .stamp_all_there .stamp-tox
	touch $@

# make sure everything in dist is in makefile and viceversa.

# -rwxr-xr-x 0/0            9790 2023-07-22 22:06 p2g-0.2.220/p2g/walkstat.py
# dist with doc in top/p2g/doc, but in the tree as top/doc etc.
# so remove up to /p2g/
# move doc and examples
# remove junk file

.stamp_all_there: $(IN_DIST) $(DIST_FILE)
	tar tzvf $(DIST_FILE)					\
         | sed -E 'sX.*[0-9][0-9]:[[:digit:]]{2} [^/]+/XXg'	\
         | sed -E "s:p2g/(doc|examples):\\1:g"			\
         | grep -v PKG-INFO | sort > .found-in-dist		
	echo $(IN_DIST) | xargs -n 1 | sort > .release-deps	
	sdiff .found-in-dist .release-deps | tee $@


##########
.PHONY:

.stamp-tox:$(DIST_FILE)
	$(PR)	tox --installpkg $(DIST_FILE)
	touch $@

##########
togithub:
	git commit --allow-empty -m v$(THIS_VERSION) -a
	- git tag --delete v$(THIS_VERSION)
	git tag  v$(THIS_VERSION)
	git push $(T)
	git push --tags $(T) --force

######################################################################
# cleanup stuff
##########
.PHONY:
isort:$(LINTABLE_SRC)
	$(PR) isort $^
##########
.PHONY:
ssort:$(LINTABLE_SRC)
	-	$(PR) ssort  $^
##########
.PHONY:
autopep8:$(LINTABLE_SRC)
	$(PR) autopep8 --in-place $^
##########
.PHONY:
black:$(LINTABLE_SRC)
	$(PR) black $^
##########
.PHONY:
autoflake:$(LINTABLE_SRC)
	 $(PR) autoflake --ignore-init-module-imports  --remove-all-unused-imports  -i -v $^
##########
.PHONY:
cleanup: isort ssort  black
######################################################################
# utils
.PHONY:
clean:
	if [  $$(which p2g) ] ; then rm -f $$(which p2g); fi
	git clean -fdx

######################################################################
# for my machine.

DSTDIR=/home/sac/vf3/_nc_

# off-wip:  vicecenter.diff probecalibrate.diff
wip:  vicecenter.diff .mark-vicecenter

.PHONY:
wip-probe: probecalibrate.diff
.PHONY:
wip-vicecenter: vicecenter.diff

MAKEONE=poetry run p2g

# %.diff: examples/%.nc
#	@	touch -f $<.old
#	-	diff $<  $<.old > $@
#	cat $@
#	@	cp $< $<.old

#.mark-%: $(EXAMPLE_DIR)/%.py $(EXAMPLE_DIR)/defs.py
#	poetry run p2g  $<   tmp.nc
#	poetry run p2g  $< --narrow  $(DSTDIR)/{countdown}-pc.nc
#


gif-examples:
	-	$(PR) pytest tests/test_examples.py --gif
	cp tests/golden/vicecenter_vicecenter.got tests/golden/vicecenter_vicecenter.nc
	cp tests/golden/probecalibrate_probecalibrate.got tests/golden/probecalibrate_probecalibrate.nc


gif-%: tests/test_%.py
	- $(PR) pytest tests/test_$*.py --gif
	sed '/^# TESTS BELOW/q' $< > t1
	- cat tests/golden/test_$*_* >> t1
	cp t1 $<
	autopep8 -i   $<

# p:
#	prospector p2g --tool bandit --tool dodgy --tool mccabe --tool mypy --tool profile-validator --tool  pycodestyle --tool pydocstyle --tool pyflakes --tool pylint --tool pyright --tool pyroma --tool vulture

# t:
#	COLUMNS=80 poetry run pytest  -vv --no-header --tb=short

# t11:
#	PYTHONPATH=. pytest   -c z tests/test_vars.py -vv --no-header --tb=short  --strict-config


# small:
#	poetry run pytest -c z tests/test_for.py
#	echo "DONE"

# debt:
# #	PYTHONPATH=. pytest   -c z tests/test_comment.py -vv --no-header --tb=short  --strict-config  --pdb
#	cd tests;	exec poetry run  python3 ~/scripts/sacpdb.py --command=c -m p2g    gen t.py -

# bp:
#	echo hi
#	echo $(THIS_VERSION)

ci:
	git commit -m 'wip' -a
	git push local


# localclean:
#	poetry env list | sed "s:(Activated)::g" | xargs poetry env remove
#	rm -f $$(which poetry)

# lint:	pytype pylint vulture ruff   flake8

# ls:
#	ls -lt --full doc

sacpdb:
	python -m p2g t.py --break --emit-rtl



st:
	 poetry run pytest tests/test_coords.py
