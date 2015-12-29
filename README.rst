python-cmdline-axiom
========================
This is a structure template for Python command line applications, ready to be
released and distributed via setuptools/PyPI/pip for Python 2 and 3.

Please have a look at the corresponding article:
http://gehrcke.de/2014/02/distributing-a-python-command-line-application/


Usage
-----
Clone this repository and adopt the axiom structure for your own project.
This is just a starting point, but I hope a good one. From there on, you should
read and follow http://python-packaging-user-guide.readthedocs.org/en/latest/,
the definite resource on Python packaging.

Rename files
~~~~~~~~~~~~

In bash::

    PROJECT=naiads
    cd python-cmdline-axiom/

    cd axiom
    rename axiom ${PROJECT} *
    cd ..
    rename axiom ${PROJECT} *

    find . -type f -print0 | xargs -0 sed -i -e "s/axiom/${PROJECT}/g"

Behavior
--------

Flexible invocation
*******************

The application can be run right from the source directory, in two different
ways:

1) Treating the axiom directory as a package *and* as the main script::

    $ python -m axiom arg1 arg2
    Executing axiom version 0.2.0.
    List of argument strings: ['arg1', 'arg2']
    Stuff and Boo():
    <class 'axiom.stuff.Stuff'>
    <axiom.axiom.Boo object at 0x7f43d9f65a90>

2) Using the axiom-runner.py wrapper::

    $ ./axiom-runner.py arg1 arg2
    Executing axiom version 0.2.0.
    List of argument strings: ['arg1', 'arg2']
    Stuff and Boo():
    <class 'axiom.stuff.Stuff'>
    <axiom.axiom.Boo object at 0x7f149554ead0>


Installation sets up axiom command
**************************************

Situation before installation::

    $ axiom
    bash: axiom: command not found

Installation right from the source tree (or via pip from PyPI)::

    $ python setup.py install

Now, the ``axiom`` command is available::

    $ axiom arg1 arg2
    Executing axiom version 0.2.0.
    List of argument strings: ['arg1', 'arg2']
    Stuff and Boo():
    <class 'axiom.stuff.Stuff'>
    <axiom.axiom.Boo object at 0x7f366749a190>


On Unix-like systems, the installation places a ``axiom`` script into a
centralized ``bin`` directory, which should be in your ``PATH``. On Windows,
``axiom.exe`` is placed into a centralized ``Scripts`` directory which
should also be in your ``PATH``.
