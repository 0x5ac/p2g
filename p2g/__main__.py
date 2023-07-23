# flake8: noqa
# pylint:  disable=wrong-import-order
# pylint:  disable=wrong-import-position
# isort: skip_file
# no import sorting, typeguard must do its thing before
# imports get done.
import typeguard
import p2g.main

typeguard.install_import_hook("p2g")
p2g.main.main()
