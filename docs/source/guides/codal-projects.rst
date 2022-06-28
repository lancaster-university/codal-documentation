CODAL Projects
==============

.. note::
    This guide covers the setup needed for new projects, but does not include how to install the required tools.
    Please see :doc:`/guides/prerequisites` for your operating system for how to install the applications and tools to build CODAL applications.

Creating New Projects (CODAL Bootstrap)
---------------------------------------

A simple way to get started developing in CODAL is to use `codal-bootstrap <https://github.com/lancaster-university/codal-bootstrap>`_ to generate
a new C++ project structure for us.

To do this, we need to get the current bootstrap build file which we will use to both set up, and compile our project.

1. Create a new folder for our project, here we will refer to it as ``app``
2. Download a copy of ``build.py`` from ``codal-bootstrap`` into our new ``app`` folder
3. Open a console or terminal window and navigate to our new ``app`` folder
4. Run ``python build.py`` to download the build tools

At this point, we will be presented with a choice of platform, this determines which device we want to build our application for.
Note that this does not lock your project into *only* being able to build for this platform, and it can be changed at a later stage; but for now
we want to choose the ``codal-microbit-v2`` target to build for the Micro:bit v2 by running ``python build.py codal-microbit-v2``

Once the tool has downloaded all the required libraries to build for the Micro:bit, you should have a working project with a bare-bones program
ready to compile.

To compile your project, run ``python build.py`` with no arguments and if all goes well, you should be left with a ``MICROBIT.hex`` file which can
be flashed to your Micro:bit by copying it to the Micro:bit disk.

Older Projects
--------------

Older projects had the build tools baked into the source code, but as ``codal-bootstrap`` maintains backwards compatibility with the older tools, they
should operate in much the same way as described here, with the exception of the initial download phase.