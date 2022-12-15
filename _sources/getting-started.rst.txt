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
- Programming model
   - Sync vs. Async calls
- Example minimal working app
- The ubit Object as an API
   - Reference diagram
   - List of common components
- Thread / Fiber model
   - Cooperative multi-tasking
   - Events, IDs and Messages
      - Handles and Callbacks
- C-like C++ coding style
   - Reference to Arduino
- Memory and Storage
   - Heap vs Stack
   - Managed objects
   - Key/value Storage
   - micro:bit virtual disk
   - Persistent storage options

Build Tools
^^^^^^^^^^^
- CMake, python, make, etc.
- build.py or codal.py
   - List of useful flags and options
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

