# pylint:  disable=wrong-import-order
# isort: skip_file
# no import sorting, typeguard must do its thing before
# imports get done.

import typeguard


typeguard.install_import_hook("p2g")
import p2g.main

p2g.main.main()
