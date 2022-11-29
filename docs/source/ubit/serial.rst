uBit.serial
===========

Serial communication provides a simple way to exchange a series of bytes between one computer and another.  The runtime's implementation of serial is general purpose and supports a number of different modes. It has a circular buffer for both the reception and transmission of data, and provides notifications to the user through the MessageBus.

By default, the baud rate for MicroBitSerial is `115200` and has very little overhead up until
it is used to `send()` or `read()`, at which point buffers are allocated in order
to accommodate incoming or outgoing data.

MicroBitSerial inherits from mbeds' [`RawSerial`](https://developer.mbed.org/users/mbed_official/code/mbed/docs/252557024ec3/classmbed_1_1RawSerial.html)
class, which exposes a lightweight version of `printf()` and incurs minimal overhead
as MicroBitSerial's buffers will not be allocated.

The MicroBitSerial class supports multithreaded operation, ensuring that only
one fiber can access the Serial port at a time.

The USB interface on the micro:bit is the [KL26Z](https://www.mbed.com/en/development/hardware/prototyping-production/daplink/daplink-on-kl26z/#Updating_your_DAPLink_firmware).

.. note::
    On Mac OSX and Linux Serial communication works out of the box, however on Windows an additional
    **[driver](https://developer.mbed.org/handbook/Windows-serial-configuration)** is required.

.. warning::
    The baud rate is shared across all instances of MicroBitSerial (this is enforced in hardware).

Serial Modes
^^^^^^^^^^^^

There are three modes of operation for all `send()` or `read()` calls:

ASYNC
    Returns immediately after fetching any available data for a given call

SYNC_SPINWAIT
    Synchronously access the serial port until the selected operation is complete.
    This mode will lock up the processor, and isn't recommended if multiple fibers are in use.

SYNC_SLEEP
    Blocks the current fiber until the selected operation is complete. This mode cooperates with the
    Fiber scheduler, and should be used in a multi-fiber program.

Serial Debug
^^^^^^^^^^^^

In MicroBitConfig.h, the configuration option `MICROBIT_DEBUG` can be used to activate serial debugging
for many of the components in the runtime.