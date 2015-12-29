Axiom
=====
Produces a report that can be used to verify if TRIRIGA-generated PM Schedules
are correct.


Usage
-----


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
