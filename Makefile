top: | announce install-tools  check-version generate test lint release
	$(HR)
	$(TITLE) 
	$(TITLE) 

PATH=$(HOME)/.local/bin:/usr/bin
export TERM:=dumb
export NO_COLOR:=true
P2G_SRC_DIR:=./p2g
TOOL_DIR:=./tools
DOC_DIR:=./doc
EXAMPLE_DIR=./examples
TEST_DIR=./tests
EMACS?=emacs
POETRY=poetry
PR:=$(POETRY) run
P2G_SCRIPT:=$(POETRY) run p2g
VERSION_SCRIPT:=tools/modversion.py
MAKE_STDVARS:=tools/makestdvars.py
RUN_VERSION_SCRIPT:= python $(VERSION_SCRIPT)
RUN_MAKESTDVARS:= python $(MAKE_STDVARS)
COVERAGE:=$(PR) coverage
PYTEST:=$(PR) pytest
OX_GFM_DIR=~/.emacs.d/straight/build/ox-gfm


TITLE=@ echo
MAYLOG=@
HR=@echo  "********************************************************"
######################################################################

GENERATED_SRC=$(P2G_SRC_DIR)/haas.py

TOOL_SRC=$(TOOL_DIR)/modversion.py     $(TOOL_DIR)/makestdvars.py		


P2G_SRC:= \
    $(P2G_SRC_DIR)/__init__.py			\
    $(P2G_SRC_DIR)/__main__.py			\
    $(P2G_SRC_DIR)/axis.py			\
    $(P2G_SRC_DIR)/coords.py			\
    $(P2G_SRC_DIR)/err.py			\
    $(P2G_SRC_DIR)/gbl.py			\
    $(P2G_SRC_DIR)/goto.py			\
    $(P2G_SRC_DIR)/usrlib.py			\
    $(P2G_SRC_DIR)/main.py			\
    $(P2G_SRC_DIR)/nd.py			\
    $(P2G_SRC_DIR)/op.py			\
    $(P2G_SRC_DIR)/scalar.py			\
    $(P2G_SRC_DIR)/stat.py			\
    $(P2G_SRC_DIR)/symbol.py			\
    $(P2G_SRC_DIR)/vector.py			\
    $(P2G_SRC_DIR)/walkbase.py			\
    $(P2G_SRC_DIR)/walkexpr.py			\
    $(P2G_SRC_DIR)/walkfunc.py			\
    $(P2G_SRC_DIR)/walkstat.py                  \
    $(GENERATED_SRC)

TEST_NAMES:=$(notdir $(basename $(wildcard $(TEST_DIR)/test*.py))) 

TEST_SRC:=$(TEST_DIR)/conftest.py \
         $(addprefix $(TEST_DIR)/,$(addsuffix .py,$(TEST_NAMES)))


VERSIONED_FILES:=$(P2G_SRC_DIR)/__init__.py pyproject.toml $(DOC_DIR)/readme.org


THIS_VERSION:=$(shell $(RUN_VERSION_SCRIPT) $(VERSIONED_FILES) --git --show )
VSTAMP:=.stamp-$(THIS_VERSION)

.PHONY:
announce: $(VSTAMP)
	echo "running for version " $(THIS_VERSION) $(VSTAMP)

fish:
	echo $(THIS_VERSION)
RELEASE_FILE=dist/p2g-$(THIS_VERSION).tar.gz

LINTABLE_SRC=$(P2G_SRC) $(GENERATED_SRC) $(TEST_SRC) $(TOOL_SRC)

COMPILED_EXAMPLES=$(EXAMPLE_DIR)/vicecenter.nc \
                  $(EXAMPLE_DIR)/probecalibrate.nc

GENERATED_DOC=\
	$(DOC_DIR)/haas.org				\
	$(DOC_DIR)/haas.txt				\
	$(DOC_DIR)/readme.txt				\
	$(DOC_DIR)/readme.md				\
	$(DOC_DIR)/readme.org				\
	readme.md \
	license.md					\
	authors.md \
	.stamp-readme.org  # used to rebuild readme.org which updates self.

CONTROL_FILES=Makefile pyproject.toml .scrutinizer.yml 

ALL_SRC_FOR_DIST=$(CONTROL_FILES) $(COMPILED_EXAMPLES)  $(GENERATED_DOC) $(GENERATED_SRC) $(P2G_SRC) $(TEST_SRC)


# make sure version number is correct by checking that there's
# stamp file with the same as the version we want. If not then
# update the relvant sources.
check-version: $(VSTAMP)

$(VSTAMP):
	$(RUN_VERSION_SCRIPT) --inplace --git $(VERSIONED_FILES)
	$(RUN_VERSION_SCRIPT) --report $(VERSIONED_FILES)
	touch $@

######################################################################
# Generate intermediates
generate: $(COMPILED_EXAMPLES)  $(GENERATED_SRC) $(GENERATED_DOC)
######################################################################
# Init environment


.PHONY:
install-tools: .stamp-poetry .stamp-deps .stamp-git


.stamp-deps:
	$(HR)
	$(TITLE)
	$(TITLE)  Install dependencies.
	$(POETRY)  install;
	$(POETRY)  update
	$(MAYLOG) touch $@


.PHONY:
install-poetry:
	$(HR)
	$(TITLE)
	$(TITLE) Install poetry using pip.
	curl -sSL https://install.python-poetry.org | python3
# -	python -m pip install --upgrade pip
# 	python -m pip install -q --force-reinstall --user --upgrade poetry
# 	python -m pip install -q --force-reinstall --user --upgrade tox


.stamp-poetry: readme.md
	$(HR)
	$(MAYLOG) if [ ! $$(which poetry) ] ; then make install-poetry ; fi
	$(MAYLOG) 	touch $@
	$(TITLE)
	$(TITLE) Poetry installed in $$(which poetry)


######################################################################
# examples
.PHONY:
examples: $(COMPILED_EXAMPLES)  

%.nc:%.py  $(P2G_SRC) $(VSTAMP) examples/*.py
	$(P2G_SCRIPT) $<  $@

######################################################################
# Doc and machine generated headers.

doc: $(GENERATED_DOC)

$(P2G_SRC_DIR)/haas.py: $(TOOL_DIR)/makestdvars.py 
	$(RUN_MAKESTDVARS)  --py=$@ 

$(DOC_DIR)/haas.txt: $(TOOL_DIR)/makestdvars.py
	echo 	$(RUN_MAKESTDVARS)  --txt=$@ 
	$(RUN_MAKESTDVARS)  --txt=$@ 

$(DOC_DIR)/haas.org: $(TOOL_DIR)/makestdvars.py 
	$(RUN_MAKESTDVARS)  --org=$@ 

# emacs may not be installed, so after running with -, touch the output.
# so next make stage will run using existing output files.


WRITE_RESULT= --eval '(write-region (point-min) (point-max) "$(@F)")'

# witout this evals won't eval, so speed things up.
DO_EVAL'=--eval "(require 'ob-python)"	'

ELCOMMON=						\
        --directory $(OX_GFM_DIR)			\
	-q --batch					\
        --chdir doc $(<F)				\
	--eval "(org-mode)"				\
        --eval "(require 'ox-gfm)"			\
	--eval "(setq org-confirm-babel-evaluate nil)"		

.stamp-readme.org: doc/readme.org  doc/haas.org $(VSTAMP)
	- emacs   $(ELCOMMON) $(DO_EVAL) $(WRITE_RESULT)
	touch $@

VERSIONED_FILES: $(VSTAMP)
.PRECIOUS: .stamp-%.md
doc/readme.md: .stamp-readme.org $(VSTAMP)
	$(HR)
	$(TITLE) Build md from org
	$(TITLE)
	- emacs $(ELCOMMON) -f org-gfm-export-as-markdown $(WRITE_RESULT)
	# fix the initial table of contents.
	- grep -q -- "---"  $@ &&  sed -i '/^---/,$$!d' $@
	rm -f readme.md.tmp 
	touch $@

doc/%.md:doc/%.org
	- emacs $(ELCOMMON) -f org-gfm-export-as-markdown $(WRITE_RESULT)

# .PRECIOUS: .stamp-%.txt
# doc/%.txt: .stamp-%.txt
# 	touch $@

doc/%.txt: doc/%.org $(VSTAMP)
	$(HR)
	$(TITLE) Build txt from org
	$(TITLE)
	-  emacs  $(ELCOMMON) -f org-ascii-export-as-ascii $(WRITE_RESULT)
	touch $@

%.md:doc/%.md
	cp $< $@


######################################################################
# release:
#   first check for sanity.

sanity:

.PHONY:


.PHONY:
test: .tests_ok

.tests_ok: install-tools $(ALL_SRC_FOR_DIST)

	$(HR)
	$(TITLE) Run pytest and coverage.
	PYTHONPATH=. COLUMNS=80 $(PYTEST) 
	$(COVERAGE) lcov -q
	$(MAYLOG) touch $@
	$(TITLE) Tests passed.
	$(HR)

sometest:
	poetry run pytest -x --lf

gitrel-push-part2:
	# need two parts otherwise version is wrong.
	make
	git commit -m 'bump' -a

	git push origin HEAD 
	git push github

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



#	python	$(VERSION_SCRIPT) --report $(VERSIONED_FILES) --bump
.bump-version:
	$(HR)
	$(TITLE) Update version numbers.
	$(TITLE) "From $(THIS_VERSION)"

	echo "NEW $(THIS_VERSION)"> .version_bumped
	python	$(VERSION_SCRIPT) --report $(VERSIONED_FILES) --bump

	# need in another shell because version env change.
	git checkout main
	git pull
	git tag $(NEXT_TAG)
	git push local 
        # git push upstream MAJOR.{MINOR+1}.0.dev0

1=hub:repos/vf3/p2gxshe 

R2=github:0x5ac/p2g
.stamp-git:
	if [ "$(shell hostname -d)" = "steveopolis.com" ] ; then	\
	   grep -q $(R1) .git/config || git remote add local $(R1); \
	   grep -q $(R2) .git/config || git remote add remote $(R2); \
	fi							 
	touch $@


.PHONY:
compiled-doc: $(COMPILED-DOC)

.PHONY:
build: clean compiled-doc lint
	$(POETRY) build 

#.PHONY:
#publish:$(RELEASE_FILE)
#	$(POETRY) publish 

# .PHONY:
# prepare-dist: $(ALL_SRC_FOR_DIST) test lint dist/p2g-$(THIS_VERSION).tar.gz


$(RELEASE_FILE):
	$(HR)
	$(TITLE) Make dist
	$(TILE)
	# want to distribute docs and examples, so copy
	# into src tree
	rm -rf  $(P2G_SRC_DIR)/doc
	rm -rf  $(P2G_SRC_DIR)/examples

	cp -a $(DOC_DIR) $(P2G_SRC_DIR)
	cp -a  $(EXAMPLE_DIR) $(P2G_SRC_DIR)
	$(POETRY) build
	rm -rf  $(P2G_SRC_DIR)/doc $(P2G_SRC_DIR)/examples


.PHONY:
tox: $(RELEASE_FILE)
	$(PR)	tox --installpkg $(RELEASE_FILE)

release: | $(RELEASE_FILE) tox

# ######################################################################
# # linty stuff

.PHONY:
vulture: install-tools | $(LINTABLE_SRC)
	 $(PR) vulture

.PHONY:
pyright:  install-tools | $(LINTABLE_SRC)
	 $(PR) pyright 
.PHONY:
mypy: install-tools |  $(LINTABLE_SRC)
	 $(PR) mypy  
.PHONY: 
flake8:  install-tools | $(LINTABLE_SRC)
	$(PR) flake8p

.PHONY:
pylint:  install-tools | $(LINTABLE_SRC)
	 $(PR) pylint tools p2g
.PHONY:
ruff:  install-tools | $(LINTABLE_SRC)
	$(PR) ruff check tools p2g  

.PHONY:
deptry: 
	$(PR) deptry . 
.PHONY:
pytype:  install-tools | $(LINTABLE_SRC)
	@# needs python < 3.11 
	@#	pytype p2g

.PHONY:
tlint:lint test

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
	$(RUN_VERSION_SCRIPT) $(VERSIONED_FILES) --git --report --inplace
# .PHONY:
clean:
	if [  $$(which p2g) ] ; then rm -f $$(which p2g); fi
	git clean -fdx
	rm -f $(COMPILED_EXAMPLES)

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

%.diff: examples/%.nc
	@	touch -f $<.old
	-	diff $<  $<.old > $@
	cat $@
	@	cp $< $<.old

.mark-%: $(EXAMPLE_DIR)/%.py $(EXAMPLE_DIR)/defs.py
	poetry run p2g  $<   tmp.nc
	poetry run p2g  $< --narrow  $(DSTDIR)/{countdown}-pc.nc 


.PHONY:
$(DSTDIR)/ZZ%.nc: %.py
	poetry run p2g $<  --wide $@
	poetry run p2g $< --wide  $(DSTDIR)/{countdown}-pc.nc 
	touch $@

# wip-probe: .mark-probecalibrate

goldify-all: $(addprefix goldify-, $(TEST_NAMES)) 


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
	git push local dev


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
