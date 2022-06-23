####################
Installation - Tools
####################

Before we can get started programming the Micro:bit v2 in CODAL, we need to install some tools.
The details of how to do this on each operating system differ, so make sure you're following the right section for your system below.

In summary, we need to have the following components installed:

- Python 3 or newer
- Git, via `Github Desktop <https://desktop.github.com/>`_ or directly via `git-scm <https://git-scm.com/>`_
- `Arm GNU Toolchain Downloads <https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/downloads>`_
- `CMake <https://cmake.org/>`_

We may also want to install these optional dependencies, which may be useful for specific tasks

- `Visual Studio Code <https://code.visualstudio.com/>`_ (Recommended!)
- `pyocd <https://pyocd.io/>`_ *or* `openocd <https://openocd.org/>`_ to use on-chip debugging


Windows Instructions
====================



Mac Instructions
================



Linux Instructions
==================

You should use your distribution's package repositories to install the required tools.
These differ from distribution to distribution, and only a few common ones are listed here, but it is expected that any modern general-purpose
distribution should have the required packages to build CODAL.


Debian/Ubuntu (and other APT-based systems)
-------------------------------------------

In a terminal, update your package index with ``apt update``, then install the basic required packages: ``apt install build-essential git cmake python3 gcc-arm-none-eabi``

.. note::
    Note that these may require root access, via either ``sudo`` or entering a root terminal.
    See your distribution's package installation documentation for specific details.


Manjaro/Arch (and other Pacman-based systems)
---------------------------------------------



Optional Dependencies
---------------------

If you want to use Visual Studio Code, please refer to their `Installation Documentation for Linux <https://code.visualstudio.com/docs/setup/linux>`_ and follow the steps for your system.