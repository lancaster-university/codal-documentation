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

Setting up a Visual Studio Code Environment
-------------------------------------------

After following the instructions above, you should be able to compile and run your CODAL applications. However, Visual Studio Code will not yet be
configured correctly, unless you've done this sort of stuff before! It's a wise idea to do this as it will provide syntax highlighting and other
features provided by Intellisense which can make your programming life easier!

Firstly, you'll want to install the ``CMake`` and ``C/C++`` extensions. You may get a prompt to install these automatically, or alternatively, click
the ``Extensions`` icon on the left to search and install them.

Once these have installed and Visual Studio Code has re-indexed your code, you might see an error being highlighted in the ``main.cpp`` file. This
is just because we haven't yet configured the correct compiler. Press ``F1`` (or ``View > Command Palette``), and type ``configure``. Select the
``CMake: Configure`` option. You then want to select the ``arm-none-eabi`` compiler.

Make sure to click accept if you receive a prompt asking permission for CMake to configure Intellisense.

Debugging in Visual Studio Code
-------------------------------

Now, you're able to create and run CODAL applications, but you're unable currently to debug your applications directly within Visual Studio Code.
Debugging is an important part of software development, as it allows you to find errors which might be hiding within your code that are tricky to
spot otherwise. It allows you to step through your code, which means you can look at the data and memory of your program after each individual line
of code is ran, as well as to set breakpoints, which tell your code to pause once it reaches a certain line of code, until you hit resume manually.

You can find out more details about debugging within Visual Studio Code on their `website <https://code.visualstudio.com/docs/editor/debugging>`_.

To set this up, we need to install a debugger for your hardware. This is a program which allows Visual Studio Code to connect through to your
physical device (e.g. micro:bit) to send and receive the data it needs to operate. Download the ``Cortex-Debug`` extension for Visual Studio Code.
This is a debugger which provides support for the type of devices which run CODAL.

Next, make sure you have downloaded and installed either pyOCD or OpenOCD, as instructed within :doc:`/guides/prerequisites`.

Then, you need to `download this configuration file <https://raw.githubusercontent.com/lancaster-university/microbit-v2-samples/master/.vscode/launch.json>`.
This is a file which sets up debugging configurations within Visual Studio Code. This file is specifically designed for debugging micro:bit v2 devices,
and so therefore you will need to modify this file as needed if you are using a different device. Consult the documentation for your specific device
if this is the case.

Place the file you have downloaded into the ``.vscode`` folder inside your application folder. If this folder doesn't exist, you should manually create it.

At this point, you can switch to the ``Run and Debug`` panel, on the left. You should see a drop-down box at the top of the panel, containing
``micro:bit PyOCD Cortex Debug`` and ``micro:bit OpenOCD Cortex Debug``. These are the configurations you installed by downloading the ``launch.json`` file.
You should select the appropriate option depending on which debugger you installed.

Next, ensure your micro:bit is plugged into your computer, and hit the green arrow to start debugging! This will make sure your program is compiled and
copied to your micro:bit, meaning you can skip the process of running the ``build.py`` script manually.

To test out the debugger, try placing a breakpoint. You can do this by clicking in the space to the left of the corresponding line number in the code editor.
Restart your program, and see if your program pauses at the breakpoints you set!

.. note::
    Unfortunately, sometimes due to a variety of reasons, attempting to start the debugger can result in errors. Much of the time this can be resolved by
    trying again, reconnecting your device to your computer, or restarting your computer entirely.

Older Projects
--------------

Older projects had the build tools baked into the source code, but as ``codal-bootstrap`` maintains backwards compatibility with the older tools, they
should operate in much the same way as described here, with the exception of the initial download phase.