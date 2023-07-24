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
WRITEABLEOUT=if [ -f $@ ]  ; then chmod +w $@; fi
NON_WRITEABLEOUT=chmod -w $@


#check:
#	rm -f .deps; ../fabricate/fabricate.py make install-tools ; cat .deps



VERSION_FILE=VERSION
THIS_VERSION:=$(shell cat $(VERSION_FILE))

# all things which depend version depend on the stamp.
VERSION_STAMP:=.stamp-version-$(THIS_VERSION)
POETRY_STAMP:=.stamp-poetry
# trick because .org is self modifying
README_STAMP=.stamp-readme-$(THIS_VERSION)


# files used, should only appear once.


P2G_GEN_SRC:= p2g/haas.py
P2G_SRC:=					\
p2g/axis.py					\
p2g/builtin.py					\
p2g/coords.py					\
p2g/err.py					\
p2g/gbl.py					\
p2g/goto.py					\
p2g/__init__.py					\
p2g/__main__.py					\
p2g/main.py					\
p2g/nd.py					\
p2g/op.py					\
p2g/scalar.py					\
p2g/stat.py					\
p2g/symbol.py					\
p2g/usrlib.py					\
p2g/vector.py					\
p2g/version.py					\
p2g/walkbase.py					\
p2g/walkexpr.py					\
p2g/walkfunc.py					\
p2g/walkstat.py					\
	$(P2G_GEN_SRC)

TOOL_DIR:=tools
TOOL_SRC:=\
	tools/modversion.py  \
	tools/makestdvars.py

TEST_DIR=tests
FUNC_TEST_FILES:=					\
	tests/conftest.py				\
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
	tests/test_vector.py				\

TEST_SRC:=					\
	$(FUNC_TEST_FILES)			\
        tests/conftest.py


GENERATED_DOC:= \
	doc/haas.org			\
	doc/haas.txt			\
	doc/license.org			\
	doc/readme.txt			\
	doc/readme.md			\
	doc/readme.org			\
	readme.md				\
	license.md				\
	authors.md 

ALL_DOC:=   doc/readme.in			\
	$(GENERATED_DOC)	  

COMPILED_EXAMPLES:=examples/vicecenter.nc \
                   examples/probecalibrate.nc

EXAMPLE_SRC:= \
	examples/csearch.py			\
	examples/defs.py			\
	examples/probecalibrate.py		\
	examples/vicecenter.py 

ALL_EXAMPLES:=$(EXAMPLE_SRC) $(COMPILED_EXAMPLES)
RELEASE_FILE=dist/p2g-$(THIS_VERSION).tar.gz

ALL_GENERATED_FILES:=$(GENERATED_DOC) $(P2G_GEN_SRC) $(COMPILED_EXAMPLES)

top: | announce $(VERSION_STAMP) $(POETRY_STAMP) $(ALL_GENERATED_FILES) test lint tox release
	$(HR)
	$(TITLE) 
	$(TITLE) 

######################################################################

LINTABLE_SRC=$(P2G_SRC) $(TEST_SRC) $(TOOL_SRC)


CONTROL_FILES=Makefile pyproject.toml .scrutinizer.yml


mps:
	echo $(TEST_SRC)

.PHONY:
announce:
	@	echo "running for version " $(THIS_VERSION)




TITLE=@ echo
MAYLOG=@
HR=@echo  "********************************************************"
######################################################################

VERSIONED_FILES=p2g/__init__.py pyproject.toml doc/readme.in

#$(VERSIONED_FILES): $(VERSION_FILE)

ALL_SRC_FOR_DIST=$(CONTROL_FILES) $(COMPILED_EXAMPLES)  $(GENERATED_DOC) $(GENERATED_SRC) $(P2G_SRC) $(TEST_SRC)

IN_RELEASE= \
p2g/__init__.py					\
p2g/__main__.py					\
p2g/axis.py					\
p2g/builtin.py					\
p2g/coords.py					\
doc/authors.org				\
doc/haas.org				\
doc/haas.txt				\
doc/license.org				\
doc/readme.in				\
doc/readme.md				\
doc/readme.org				\
doc/readme.txt				\
p2g/err.py					\
examples/csearch.py				\
examples/defs.py				\
examples/probecalibrate.nc			\
examples/probecalibrate.py			\
examples/vicecenter.nc			\
examples/vicecenter.py			\
p2g/gbl.py					\
p2g/goto.py					\
p2g/haas.py					\
p2g/main.py					\
p2g/nd.py					\
p2g/op.py					\
p2g/scalar.py					\
p2g/stat.py					\
p2g/symbol.py					\
p2g/thanksto					\
p2g/usrlib.py					\
p2g/vector.py					\
p2g/version.py					\
p2g/walkbase.py					\
p2g/walkexpr.py					\
p2g/walkfunc.py					\
p2g/walkstat.py					\
pyproject.toml			\
readme.md				



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

$(VERSION_STAMP): VERSION
	$(RUN_MODVERSION) --truth VERSION --list $(VERSIONED_FILES)
	touch $@

.PHONY:
install-poetry:
	$(HR)
	$(TITLE) Install poetry
	curl -sSL https://install.python-poetry.org | python3

.stamp-poetry: 
	$(HR)
	$(MAYLOG) if [ ! $$(which poetry) ] ; then make install-poetry ; fi
	$(MAYLOG) 	touch $@
	$(TITLE)
	$(TITLE) Poetry installed in $$(which poetry)
	$(POETRY) install
	$(POETRY) update
	$(POETRY) export > requirements.txt
	$(MAYLOG) touch $@

######################################################################
# examples

%.nc:%.py  $(P2G_SRC) 
	$(RUN_P2G) $<  $@

######################################################################
# machine generated code

p2g/haas.py: tools/makestdvars.py
	$(WRITEABLEOUT)
	$(RUN_MAKESTDVARS)  --py=$@ 
	$(NON_WRITEABLEOUT)
doc/haas.txt: tools/makestdvars.py
	$(WRITEABLEOUT)
	$(RUN_MAKESTDVARS)  --txt=$@ 
	$(NON_WRITEABLEOUT)

doc/haas.org: $(TOOL_DIR)/makestdvars.py
	$(WRITEABLEOUT)
	$(RUN_MAKESTDVARS)  --org=$@ 
	$(NON_WRITEABLEOUT)
######################################################################
#
# doc
#
# emacs may not be installed, so after running with -, touch the
# output,  so next make stage will run using existing output files.


WRITE_RESULT= --eval '(write-region (point-min) (point-max) "$(abspath $@)")'
# witout this evals won't eval, so speed things up.
DO_EVAL'=--eval "(require 'ob-python)"	'


ELCOMMON=						\
        --directory $(OX_GFM_DIR)			\
	-nsl -q --batch					\
	--eval "(org-mode)"				\
        --eval "(require 'ox-gfm)"			\
	--eval "(setq org-confirm-babel-evaluate nil)"		

%.md:%.org
	$(WRITEABLEOUT)
	- $(EMACS) $< $(ELCOMMON) -f org-gfm-export-as-markdown $(WRITE_RESULT)
	# fix the initial table of contents.
	$(PR) python tools/repairmd.py --src $@ --dst $@
	rm -f $@.tmp
	$(NON_WRITEABLEOUT)

%.md:doc/%.md
	$(WRITEABLEOUT)
	cp $< $@
	$(NON_WRITEABLEOUT)

%.org:%.in $(VERSION_FILE)
	$(WRITEABLEOUT)
	- $(EMACS) $< $(ELCOMMON) $(DO_EVAL) $(WRITE_RESULT)
	touch $@
	$(NON_WRITEABLEOUT)

%.txt: %.org
	$(WRITEABLEOUT)
	-  $(EMACS) $< $(ELCOMMON) -f org-ascii-export-as-ascii $(WRITE_RESULT)
	$(NON_WRITEABLEOUT)


######################################################################
# release:
#   first check for sanity.

sanity:

.PHONY:


.PHONY:
test: .stamp-tests

.stamp-tests:  $(POETRY_STAMP) $(P2G_SRC) $(TEST_SRC)
	$(HR)
	$(TITLE) Run pytest and coverage.
	PYTHONPATH=. COLUMNS=80 $(PYTEST) 
	$(COVERAGE) lcov -q
	$(MAYLOG) touch $@
	$(TITLE) Tests passed.
	$(HR)

sometest:
	poetry run pytest -x --lf
T=local
packup:
	git commit -m --allow-empty -m "rel v$(THIS_VERSION)" -a
	git tag -a v$(THIS_VERSION) -m v$(THIS_VERSION)
	git push $(T)
	git push --tags $(T)



foop:
	echo $(THIS_VERSION)

tohub:
	git commit --allow-empty -m v$(THIS_VERSION)
	git tag  v$(THIS_VERSION)
	git push
	git push --tags
git-push:
	make bump-version
	make gitrel-push-part2


gitci:
	# need new shells because version changes.
	make bump-version
	make prepare-dist
	git commit -m 'new patch' -a
	git push github

bump-version: .bump-version



#	python	$(MODVERSION) --report $(VERSIONED_FILES) --bump
.bump-version:
	$(HR)
	$(TITLE) Update version numbers.
	$(TITLE) "From $(THIS_VERSION)"

	echo "NEW $(THIS_VERSION)"> .version_bumped
	python	$(MODVERSION) --report $(VERSIONED_FILES) --bump

	# need in another shell because version env change.
	git checkout main
	git pull
	git tag $(NEXT_TAG)
	git push local 
        # git push upstream MAJOR.{MINOR+1}.0.dev0

# 1=hub:repos/vf3/p2gxshe 

# R2=github:0x5ac/p2g
# .stamp-git:
# 	if [ "$(shell hostname -d)" = "steveopolis.com" ] ; then	\
# 	   grep -q $(R1) .git/config || git remote add local $(R1); \
# 	   grep -q $(R2) .git/config || git remote add remote $(R2); \
# 	fi							 
# 	touch $@



#.PHONY:
#publish:$(RELEASE_FILE)
#	$(POETRY) publish 

# .PHONY:
# prepare-dist: $(ALL_SRC_FOR_DIST) test lint dist/p2g-$(THIS_VERSION).tar.gz


diff:
	echo $(IN_RELEASE) | xargs -n 1 | sort >want
	echo $(ALL_EXAMPLES) $(CONTROL_FILES) $(ALL_DOC) $(P2G_SRC) | xargs -n 1 | sort > got
	sdiff want got

$(RELEASE_FILE): $(IN_RELEASE)
	$(HR)
	$(TITLE) Make dist
	$(TILE)
	# want to distribute docs and examples, so copy
	# into src tree
	rm -rf  p2g/doc
	rm -rf  p2g/examples

	cp -a doc p2g
	cp -a  examples p2g
	$(POETRY) build
	rm -rf  p2g/doc p2g/examples


.PHONY:
tox: .stamp-tox

.stamp-tox:$(RELEASE_FILE)
	$(PR)	tox --installpkg $(RELEASE_FILE)
	touch $@

release: | $(RELEASE_FILE) tox

# ######################################################################
# # linty stuff

.PHONY:
vulture:.stamp-vulture

.stamp-vulture: $(POETRY_STAMP) | $(LINTABLE_SRC)
	 $(PR) vulture
	touch $@

.PHONY:
pyright:.stamp-pyright

.stamp-pyright: $(POETRY_STAMP) | $(LINTABLE_SRC)
	 $(PR) pyright
	touch $@
.PHONY:
mypy:.stamp-mypy

.stamp-mypy: $(POETRY_STAMP) |  $(LINTABLE_SRC)
	 $(PR) mypy
	touch $@
.PHONY: 
flake8:.stamp-flake8

.stamp-flake8: $(POETRY_STAMP) | $(LINTABLE_SRC)
	$(PR) flake8p
	touch $@

.PHONY:
pylint:.stamp-pylint

.stamp-pylint: $(POETRY_STAMP) | $(LINTABLE_SRC)
	 $(PR) pylint tools p2g
	touch $@
.PHONY:
ruff:.stamp-ruff

.stamp-ruff: $(POETRY_STAMP) | $(LINTABLE_SRC)
	$(PR) ruff check tools p2g
	touch $@

.PHONY:
deptry:.stamp-deptry

.stamp-deptry: 
	$(PR) deptry .
	touch $@
.PHONY:
pytype:.stamp-pytype

.stamp-pytype: $(POETRY_STAMP) | $(LINTABLE_SRC)
	@# needs python < 3.11
	touch $@
	@#	pytype p2g


.PHONY:
lint: pyright mypy pytype pylint vulture ruff   flake8

# ######################################################################
# cleanup stuff

.PHONY:
isort:$(LINTABLE_SRC)
	$(PR) isort $^ 

.PHONY:
ssort:$(LINTABLE_SRC)
	-	$(PR) ssort  $^

.PHONY:
autopep8:$(LINTABLE_SRC)
	$(PR) autopep8 --in-place $^

.PHONY:
black:$(LINTABLE_SRC)
	$(PR) black $^

.PHONY:
autoflake:$(LINTABLE_SRC)
	 $(PR) autoflake --ignore-init-module-imports  --remove-all-unused-imports  -i -v $^


.PHONY:
cleanup: isort ssort  black

# ######################################################################
# utils


.PHONY:
force-version:
	$(RUN_MODVERSION) $(VERSIONED_FILES) --git --report --inplace
# .PHONY:
clean:
	if [  $$(which p2g) ] ; then rm -f $$(which p2g); fi
	git clean -fdx


# # remove poetry and env and try from scratch
# .PHONY:
# TMPDIR=/tmp/p2g
# ab-initio: kill-env
# 	rm -rf $(TMPDIR) 
# 	git clone hub:repos/vf3/p2g $(TMPDIR)
# 	make -C $(TMPDIR)


# kill-env:
# 	pip -q uninstall -y p2g poetry
# 	rm -rf ~/.cache/pypoetry/cache
# 	rm -rf ~/.cache/pypoetry/virtualenvs
# 	if [  $$(which poetry) ] ; then rm -f $$(which poetry); fi
# 	if [  $$(which poetry) ] ; then rm -f $$(which poetry)  ; fi

# # Build my wips
# mall:
# 	 sed 'sXfrom.*import \(.*\)X"\1\",Xg' p2g/__init__.py
# verbose:
# 	poetry run pytest tests/test_vars.py  -vvvv --capture=tee-sys
# .PHONY:
# sf:
# 	 python 	/home/sac/w/nih/snakefood/main.py . p2g

DSTDIR=/home/sac/vf3/_nc_


# .PRECIOUS:  vicecenter.ncwide probecalibrate.ncwide

# off-wip:  vicecenter.diff probecalibrate.diff
wip:  vicecenter.diff .mark-vicecenter

.PHONY:
wip-probe: probecalibrate.diff
.PHONY:
wip-vicecenter: vicecenter.diff 


MAKEONE=poetry run p2g 

# %.diff: examples/%.nc
# 	@	touch -f $<.old
# 	-	diff $<  $<.old > $@
# 	cat $@
# 	@	cp $< $<.old

#.mark-%: $(EXAMPLE_DIR)/%.py $(EXAMPLE_DIR)/defs.py
#	poetry run p2g  $<   tmp.nc
#	poetry run p2g  $< --narrow  $(DSTDIR)/{countdown}-pc.nc 
# 

.PHONY:
$(DSTDIR)/ZZ%.nc: %.py
	poetry run p2g $<  --wide $@
	poetry run p2g $< --wide  $(DSTDIR)/{countdown}-pc.nc 
	touch $@

# wip-probe: .mark-probecalibrate



goldify-test_examples: 
	cp tests/golden/vicecenter_vicecenter.got tests/golden/vicecenter_vicecenter.nc
	cp tests/golden/probecalibrate_probecalibrate.got tests/golden/probecalibrate_probecalibrate.nc

goldify-%: tests/%.py
	echo "RUNNING " $*
	sed '/^# TESTS BELOW/q' tests/$*.py > t1
	- cat tests/golden/$** >> t1
	cp t1 tests/$*.py
	autopep8 -i   tests/$*.py



# p:
# 	prospector p2g --tool bandit --tool dodgy --tool mccabe --tool mypy --tool profile-validator --tool  pycodestyle --tool pydocstyle --tool pyflakes --tool pylint --tool pyright --tool pyroma --tool vulture

# t:
# 	COLUMNS=80 poetry run pytest  -vv --no-header --tb=short

# t11:
# 	PYTHONPATH=. pytest   -c z tests/test_vars.py -vv --no-header --tb=short  --strict-config


# small:
# 	poetry run pytest -c z tests/test_for.py
# 	echo "DONE"

# debt:
# #	PYTHONPATH=. pytest   -c z tests/test_comment.py -vv --no-header --tb=short  --strict-config  --pdb
# 	cd tests;	exec poetry run  python3 ~/scripts/sacpdb.py --command=c -m p2g    gen t.py -

# bp:
# 	echo hi
# 	echo $(THIS_VERSION)

ci:
	git commit -m 'wip' -a
	git push local


# localclean:
# 	poetry env list | sed "s:(Activated)::g" | xargs poetry env remove
# 	rm -f $$(which poetry)

# lint:	pytype pylint vulture ruff   flake8

# ls:
# 	ls -lt --full doc

sacpdb:
	python -m p2g t.py --break --emit-rtl



st:
	 poetry run pytest tests/test_rtl.py
