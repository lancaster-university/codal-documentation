PacketBuffer
============

The MicroBitRadio class provides direct micro:bit to micro:bit communication.
It is often beneficial in both wired and wireless communication protocols to send and receive data in a raw format, viewed as an ordered sequence of bytes.
This class provides a basic set of functions for the creation, manipulation and accessing of a managed type for byte arrays used to hold network data packets.

.. note::
    This is a managed type. This means that it will automatically use and release memory as needed. There is no need for you to explicitly free or release memory
    when your done - the memory will be freed as soon as the last piece of code stops using the data.
    Creating PacketBuffers

PacketBuffers are simple to create - just create them like a variable, and provide the size (in bytes) of the buffer you want to create.

.. code-block:: c++

    PacketBuffer b(16);

Alternatively, if you already have an array of bytes allocated, then you can simply refer to that using a slightly different form:

.. code-block:: c++

    uint8_t data[16];
    PacketBuffer b(data,16);

Manipulating PacketBuffers
--------------------------

Once created, the data inside PacketBuffers can be freely changed at any time. The simplest way to do this is through the array operators [ and ].

You can read or write bytes to the buffer by simply dereferencing it with square bracket.

For example: to create, set and send a PacketBuffer on the micro:bit radio, you could do the following:

.. code-block:: c++

    PacketBuffer b(2);
    b[0] = 255;
    b[1] = 10;

    uBit.radio.datagram.send(b);

PacketBuffers can also be assigned a value:

.. code-block:: c++

    PacketBuffer b;
    b = uBit.radio.datagram.recv();

If you need more granular access, the getBytes function provides direct access to the memory buffer, presented as a byte array:

.. code-block:: c++

    PacketBuffer b(16);
    uint8_t *buf = b.getBytes();

    memcpy(buf, "HI", 2);

Finally, it is also possible to extract the received signal strength of a packet from a PacketBuffer.

This can provide both a rough indication of the reliability of the link, and a crude but moderately effective mechanism to estimate the distance between two micro:bits.

.. code-block:: c++

    PacketBuffer b;
    b = uBit.radio.datagram.recv();

    uBit.display.scroll(b.getRSSI());
