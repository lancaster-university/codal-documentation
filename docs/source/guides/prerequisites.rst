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
- `pyOCD <https://pyocd.io/>`_ *or* `OpenOCD <https://openocd.org/>`_ to use on-chip debugging


Windows Instructions
====================

Windows Package Manager (winget) is preinstalled on Windows 11 and up-to-date versions of Windows 10. You can check if it is installed on your system by checking if you can run the ``winget`` command in your terminal.

.. note::
    To open a terminal/command prompt window, right click on the start button and click ``Windows PowerShell`` if you're using Windows 10, or ``Windows Terminal`` if you're using Windows 11.

If you do not have Windows Package Manager installed, you should manually download and install the dependencies listed above. Otherwise, follow the installation instructions below.

Using Windows Package Manager
-----------------------------

The following commands will install each component. If you have any of the components installed already, you will not need to run its install command below.

Whilst some of these will install silently in the background, you may need to manually read and accept any installation prompts which occur.

Python:
  ``winget install --id=Python.Python.3 -e``

ARM GUI Toolchain:
  ``winget install --id=Arm.GnuArmEmbeddedToolchain -e``

Git:
  ``winget install --id=Git.Git -e``

CMake:
  ``winget install --id=Kitware.CMake -e``

Visual Studio Code (optional):
  ``winget install --id=Microsoft.VisualStudioCode -e``

Additional Dependencies
-----------------------
You will also need to install Ninja, which is a build tool allowing your code to be compiled. To install this, ensure you have installed Python successfully and run the following: ``python -m pip install ninja``.

If you'd like to use debugging, note that neither pyOCD nor OpenOCD are available through the Windows Package Manager, though you can install pyOCD using ``python -m pip install -U pyocd``.


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