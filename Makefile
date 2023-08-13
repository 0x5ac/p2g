.RECIPEPREFIX=>
export MAKEFLAGS=-Otarget --no-print-directory -r -R --warn
export COLUMNS=40


# topj:
# > @ make -j 3 default
PATH             := $(HOME)/.local/bin:/usr/bin
EMACS            := emacs
POETRY           := poetry
PR               := $(POETRY) run

RUN_MODVERSION   := $(PR) python tools/modversion.py
RUN_MAKESTDVARS  := $(PR) python tools/makestdvars.py
RUN_COVERAGE     := $(PR) coverage
RUN_PYTEST       := $(PR) pytest

LOG_DIR          := log
DOCS_DIR          := docs
VERSION_FILE     := p2g/VERSION

LINTS            := pyright mypy pylint ruff flake8
LOG_LINTS        := $(patsubst %,$(LOG_DIR)/%.llog, $(LINTS))

DISTDIFFS_ERROR  := $(LOG_DIR)/distdiffs-error
LOG_DISTDIFFS    := $(LOG_DIR)/distdiffs.log
LOG_DISTGOT      := $(LOG_DIR)/distgot.log
LOG_DISTWANT     := $(LOG_DIR)/distwant.log

LOG_DIST         := $(LOG_DIR)/FILES-IN-DIST.LOG
LOG_DOC          := $(LOG_DIR)/doc.log
LOG_EXAMPLES     := $(LOG_DIR)/examples.log
LOG_LINT         := $(LOG_DIR)/ALL-LINTS.LOG
LOG_POETRY       := $(LOG_DIR)/poetry.log
LOG_COVERAGE     := $(LOG_DIR)/coverage.log
LOG_TESTS        := $(LOG_DIR)/pytest.log
THIS_VERSION     := $(shell cat $(VERSION_FILE))
LOG_TOX          := $(LOG_DIR)/tox.log
VERSION_STAMP    := $(LOG_DIR)/version-$(THIS_VERSION).log


.PHONY           : lint test start finish examples docs poetry version  dist
default          : start | finish
docs             : $(LOG_DOC)
examples         : $(LOG_EXAMPLES)
lint             : $(LOG_LINT)
poetry           : $(LOG_POETRY)
tests            : $(LOG_TESTS)
version          : $(VERSION_STAMP)
tox              : $(LOG_TOX)
dist             : $(LOG_DIST)

# only need this if rebuilding doc.
OX_GFM_DIR       = ~/.emacs.d/straight/build/ox-gfm

HR               = @ echo "*******"
H1               = @ echo "***"
H2               = @ echo "*****"
HW               = @ echo "newer deps " $?
######################################################################
# files used, should only appear once.
P2G_GEN_SRC       :=            \
  p2g/haas.py

ALL_P2G_SRC       :=            \
  p2g/__init__.py               \
  p2g/__main__.py               \
  p2g/axis.py                   \
  p2g/builtin.py                \
  p2g/coords.py                 \
  p2g/err.py                    \
  p2g/fstring.py                \
  p2g/gbl.py                    \
  p2g/goto.py                   \
  p2g/main.py                   \
  p2g/nd.py                     \
  p2g/op.py                     \
  p2g/scalar.py                 \
  p2g/stat.py                   \
  p2g/symbol.py                 \
  p2g/sys.py                    \
  p2g/vector.py                 \
  p2g/walkbase.py               \
  p2g/walkexpr.py               \
  p2g/walkfunc.py               \
  p2g/walkstat.py               \
  $(P2G_GEN_SRC)

TOOL_SRC          :=            \
  tools/modversion.py           \
  tools/makestdvars.py

FUNC_TEST_FILES   :=            \
  tests/test_assert.py          \
  tests/test_axes.py            \
  tests/test_badpytest.py       \
  tests/test_basic.py           \
  tests/test_builtins.py        \
  tests/test_comment.py         \
  tests/test_coords.py          \
  tests/test_dprnt.py           \
  tests/test_edge.py            \
  tests/test_error.py           \
  tests/test_examples.py        \
  tests/test_expr.py            \
  tests/test_for.py             \
  tests/test_func.py            \
  tests/test_goto.py            \
  tests/test_interp.py          \
  tests/test_is.py              \
  tests/test_lib.py             \
  tests/test_linenos.py         \
  tests/test_main.py            \
  tests/test_makestdvars.py     \
  tests/test_marker.py          \
  tests/test_meta.py            \
  tests/test_nt1.py             \
  tests/test_op.py              \
  tests/test_prec.py            \
  tests/test_rtl.py             \
  tests/test_smoke.py           \
  tests/test_starimport.py      \
  tests/test_str.py             \
  tests/test_symtab.py          \
  tests/test_sys.py             \
  tests/test_tuple.py           \
  tests/test_vars.py            \
  tests/test_vector.py

READMEMD          := readme.md
DIST_DOC          :=            \
  docs/howto.md                 \
  docs/howto.txt                \
  docs/haas.txt                 \
  docs/pytest.svg               \
  docs/coverage.svg             \
  docs/mit.svg                  \
  $(READMEMD)

INCLUDED_ORGS     :=            \
  docs/src/authors.org          \
  docs/src/axes.org             \
  docs/src/badges.org           \
  docs/src/coordinates.org      \
  docs/src/dprnt.org            \
  docs/src/examples.org         \
  docs/src/expressions.org      \
  docs/src/goto.org             \
  docs/src/haas.org             \
  docs/src/install.org          \
  docs/src/introduction.org     \
  docs/src/license.org          \
  docs/src/notes.org            \
  docs/src/release.org          \
  docs/src/symboltables.org     \
  docs/src/thanksto.org         \
  docs/src/toc.org              \
  docs/src/usage.org            \
  docs/src/variables.org        \
  docs/src/video.org            \
  docs/src/when.org             \
  docs/src/why.org

COMPILED_EXAMPLES :=            \
  examples/probecalibrate.nc    \
  examples/vicecenter.nc        \
  examples/maxflutes.nc

EXAMPLE_SRC       :=            \
  examples/maxflutes.py         \
  examples/probecalibrate.py    \
  examples/usrlib.py            \
  examples/vicecenter.py        \

ALL_TEST_SRC      :=            \
  $(FUNC_TEST_FILES)            \
  $(EXAMPLE_SRC)                \
  tests/conftest.py



######################################################################
ALL_EXAMPLES    := $(EXAMPLE_SRC) $(COMPILED_EXAMPLES)
DIST_FILE       := dist/p2g-$(THIS_VERSION).tar.gz
ALL_PY          := $(ALL_P2G_SRC) $(TOOL_SRC) $(ALL_TEST_SRC)
LINTABLE_SRC    := $(ALL_P2G_SRC) $(TOOL_SRC)
CONTROL_FILES   := Makefile pyproject.toml .scrutinizer.yml


VERSIONED_FILES = p2g/__init__.py pyproject.toml  docs/src/introduction.org
IN_DIST         := $(ALL_EXAMPLES) $(DIST_DOC) $(ALL_P2G_SRC) $(VERSION_FILE)

.PRECIOUS: $(LOG_POETRY)
.PRECIOUS: $(IN_DIST)
.PRECIOUS: $(LOG_DOC)
.PRECIOUS: $(LOG_TESTS)
.PRECIOUS: $(LOG_LINT)
.PRECIOUS: $(DIST_FILE)
DEFAULT_DEPS    :=          \
  $(LOG_POETRY)       \
  $(IN_DIST)                \
  $(LOG_DOC)                \
  $(LOG_TESTS)              \
  $(LOG_LINT)               \
  $(DIST_FILE)

######################################################################
.EXTRA_PREREQS:= .mkdirs

.mkdirs:
>mkdir -p $(LOG_DIR)  $(DOCS_DIR)/obj
> touch $@

$(DOCS_DIR)/obj $(LOG_DIR):
>	mkdir -p $@

start           :
> $(HR)
> $(H1)  $$(python --version) p2g $(THIS_VERSION)


finish          : $(DEFAULT_DEPS) $(LOG_DISTDIFFS)
> $(HR)
> $(H1) Package in $(DIST_FILE)


install         : $(DIST_FILE)
> pip install --user $<

######################################################################
# Init environment

$(VERSION_STAMP) : $(VERSION_FILE) $(LOG_POETRY)
> $(RUN_MODVERSION)             \
  --truth $(VERSION_FILE)       \
  --names $(VERSIONED_FILES)    \
  --stdout >	$@

$(VERSIONED_FILES) : $(VERSION_STAMP)

.PRECIOUS: $(LOG_POETRY)
$(LOG_POETRY)    :
> # take opportunity to make dest directories.
> $(HR)
> which poetry || curl -sSL https://install.python-poetry.org | python3
> $(HR)
> $(H1) "Poetry $$(which poetry)"
> $(HR)
> $(POETRY) install
> $(POETRY) update
> $(POETRY) export --without-hashes > requirements.txt
> $(POETRY) --version > $(LOG_POETRY)

######################################################################
#   examples
#$(LOG_EXAMPLES) : $(COMPILED_EXAMPLES)
#n
#examples/%.nc:examples/%.py
#> $(PR) p2g $<  $@ | tee -a $(LOG_EXAMPLES)

######################################################################
# machine generated code
p2g/haas.py            : tools/makestdvars.py $(LOG_POETRY)
> $(RUN_MAKESTDVARS)  --py=$@

docs/haas.txt  : tools/makestdvars.py $(LOG_POETRY)
> $(RUN_MAKESTDVARS)  --txt=$@

docs/haas.html : tools/makestdvars.py $(LOG_POETRY)
> $(RUN_MAKESTDVARS)  --html=$@

######################################################################
# emacs path
# only make docs if there's an emacs.
ifeq ($(shell which $(EMACS)),)
$(LOG_DOC) :
>   echo "DOC not being rebuilt, needs emacs." | tee $@
>   touch $(DIST_DOC)
EVAL=@ echo "NO EMACS"
else
ifeq ($(wildcard $(OX_GFM_DIR)),)
$(LOG_DOC) :
>@   echo "EMACS installed, but still need" \
    "github markdown org export." \
|   tee $@
>   touch $(DIST_DOC)
EVAL=@ echo NEED GITHUB MARKDOWN EXPORT"
else
# run emacs in batch to expand and include files
# which make up the final doc.  Sed out the
# loquacity.
EVAL =                                      \
  emacs $(abspath $<)                       \
  -q -Q                                     \
  --chdir $(dir $(abspath $<))              \
  -L $(OX_GFM_DIR)                          \
  --batch                                   \
  --load $(abspath tools/org-to-x.el)       \
  -f org-to-any                             \
  $(abspath $@)                             \
  2>&1 | sed                                \
  -e  '/Code block.*/d'                     \
  -e  's:executing Python code block::g' ;  \
  test -s $@ || echo "EMPTY FILE"; \
  test -s $@

######################################################################
# the readme md includes some of the exorgs and the toc., see what changed.
TMP_ORGS   = $(patsubst docs/src/%,docs/obj/%,$(INCLUDED_ORGS))
ORG_DIFFS  = $(patsubst %.org, %.diff,$(TMP_ORGS))
$(LOG_DOC) : $(DIST_DOC) $(ORG_DIFFS)
> @ cat $(ORG_DIFFS) | tee $@.error
> if test  -s $@.error ; then                       \
  echo "DOC HAS DIFFERENCES"            ;           \
  echo "maybe cp docs/obj/*.org docs/src"    ;      \
  exit 1;                                           \
fi
> mv $@.error $@

endif


######################################################################
# tmp orgs are org files with includes and evaluation.

VPATH            = docs/src

docs/obj/%.org:%.org $(VERSION_STAMP)
> $(EVAL)


docs/obj/%.diff:docs/obj/%.org
> - diff  docs/src/$*.org $< > $@

%.md:%.org $(TMP_ORGS)
> $(EVAL)

$(READMEMD)        : readme.org $(TMP_ORGS)
> $(EVAL)

$(INCLUDED_ORGS) : $(VERSION_STAMP)

docs/howto.txt docs/howto.md:  docs/obj/howto.org $(TMP_ORGS)
> $(EVAL)

endif

######################################################################
# badges

STYLE=?style=plastic


docs/coverage.svg: docs/src/coverage.in.svg $(LOG_COVERAGE)
> inside=$$(grep TOTAL log/coverage.log  | sed  -E "s:.* ([0-9]+)%:\1%:g"); sed -E s:100%:$$inside:g $< >$@

docs/pytest.svg: docs/src/pytest.in.svg $(LOG_TESTS)
> inside=$$(grep "^[0-9]" $(LOG_TESTS)); sed -E s:XXX:$$inside:g $< >$@

docs/mit.svg: docs/src/mit.in.svg
> cp $< $@



#######################################################################
# lints

$(LOG_DIR)/%.llog : $(LINTABLE_SRC)
> @ # run lint over p2g directory
> $(PR) $* p2g | tee $@

# use all lintlogs to make one big one.
$(LOG_LINT)      : $(LOG_LINTS)
> @ cat $^ > $@

######################################################################
# Tests

$(LOG_TESTS):  $(ALL_P2G_SRC) $(ALL_TEST_SRC) $(ALL_EXAMPLES)
> $(HR)
> $(H1) pytest.
> $(RUN_PYTEST) | tee $(LOG_TESTS)

$(LOG_COVERAGE): $(LOG_TESTS)
> $(RUN_COVERAGE) lcov -q
> $(RUN_COVERAGE) report | tee $@
> $(HR)

######################################################################
# make a release : build the distribution .tar for pip
# test it for sanity

# want to distribute docs and examples, so copy
# into src tree just while the packager is busy.
$(DIST_FILE) $(LOG_DIST) &: $(IN_DIST)
> $(HR)
> $(H1) "Make dist"
> rsync  docs/*.*   p2g/docs
> rsync examples/* p2g/examples
> $(POETRY) build
> rm -rf p2g/examples
> rm -rf p2g/docs
> tar ztvf  $(DIST_FILE) > $(LOG_DIST)




######################################################################$


# make sure everything in dist is in makefile and viceversa.
# a dist tar file has elements like this:
# -rwxr-xr-x 0/0            9790 2023-07-22 22:06 p2g-0.2.220/p2g/walkstat.py
# dist with doc in top/p2g/doc, but in the tree as top/doc etc.
# we mess with the paths to make them match up with our tree.
# and remove junk, then compare with what we have.
# any differences need to be investigated.

$(LOG_DISTGOT)  : $(DIST_FILE)
> $(HR)
> $(H1)  Comparing expected and actual distribution.
> tar tzvf $(DIST_FILE)                                 \
| sed -E 'sX.*[0-9][0-9]:[[:digit:]]{2} [^/]+/XXg'      \
| egrep -v "(pyproject.toml|PKG-INFO)"                  \
| sort > $(LOG_DISTGOT)


$(LOG_DISTWANT) : $(IN_DIST)
> $(H2) Make $(LOG_DISTWANT)
> echo $(IN_DIST)                                       \
| sed -E "s:(examples|docs)/:p2g/\\1/:g"                \
| xargs -n 1                                            \
| sort > $(LOG_DISTWANT)

$(LOG_DISTDIFFS) : $(LOG_DISTWANT) $(LOG_DISTGOT)
> $(H1) Compare want with got
> $(H2) "BOTH COLUMNS SHOULD BE SAME" > $(DISTDIFFS_ERROR)
> @ printf "%9s%40s\n" "***WANT***" "***GOT***" >> $(DISTDIFFS_ERROR)
> @ sdiff -w 70 $(LOG_DISTWANT) $(LOG_DISTGOT) >>  $(DISTDIFFS_ERROR)
> diff -u $(LOG_DISTWANT) $(LOG_DISTGOT)
> $(H1) All OK
> mv $(DISTDIFFS_ERROR) $(LOG_DISTDIFFS)
> $(HR)


$(LOG_TOX) : $(DIST_FILE)
> $(PR)	tox --installpkg $(DIST_FILE) | tee $@

##########

release:
>	gh release create v$(THIS_VERSION) --notes="release v$(THIS_VERSION)"

newwork:
> git fetch origin
> - git branch -C dev$(THIS_VERSION) origin/main
> git push origin dev$(THIS_VERSION)
tagit:
> git fetch origin
> git tag -a v$(THIS_VERSION) -m "release v$(THIS_VERSION)"
> git push origin v$(THIS_VERSION)

togithub   :
> git commit --allow-empty -m v$(THIS_VERSION) -a
#> git tag  v$(THIS_VERSION)
> git push $(T)
> git push --tags $(T) --force


######################################################################
# cleanup stuff
##########
.PHONY:
isort:$(LINTABLE_SRC)
> $(PR) isort $^
##########
.PHONY:
ssort:$(LINTABLE_SRC)
> -	$(PR) ssort  $^
##########
.PHONY:
autopep8:$(LINTABLE_SRC)
> $(PR) autopep8 --in-place $^
##########
.PHONY:
black:$(LINTABLE_SRC)
> $(PR) black $^
##########
.PHONY:
autoflake:$(LINTABLE_SRC)
>  $(PR) autoflake --ignore-init-module-imports  --remove-all-unused-imports  -i -v $^
##########
.PHONY:
cleanup: isort ssort  black
######################################################################
# utils
.PHONY:
clean:
> if [  $$(which p2g) ] ; then rm -f $$(which p2g); fi
> git clean -fdx

######################################################################
######################################################################
#for my machine.

telnet:
> telnet vf3 9192
DSTDIR=/home/sac/vf3/_nc_


wip: examples/fastervicecenter.nc
>	poetry run p2g  examples/fastervicecenter.py --narrow  $(DSTDIR)/{countdown}-pc.nc


wip-probe: probecalibrate.diff
.PHONY:
wip-fasterviceceneter: fasterviceceneter.diff

MAKEONE=poetry run p2g

%.diff: examples/%.nc
> @	touch -f $<.old
> -	diff $<  $<.old > $@
> cat $@
> @	cp $< $<.old

.mark-%: examples/%.py examples/usrlib.py
> poetry run p2g  $<   tmp.nc
> poetry run p2g  $< --narrow  $(DSTDIR)/{countdown}-pc.nc

# examples/%.nc : examples/%.py
# > poetry run p2g  $< $@


gif-examples: examples/vicecenter.nc examples/probecalibrate.nc examples/maxflutes.nc
> cp examples/vicecenter*.got examples/vicecenter.nc
> cp examples/probecalibrat*.got examples/probecalibrate.nc
> cp examples/maxflutes*.got examples/maxflutes.nc


gif-%: tests/test_%.py
> - $(PR) pytest tests/test_$*.py --gif
> sed '/^# TESTS BELOW/q' $< > t1
> - cat tests/test_$*_* >> t1
> cp t1 $<
> black   $<

SHORT_TEST_NAMES = $(patsubst tests/test_%.py,%, $(FUNC_TEST_FILES))
allgif           :
> for x in $(SHORT_TEST_NAMES) ; do make gif-$$x; done


ci:
> git commit -m 'wip' -a
> git push local HEAD:main

gci:
> git commit -m 'wip' -a
> git push github HEAD:main

#justt:
#> python -m p2g  examples pop
help:
> python -m p2g   -
msv:
> python tools/makestdvars.py --dpy=-
example:
> python -m p2g  examples/fasterviceceneter.py

apytest:
> poetry run pytest tests/test_dprnt.py

btest:
> python tools/makebadge.py  --type=pytest --logfile=$(LOG_TESTS) --src=docs/src/pytest.svg	 --dst=docs/pytest.svg
extest:
> poetry run pytest tests/test_examples.py

mtest:
> python ~/.emacs.d/etc2022jul/remake.py

tmodversion:
> python  tools/modversion.py --truth $(VERSION_FILE)  --top . --out .build --names $(VERSIONED_FILES)
>
justt:
> poetry run p2g t.py
#pdb: justt
#pdb: justt
#pdb: tmodversion
#pdb: btest
#pdb: mdc
#pdb: fakeorg
pdb:example


# T=tests/test_assert.py
# T=tests/test_badpytest.py
# T=tests/test_vector.py
# T=tests/test_axis.py
ARGS=--pdb
RUNNER=poetry run pytest


sxpdb:
> python -m pdb --command=c tools/makestdvars.py --dpy=-

p:
> poetry run pytest  tests/test_tools.py

# TN 9192
# MDC 9191
#
# Local Variables:
# makefile-backslash-column:20
# End:
