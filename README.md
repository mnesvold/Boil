Boiler
======

Command-line utility for generating boilerplate files. At the moment, it's a glorified file-copy utility, but the plan is to include basic templating in the future.


Installation
------------

The utility itself lives in a single file, `boiler.py`. To install, just drop the file (or a link to the file) anywhere in your `PATH`.

To run the tests, download both files, make sure `test-boiler.py` can reference `boiler.py` via `import boiler` (putting them in the same folder is easiest), and run `python test-boiler.py`.


Usage
-----

The utility copies named files from a _templates directory_ (by default, `~/.boiler`) into an _output directory_ (by default, the working directory):

```bash
$ ls
awesome-program.c
$ ls ~/.boiler
build.xml setup.py Makefile LICENSE
$ boiler.py Makefile LICENSE
$ ls
awesome-program.c Makefile LICENSE
```

The default templates directory and output directory may be overridden:

```bash
$ ls project
$ ls ../templates
build.xml setup.py Makefile LICENSE
$ boiler.py --templates-dir ../templates --output-dir project Makefile LICENSE
$ ls project
Makefile LICENSE
```
