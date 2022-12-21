MicroBitImage
=============

MicroBitImage represents a bitmap picture.
Images can be of any size, and each pixel on the image has an individual brightness value in the range 0 - 255.
Once created, this class also provides functions to undertake graphical operations on that image, including setting pixels, clearing the image, pasting one image onto
another at a given position, shifting the content of an image and comparing and copying images.

It is designed to work with the MicroBitDisplay class to allow the creation of animations and visual effects.

.. note::
    This is a managed type. This means that it will automatically use and release memory as needed. There is no need for you to explicitly free or release memory when
    your done - the memory will be freed as soon as the last piece of code stops using the data.


Creating Images
---------------

Images are easy to create - just create them like a variable, but provide the details requested in one of the constructor function shown below. This may sound complex,
but is quite simple when you get used to it. For example, to create a blank, 2x2 image:

.. code-block:: c++

    MicroBitImage image(2,2);

You can also create one from a text string that represents the pixel values that you want. This is a really easy way to create icons and emojis in your code.

The string constructor for a MicroBitImage takes the form of a series of comma separate values. Each value is the brightness of a pixel, starting at the top left of
your image and working to the right. Whenever you put a newline character \n in your string, this moves onto a new line of pixels.

So to create a 3x3 image that is a picture of a cross, you might write:

.. code-block:: c++

    MicroBitImage cross("0,255,0\n255,255,255\n0,255,0\n");

Manipulating Images
-------------------

Once you have created an image, you can use any of the functions listed in the API below to change that image. For example, you can use setPixelValue to change an
individual pixel.

In the example below, you can see how to change the centre pixel in our cross image created earlier:

.. code-block:: c++

    cross.setPixelValue(1,1,0);


.. note::
    Co-ordinates are indexed from zero, with the origin (0,0) being at the top left of the image.

You can print characters onto an image...

.. code-block:: c++

    MicroBitImage image(5,5);
    image.print('J');

You can also paste the content of one image onto another - either at the origin, or somewhere else:

.. code-block:: c++

    MicroBitImage image(5,5);
    image.paste(cross);

    MicroBitImage image(5,5);
    image.paste(cross, 1, 1);

and of course, you can display your image on the LEDs using the MicroBitDisplay class:

.. code-block:: c++

    MicroBitImage image(5,5);
    image.paste(cross);
    uBit.display.print(image);


Comparing and Assigning Images
------------------------------

MicroBitImage is a managed type, so you can pass images as parameters to functions, store then and assign them to other variables without having to worry about memory leaks.

The type will count the number of times it is used, and will delete itself as soon as your image is not used anymore.

You can assign images just like any other variable. So this is perfectly permitted, and memory safe:

.. code-block:: c++

    MicroBitImage cross("0,255,0\n255,255,255\n0,255,0\n");
    MicroBitImage img;

    img = cross;
    uBit.display.print(img);

As is this:

.. code-block:: c++

    void doSomething(MicroBitImage i)
    {
        uBit.display.print(img);
    }

    int main()
    {
        MicroBitImage cross("0,255,0\n255,255,255\n0,255,0\n");

        doSomething(cross);
    }

You can also compare images:

.. code-block:: c++

    MicroBitImage cross("0,255,0\n255,255,255\n0,255,0\n");
    MicroBitImage img;

    img = cross;

    if (img == cross)
        uBit.display.scroll("SAME!");


Storing Images in Flash Memory
------------------------------

The micro:bit is a very constrained device in terms of Random Access Memory (RAM). Unlike modern PCs that typically have over 4 Gigabytes of RAM (around four thousand
million bytes!), the micro:bit has only 16 Kilobytes (16 thousand bytes!), and if you take a look at the memory map, you will see most of this is already committed to
running the Bluetooth stack.

By default, any MicroBitImage you create will be stored in this precious RAM, so that you have the ability to change it. However, it is not uncommon to have read-only
images. in this case, we can store the image in FLASH memory (the same place as your program), of which the micro:bit has 256 Kilobytes.

Should you want to create an store a constant image in flash, you can do so using the following constructor, it is a little more complicated, but can save you memory:

- The array of bytes should always start with 0xff, 0xff - which tell the runtime that this image is stored in FLASH memory.
- The next number should be the width in pixels, followed by a zero.
- The next number should be the height in pixels, followed by a zero.
- The following bytes are then individual pixel brightness values, starting at the top left, then working left to right, top to bottom until the bottom right corneris reached.

.. note::
    If you create an image this way, none of the functions to change the content will work on that image (e.g. setPixelValue, paste, etc).

.. code-block:: c++

    const uint8_t heart[] __attribute__ ((aligned (4))) = { 0xff, 0xff, 10, 0, 5, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0};

    MicroBitImage i((ImageData*)heart);
    uBit.display.animate(i,5);


