uBit.display
============

The `codal::Display` class is a general purpose device driver for controlling LED matrix displays.
LED matrix displays are simple, inexpensive devices that use a single LED as a display pixel. They therefore
tend to be of relatively low resolution, but often provide visually attractive displays due to the high coherence and brightness
of the LEDs.

LEDs in matrix displays are connected to general purpose I/O (GPIO) pins on CPU. Although they *could* be connected such that each
LED has its own GPIO pin, this is not usually the case, as the scarce resource of GPIO pins would soon be used up.  For example,
on the micro:bit, the LED matrix has 25 LEDs. If this required 25 GPIO pins, then there would be none left for anything else!

Instead, these LEDs are controlled by 12 GPIO pins. Three of those pins provide power to LEDs, the other
nine provide a route to ground. The pins that source power are called **rows**. The pins that sink power are called **columns**.
The following diagram shows how the 5x5 grid is connected into 3 logical 'rows' and 9 'columns':

.. figure:: assets/display/light-sensing.png
    :align: center
    
    The format used here is: "ROW.COLUMN"

So, if we wanted to light up the middle LED, we would need to put a HIGH voltage (logic 1) on row 2, and a LOW voltage (logic 0) on column 3. Notice that when row 2 is
HIGH, we the value we write to the 9 column pins affect all of the LEDs 2.1 to 2.7, without affecting any of the LEDS on row 1 or row 3. Sharing GPIO pins in this way is known as multiplexing.
Moreover, if we scan through the different rows fast enough - faster than the eye can see - then we can provide the illusion of all the LEDS being on at the same time! This is a technique
known as *persistence of vision*... and was also the same basis of the very first TV sets (although that did not use LEDs!).

In it's normal mode, the display will update every 18ms (55 Hz). If the display is in light saving mode the period is changed to 15ms (66 Hz).

Capabilities
------------

The MicroBitDisplay class provides a driver for a general purpose matrix display, and also several high level features that make creating animations and visual effects on the
micro:bit LED display easy and fun! This class lets you:

- Control the LED matrix on the micro:bit.
- Use an optimised typeface (font) so you can show upper and lower case letters, numbers of symbols on the display.
- Set Display wide or *per-pixel* brightness control up to 256 levels per pixel.
- Create, move, paste and animate images.
- Scroll and print images and text.
- Access the screen buffer directly, so you can manipulate individual pixels.

Using the Display
-----------------

When using the uBit object, the display is automatically set up, and ready for you to use. Use any or all of the functions listed in the API section below to create effects on the
LED display. Here are a few examples to get you started though!

Scrolling Text
^^^^^^^^^^^^^^
Simply use the scroll function to specify the message you want to scroll, and sit back and watch the result. The message you provide will be scrolled, pixel by pixel across the display from right to left.
If you take a look at the documentation for the scroll function in the API below, you will notice that you can also specify the speed of the scroll as an optional final parameter. The lower the delay, the
faster your text will scroll across the screen.

::

    uBit.display.scroll("HELLO!");
    uBit.display.scroll("HELLO!", 100);

Notice that you can also scroll numbers (either constants of variables).

::

    int c = 42;
    uBit.display.scroll(c);

Printing Text
^^^^^^^^^^^^^
Sometimes it is better to show the letters/numbers in turn on the screen rather than scrolling them. If you want to do this, the 'print' function has exactly the same parameters as 'scroll', but
with this behaviour.  e.g

::

    uBit.display.print("HELLO!");
    uBit.display.print("HELLO!", 100);
    uBit.display.print(42);

Do notice that print behaves slightly differently if you provide a single character or numeric digit though. if you do this, the value you provide will stay on the screen until you explicitly
change the screen. If you ask the runtime to print a string with two or more characters, then each will appear in turn, then disappear. e.g. try this and you will find it stays on the screen::

    uBit.display.print(7);

Showing Images
^^^^^^^^^^^^^^
It is also possible to print and scroll bitmap images on the display. Images are represented in the runtime by using a [MicroBitImage](../data-types/image.md). These can easily be created, just as
you create any variable. Once created, you can then provide them as a parameter to the scroll and print functions. Unlike the text based animation functions, you can also specify exactly
where in the screen you would like the image to appear - and you can even treat pixel values of zero as transparent if you like!
See the [MicroBitImage page](../data-types/image.md) for more details on images, but here are a few simple examples

::

    // show your smiley on the screen...
    MicroBitImage smiley("0,255,0,255, 0\n0,255,0,255,0\n0,0,0,0,0\n255,0,0,0,255\n0,255,255,255,0\n");
    uBit.display.print(smiley);

::

    // make your smiley peep up from the bottom of the screen...
    MicroBitImage smiley("0,255,0,255, 0\n0,255,0,255,0\n0,0,0,0,0\n255,0,0,0,255\n0,255,255,255,0\n");
    for (int y=4; y >= 0; y--)
    {
        uBit.display.image.paste(smiley,0,y);
        uBit.sleep(500);
    }

::
    
    // scroll your smiley across the screen...
    MicroBitImage smiley("0,255,0,255, 0\n0,255,0,255,0\n0,0,0,0,0\n255,0,0,0,255\n0,255,255,255,0\n");
    uBit.display.scroll(smiley);


Running in the Background...
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
By now you have probably noticed that the scroll, print and animate functions all wait for the effect requested to finishes before returning. This is by design, to allow you to easily synchronise your programs.
However, sometimes you want to launch an effect, and let it run in the background while your program does something else. For this, you can use the *Async* variations of the scroll, print and animate functions.
These all have identical parameters and capabilities, but will return immediately. Try some of the examples above with their Async equivalents to understand this different behaviour.  For example:

::

    // scroll your smiley across the screen, without waiting for it to finish...
    MicroBitImage smiley("0,255,0,255, 0\n0,255,0,255,0\n0,0,0,0,0\n255,0,0,0,255\n0,255,255,255,0\n");
    uBit.display.scrollAsync(smiley);


Changing Display Mode
^^^^^^^^^^^^^^^^^^^^^

The MicroBitDisplay class supports either on/off LED display, or displays where each pixel has an individual brightness value between 0 and 255. The former costs much less processor time and battery power to
operate, so it is the default. The latter does provide more useful effects though, so you can change between these modes by using the  'setDiplayMode' function. Valid values are:

DISPLAY_MODE_BLACK_AND_WHITE
    Each pixel can be just on or off. The brightness of all pixels is controlled by the setBrightness function.

DISPLAY_MODE_BLACK_AND_WHITE_LIGHT_SENSE
    Each pixel can be just on or off, and the display driver will also sense the ambient brightness from the LEDs.

DISPLAY_MODE_GREYSCALE
    Each pixel can independently have 256 levels of brightness.

For example:

::

    // show a smiley with bright eyes!
    MicroBitImage smiley("0,255,0,255, 0\n0,255,0,255,0\n0,0,0,0,0\n32,0,0,0,32\n0,32,32,32,0\n");
    uBit.display.setDisplayMode(DISPLAY_MODE_GREYSCALE);
    uBit.display.print(smiley);

Accessing the Display Buffer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The memory buffer that is used to drive the LEDs is itself a [MicroBitImage](../data-types/image.md). This means that you can also access and call any of the functions listed in the [MicroBitImage API documentation](../data-types/image.md)
directly on the display buffer. Examples here include setPixelValue, as illustrated below, but read the above documentation link for full details.

::

    // set a single pixel by co-ordinate
    uBit.display.image.setPixelValue(2,2,255);

Other Useful Functions
^^^^^^^^^^^^^^^^^^^^^^

- 'clear' will clear the screen immediately.
- 'stopAnimation' will terminate any on-going print, scroll or animate functions.
- 'setBrightness' lets you set the overall maximum brightness of the display, as a value between 1 and 255.
- 'enable' and 'disable' turn on and off the display. When disabled, you can reuse many if the GPIO pins. See the [MicroBitIO](/ubit/io.md) class for more information.
- 'rotateTo' even lets you specify the orientation of the display - in case you need to use your micro:bit the wrong way up. :-)
- 'readLightLevel' runs the LEDs backwards as photodiodes and tells you how bright your room is... see [Light Sensing](/extras/light-sensing.md) for more info!

Useful Methods
--------------

As the Display class includes quite a lot of functionality, the full API reference (as can be found here: :class:`codal::Display`, and here: :class:`codal::AnimatedDisplay`) can be quite daunting,
so here are a collection of hand-picked methods you might find as the most interesting.

.. doxygenfunction:: codal::Display::getWidth
.. doxygenfunction:: codal::Display::getHeight
.. doxygenfunction:: codal::Display::setBrightness
.. doxygenfunction:: codal::Display::getBrightness
.. doxygenfunction:: codal::Display::enable
.. doxygenfunction:: codal::Display::screenShot

Synchronous Methods
^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: codal::AnimatedDisplay::print(Image i, int x = 0, int y = 0, int alpha = 0, int delay = 0)
.. doxygenfunction:: codal::AnimatedDisplay::print(ManagedString s, int delay = 400)
.. doxygenfunction:: codal::AnimatedDisplay::printChar
.. doxygenfunction:: codal::AnimatedDisplay::scroll(Image image, int delay = 120, int stride = -1)
.. doxygenfunction:: codal::AnimatedDisplay::scroll(ManagedString s, int delay = 120)

Asynchronous Methods
^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: codal::AnimatedDisplay::printAsync(Image i, int x = 0, int y = 0, int alpha = 0, int delay = 0)
.. doxygenfunction:: codal::AnimatedDisplay::printAsync(ManagedString s, int delay = 400)
.. doxygenfunction:: codal::AnimatedDisplay::printCharAsync
.. doxygenfunction:: codal::AnimatedDisplay::scrollAsync(Image image, int delay = 120, int stride = -1)
.. doxygenfunction:: codal::AnimatedDisplay::scrollAsync(ManagedString s, int delay = 120)