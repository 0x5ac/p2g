.RECIPEPREFIX   = >
export MAKEFLAGS=-Otarget --no-print-directory -r -R --warn #-j30
export COLUMNS=40

PATH         := $(HOME)/.local/bin:/usr/bin

LOG_DIR      := log
DIST_DIR     := dist
DOCS_DIR     := docs
STAGING_DIR  := staging

VERSION_FILE := p2g/VERSION
VERSION      := $(shell cat $(VERSION_FILE))
DIST_FILE    := dist/p2g-$(VERSION).tar.gz

LOG_POETRY   := $(LOG_DIR)/poetry.log
LOG_COVERAGE := $(LOG_DIR)/coverage.log
LOG_TESTS    := $(LOG_DIR)/pytest.log
LOG_LINTS    := $(LOG_DIR)/lints.log

LINTS        := pyright mypy pylint ruff flake8

POETRY       := poetry
PR           := $(POETRY) run

default      : dist

H0               = @ echo "*"
H1               = @ echo "***"
H2               = @ echo "*****"
HR               = @ echo "*******"

######################################################################
# files used, should only appear once.

ALL_P2G_SRC     :=              \
  p2g/__init__.py               \
  p2g/__main__.py               \
  p2g/abandon.py                \
  p2g/axis.py                   \
  p2g/builtin.py                \
  p2g/coords.py                 \
  p2g/err.py                    \
  p2g/fstring.py                \
  p2g/gbl.py                    \
  p2g/goto.py                   \
  p2g/haas.py                   \
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

TOOL_SRC        :=              \
  tools/modversion.py           \
  tools/makestdvars.py          \
  tools/fakeorg.py

FUNC_TEST_FILES :=              \
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

DIST_DOC        :=              \
  docs/howto.md                 \
  docs/howto.txt                \
  docs/haas.txt                 \
  docs/coverage.svg             \
  docs/pytest.svg               \
  docs/mit.svg                  \
  readme.md


EXAMPLES        :=              \
  examples/probecalibrate.nc    \
  examples/vicecenter.nc        \
  examples/maxflutes.nc         \
  examples/maxflutes.py         \
  examples/probecalibrate.py    \
  examples/usrlib.py            \
  examples/vicecenter.py        \

ALL_TEST_SRC    :=              \
  $(FUNC_TEST_FILES)            \
  tests/conftest.py

ALL_ORGS        :=              \
docs/src/authors.org            \
  docs/src/axes.org             \
  docs/src/badges.org           \
  docs/src/coordinates.org      \
  docs/src/dprnt.org            \
  docs/src/examples.org         \
  docs/src/expressions.org      \
  docs/src/goto.org             \
  docs/src/haas.org             \
  docs/src/howto.org            \
  docs/src/install.org          \
  docs/src/introduction.org     \
  docs/src/license.org          \
  docs/src/maint.org            \
  docs/src/maintopt.org         \
  docs/src/notes.org            \
  docs/src/readme.org           \
  docs/src/release.org          \
  docs/src/symboltables.org     \
  docs/src/thanksto.org         \
  docs/src/toc.org              \
  docs/src/usage.org            \
  docs/src/variables.org        \
  docs/src/video.org            \
  docs/src/when.org             \
  docs/src/why.org


LINTABLE_SRC    := $(ALL_P2G_SRC) $(TOOL_SRC)
VERSIONED_FILES := p2g/__init__.py pyproject.toml docs/src/introduction.org
IN_DIST         := $(EXAMPLES) $(DIST_DOC) $(ALL_P2G_SRC) $(VERSION_FILE)



######################################################################
.EXTRA_PREREQS := $(LOG_POETRY)

dist           : tests lint $(DIST_FILE)
> $(HR)
> $(H1)  $$(python --version) p2g $(VERSION)
> $(H1) Package in $(DIST_FILE)

install        : $(DIST_FILE)
> pip install --user $<

######################################################################
# Init environment

$(VERSIONED_FILES) &: $(VERSION_FILE)  $(LOG_POETRY)
> $(PR) python tools/modversion.py     \
  --truth $(VERSION_FILE)               \
  --victims $(VERSIONED_FILES)

.PRECIOUS          : $(LOG_POETRY)
$(LOG_POETRY)      :
> mkdir -p $(LOG_DIR) $(DIST_DIR)
> # take opportunity to make dest directories.
> $(HR)
> which poetry || curl -sSL https://install.python-poetry.org | python3
> $(HR)
> $(H1) "Poetry $$(which poetry)"
> $(HR)
> $(POETRY) install
> $(POETRY) update
> #$(POETRY) export --without-hashes > requirements.txt
> $(POETRY) --version > $(LOG_POETRY)
> # make the log file old - things don't depend on
> # when poetry was installed, just that it was.
> @touch  -t 200001010101 $(LOG_POETRY)


######################################################################

examples/%.nc: examples/%.py
>	poetry run p2g --no-id $< $@

######################################################################
# machine generated code
p2g/haas.py  : tools/makestdvars.py $(LOG_POETRY)
> $(PR) python tools/makestdvars.py  --py=$@

docs/haas.txt  : tools/makestdvars.py $(LOG_POETRY)
> $(PR) python tools/makestdvars.py  --txt=$@

docs/haas.html : tools/makestdvars.py $(LOG_POETRY)
> $(PR) python tools/makestdvars.py  --html=$@

#######################################################################
# lints

LINTOUTS     = $(patsubst %,$(LOG_DIR)/%.lintout, $(LINTS))

$(LOG_DIR)/%.lintout : $(LINTABLE_SRC)
> @ # run lint over p2g directory
> $(PR) $* p2g tools | tee $@

# use all lintlogs to make one big one.
$(LOG_LINTS) : $(LINTOUTS)
> cat $^ > $@

lint         : $(LOG_LINTS)
> cat $(LOG_LINTS)

######################################################################
# Tests

$(LOG_COVERAGE) $(LOG_TESTS) &: $(ALL_P2G_SRC) $(ALL_TEST_SRC) $(EXAMPLES)
> $(HR)
> $(H1) pytest.
> $(PR) pytest | tee $(LOG_TESTS)
> $(PR) coverage lcov -q
> $(PR) coverage report | tee $(LOG_COVERAGE)
> $(HR)

tests: $(LOG_TESTS)
> cat $(LOG_TESTS)

######################################################################
# build release from a dummy tree
# copy only things explicityly named here.

$(DIST_FILE) : $(IN_DIST)
> rm -rf $(STAGING_DIR)
> mkdir -p $(STAGING_DIR)
> tar cf - $(IN_DIST) | tar -C $(STAGING_DIR)  -xf -
> mv $(STAGING_DIR)/docs $(STAGING_DIR)/p2g
> mv $(STAGING_DIR)/examples $(STAGING_DIR)/p2g
> cp pyproject.toml $(STAGING_DIR)
> (cd $(STAGING_DIR); poetry build)
> mv $(STAGING_DIR)/dist/* dist

tox          : $(DIST_FILE)
> $(PR)	tox --installpkg $(DIST_FILE)

##########

release:
> gh release create v$(VERSION) --notes="release v$(VERSION)"

######################################################################
# cleanup stuff

isort:$(LINTABLE_SRC)
> $(PR) isort $^

ssort:$(LINTABLE_SRC)
> - $(PR) ssort  $^

autopep8:$(LINTABLE_SRC)
> $(PR) autopep8 --in-place $^

black:$(LINTABLE_SRC)
> $(PR) black $^

autoflake:$(LINTABLE_SRC)
>  $(PR) autoflake --ignore-init-module-imports  --remove-all-unused-imports  -i -v $^

cleanup: isort ssort black autopep8
######################################################################
# utils

clean:
> if [  $$(which p2g) ] ; then rm -f $$(which p2g); fi
> git clean -fdx


######################################################################
# DOC

# for rebuilding doc, may never need it
EMACS     := emacs
OX_GFM    := ~/.emacs.d/straight/build/ox-gfm/ox-gfm.el

CAN_EMACS := YES

ifeq ($(wildcard $(OX_GFM)),)
CAN_EMACS := NO
endif
ifeq ($(wildcard $(shell which $(EMACS))),)
CAN_EMACS := NO
endif

ifeq ($(CAN_EMACS),NO)
docs/%.txt docs/%.md: docs/src/%.org $(ALLORGS)
> $(HR)
> $(HR)
> $(H0) "DOC not being rebuilt, needs emacs and ox-gfm."
> touch $@
else
# readme.md and howto.md from .org
EVAL      =                                 \
  $(EMACS) $(abspath $<)                    \
  -q -Q                                     \
  --chdir $(dir $(abspath $<))              \
  -L $(dir $(OX_GFM))                       \
  --batch                                   \
  --load $(abspath tools/org-to-x.el)       \
  -f org-to-any                             \
  $(abspath $@)

docs/howto.txt : docs/src/howto.org $(ALL_ORGS) docs/haas.txt
> $(PR) python tools/fakeorg.py $(dir $<)
> $(EVAL)

%.md docs/%.md: docs/src/%.org docs/howto.txt docs/haas.txt
> $(EVAL)

endif

######################################################################
# badges
docs/coverage.svg: docs/src/coverage.in.svg $(LOG_COVERAGE)
> $(H1) Make $@
> @ inside=$$(grep TOTAL $(LOG_COVERAGE)  | sed  -E "s:.* ([0-9]+)%:\1%:g"); sed -E s:100%:$$inside:g $< >$@

docs/pytest.svg: docs/src/pytest.in.svg $(LOG_TESTS)
> $(H1) Make $@
> @ inside=$$(grep "^[0-9]" $(LOG_TESTS)); sed -E s:XXX:$$inside:g $< >$@

docs/mit.svg: docs/src/mit.in.svg
> $(H1) Make $@
> @ cp $< $@

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

.PHONY:aexample pdb
aexample:
> echo HIU
> python -m p2g help version #--job=O123 examples/vicecenter.py

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
fakeorg:
> python  docs/src/fakeorg.py docs/src/fish.org
>
justt:
> poetry run p2g t.py
#pdb: justt
#pdb: justt
#pdb: tmodversion
#pdb: btest
#pdb: mdc
#pdb: fakeorg
pdb: aexample




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


######################################################################
newwork:
> git fetch origin
> - git branch -C dev$(VERSION) origin/main
> git push origin dev$(VERSION)
tagit:
> git fetch origin
> git tag -a v$(VERSION) -m "release v$(VERSION)"
> git push origin v$(VERSION)

togithub   :
> git commit --allow-empty -m v$(VERSION) -a
#> git tag  v$(VERSION)
> git push $(T)
> git push --tags $(T) --force
