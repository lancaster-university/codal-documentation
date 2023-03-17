Getting Started with CODAL
==========================

.. contents:: Contents

To start developing in C++ with CODAL and the Micro:bit you'll first need to ensure that you have followed the steps in :doc:`/guides/prerequisites` for
your operating system, and that you have a new project set up by following the steps in :doc:`/guides/codal-projects`

What is CODAL?
--------------

CODAL is the `Component Oriented Device Abstraction Layer` and is the set of controls through which you drive the micro:bit v2 devices (and friends!).
It sits in the slightly fuzzy zone between an Application Programming Interface (API) and an Operating System (OS) and shares some functions with both.

Traditional operating systems, such as those you would find on your compter, tablet, phone, and other devices run the show and present a nicely isolated
way for programs to interact with the user, hiding the complexity of running the system itself.
Programs run in a sort of fantasy world, where they own all the hardware and can do whatever they like with it (within reason) but in reality the OS is
hiding everything from them (except through special methods).

By contrast, a pure API would simply be a library which is compiled in with the applications themselves and becomes a part of the application during run
time.
Often these would then use OS methods to actually perform any useful task (although purely application-level APIs do exist in abundance!) 

What is a device abstraction?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Rather than having to write code for each and every specific device, it is often useful to hide the complexity of the actual device specifics
by wrapping or 'layering' it under a much more simple interface.
CODAL does this for most (if not all) of its devices, allowing programs written for one target, such as the micro:bit v2, also execute on other
CODAL-running platforms.

In general, this means that developers are presented with a set of functions, methods and classes which describe the functional operation of a device
rather than the required steps to actually realise these functions.
An extremely common case for this would be initialisation code; whereby from the application developers perspective, the device comes pre-initialised
and ready to go, but under this layer, the CODAL component (or components, for exceptionally complex hardware) are actually configuring the serial busses,
memory mappings, and maintenance tasks required to make this possible, all without the developer having to know.

.. note::
   Naturally, if a developer is porting CODAL to a new platform, they are much more likely to encounter the lower level parts of the system, but for just
   using CODAL, development is simplified.

.. figure:: static/missing-image.jpg
    :align: center
    
    The micro:bit v2 CODAL architecture, as a set of conceptual layers

Device 'drivers' are therefore composed of two parts; one which does the heavy lifting on the device to actually run the hardware, and another which presents
this device or class of devices to the application developer.
One good example of this is the :class:`codal::Serial` class, as it neatly hides if this is a hardware-backed serial device (with hardware-based buffering and
management circuitry) or if this is a software-based serial device, handled entirely within CODAL itself; or indeed, if this is a more exotic serial device, such
as the one we use for communication with a computer through the KL27 (See :doc:`/hardware/kl27` for info on the KL27) over our internal I2C connection, or the
line-based serial link in the Field Testing library for NMEA uBlox GPS devices (See :doc:`/libraries/codal-field-testing.rst`).

What is a "Component"?
^^^^^^^^^^^^^^^^^^^^^^
Components in CODAL devide up specific blocks of functionality, and these informally take on one or more of the following three aspects:

Device Drivers
   Whereby the function is that of configuring, running and responding to events for a specific piece of hardware.

Function Abstraction
   These

Utility-based Grouping
   These components group together a set of co-useful functions such that developers have all the relevant tools within a handful of objects or classes.
   This is the most pragmatic form of Component, whereby the decisions for what compose these groupings 

This might take the form of a `device driver`, whereby the function is that of running a piece of hardware, or may be a more logical seperation of function, such
as splitting or mixing audio.

- Bounded areas of function
   - A pragramatic approach
   - Where do C++ classes and objects fit in?

C++ for the micro:bit
^^^^^^^^^^^^^^^^^^^^^
- The ubit Object as an API
   - Reference diagram
   - List of common components
- Example minimal working app


- Programming model
   - Sync vs. Async calls

Concurrency
~~~~~~~~~~~
It is not uncommon to want to write programs that can do more than one thing at a time. For example, it takes quite a long time to scroll a message over the LED
matrix, so what if you want your program to do something else while this is happening?

Programs that do more than one thing at a time are called concurrent programs.

The runtime provides two ways you can achieve concurrency in your programs:

- Functions that may take a very long time to complete (e.g. :method:`codal::AnimatedDisplay.scroll`) often have "Async" versions
  (e.g. :method:`codal::AnimatedDisplay.scrollAsync`).
  These functions have the exact same behaviour as their counterparts, but don't wait for the effect to finish before allowing the user's program to continue.
  Instead, as soon as the function is called, the user's program carries on executing (and can go an do something else while the task is running in the background).

- Users can also make use of the runtime fiber scheduler. This lets you run parts of your program in the background, and share the processor on your micro:bit
  between those parts as they need it.
  In fact, whenever you write an event handler, the runtime will normally execute your handler in the background in this way, so that it reduces the impact on the
  rest of your program!
  The scheduler is a type of non-preemptive scheduler. This means that the runtime will never take control away from your program - it will wait for it to make a
  call to a runtime function that is blocking.
  All the functions that are blocking are listed as such in their documentation. You can create fibers at any time.

Events
~~~~~~

Computer programs execute sequentially - one line after another, following the logic of the program you have written. Sometimes though, we want to be able to determine
when something has happened, and write some code to decide what should happen in that case. For example, maybe you want to know when a button has been pressed, when
your micro:bit has been shaken, or when some data has been sent to you over the micro:bit radio. For these sorts of cases, we create a MicroBitEvent.

Creating Events
'''''''''''''''

Many components will raise events when interesting things occur. For example, 'MicroBitAccelerometer' will raise events to indicate that the micro:bit has be been shaken,
or is in freefall and 'MicroBitButton' will send events on a range of button up, down, click and hold events. Programmers are also free to send their own events whenever
they feel it would be useful. MicroBitEvents are very simple, and consist of only two numbers:

- :code:`source` - A number identifying the component that created the event.
- :code:`value` - A number unique to the source that identifies the event.

The documentation for each component defines its event source, and all the events it may generate, and also gives a name to these event values. For example, take a look
at the button documentation to see that the source MICROBIT_ID_BUTTON_A has the value '1', and an event MICROBIT_BUTTON_EVT_CLICK with the value '3' is generated when a
button is clicked.

Creating an event is easy - just create a MicroBitEvent with the source and value you need, and the runtime takes care of the rest:

.. code-block:: c++

   MicroBitEvent(MICROBIT_ID_BUTTON_A, MICROBIT_BUTTON_EVT_CLICK);

Feel free to create your own events lke this too. Just try to avoid using any source ID that is already used by the runtime! :-) See the messageBus page for a complete
table of the reserved source IDs.

Detecting Events
''''''''''''''''

The micro:bit runtime has a component called the MicroBitMessageBus, and its job is remember which events your program is interested in, and to deliver MicroBitEvents to
your program as they occur.

To find out when an event happens, you need to create a function in your program, then tell the message bus which event you want to attach this function to. This is known
as writing an event handler.

You write an event handler through the MicroBitMessageBus listen function.

.. todo::
   Needs a set of examples here. Also some mention of dynamic component IDs under some kind of 'advanced topics' section.

- Thread / Fiber model
   - Cooperative multi-tasking
   - Events, IDs and Messages
      - Handles and Callbacks



- C-like C++ coding style
   - Reference to Arduino
- Memory and Storage
   - Heap vs Stack
   - Managed objects
     - Strings :doc:`/memory-and-storage/managedstring`
   - Key/value Storage
   - micro:bit virtual disk
   - Persistent storage options

Build Tools
^^^^^^^^^^^

Under 'the hood', CODAL uses arm-gcc_ to compile source code into the binary we write to the board, and this compiler suite is driven by `GNU make_` from makefiles
created by CMake_.
However, the developer interface to this (and many other functions) is `build.py`, which is a Python_ script designed to launch CMake and other tools for you, greatly
simplifying the build, deployment and management of your CODAL projects.

.. note::
   The build script `build.py` may be replaced by an updated `codal.py` script in the future, as there are plans to merge `codal-bootstrap`_ into the main `codal` repository,
   to provide developers with a more streamlined build system, and an easy way to update local tooling with updates from The Foundation.
   While the timeline for this is not yet fixed, the changes from a developers perspective should be minimal, as `codal.py` is intended to replicate the functions and features
   available currently in `build.py`, and will just require some slight alterations in workflows to migrate.

.. _codal-bootstrap: https://github.com/lancaster-university/codal-bootstrap
.. _arm-gcc: https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/downloads
.. _GNU make: https://www.gnu.org/software/make/
.. _CMake: https://cmake.org/
.. _Python: https://www.python.org/

- CMake, python, make, etc. [x]
- build.py or codal.py [x]
   - List of useful flags and options [x]
- Libraries and project structure
   - Custom extra targets
   - Custom user libraries
- Running applications on real hardware
   - Flashing code to a board
   - Debugging via pyOCD or OpenOCD
- Build configurations
   - codal.json
   - target.json
   - Set/Unset syntax for `config{}` blocks
   - Common/known config variables
      - Examples for common cases
         - DMESG settings
         - Flash erase settings
- The Edge Connector
   - GPIO access via the uBit object
      - Digital / Analog / PWM
   - Serial Communication
      - UART / Serial -> Software vs. Hardware
      - SPI
      - I2C -> Internal vs External busses
         - On-board devices
- The Radio
   - 2.4Ghz packet radio -> protocol options
   - Bluetooth radio
   - BLE bluetooth mode

Projects and Guides
^^^^^^^^^^^^^^^^^^^
- "Disco Lights" -> audio pipeline and display
- "Hot Potato" -> accelerometer, timers and audio
- "Alien Scanner" -> radio, display, buttons, audio


Holding Zone (Temp)
-------------------

::

    #include "MicroBit.h"

    // The Micro:bit control object
    MicroBit uBit;

    // Our main function, run at startup
    int main() {
        // Set up the uBit object (needs only to be done once on startup)
        uBit.init();

        // Scroll some text on the display
        uBit.display.scroll( "Hello, World!" );

        // By calling this we allow CODAL to continue to run when we've exited
        release_fiber();
    }

