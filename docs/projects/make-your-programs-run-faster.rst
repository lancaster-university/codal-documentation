Make Your Programs Run Faster
=============================

Maybe you tried running some Python scripts on your microcontroller
board before, and wondered if they could be made to run any faster?

That is very well possible, and not only by a little - but often by a
large factor!

Consider the following minimalistic task: We want to make our display
LEDs blink, the first LED as fast as we can count to 4096, the second
LED only half as fast as the first LED, the third LED only half as fast
as the second LED and so on. If the user presses the "A"-button, the
counting should stop, until the "B"-button is pressed.

The following little Python program would do that for us:

.. code:: python

   from microbit import *

   imgbuf = bytearray(bytes(25))

   c = 0
   while True:
       c += 1
       if c & 0xfff != 0:
           continue
       
       if button_a.is_pressed():
           while True:
               if button_b.is_pressed():
                   break
               sleep(100)
       
       i = c >> 12
       for p in range(25):
           imgbuf[p] = -(i & 1)
           i >>= 1
       display.show(Image(5, 5, imgbuf), delay=0, wait=False)

Notice how this little Python program is mostly busy with just
incrementing variable "c", and only every 4096 counts, it will check for
button presses and update the display.

If you run this program on a Micro:Bit v2, the first LED will blink
about every second or so, and the following LEDs with ever halving
frequency.

Now try running the following C++ program, which does the same, and is
very similar to above Python program, on the same microcontroller board:

.. code:: cpp

   #include "MicroBit.h"
   #include "Image.h"

   MicroBit uBit;

   int main() {
       uBit.init();
       uBit.display.setDisplayMode(DISPLAY_MODE_BLACK_AND_WHITE);
       
       uint32_t c = 0;
       while(true) {
           c += 1;
           if ((c & 0xfff) != 0) {
               continue;
           }
           
           if (uBit.buttonA.isPressed()) {
               while(true) {
                   if (uBit.buttonB.isPressed()) {
                       break;
                   }
                   uBit.sleep(100);
               }
           }
           
           unsigned int i = c >> 12;
           uint8_t * img_buf_p = uBit.display.image.getBitmap();
           uint8_t * img_buf_end = img_buf_p + 25;
           while (img_buf_p < img_buf_end) {
               *img_buf_p++ = -(i & 1);
               i >>= 1;
           }
       }
   }

If you run this, you will notice how several LEDs will blink so fast
that your eye can hardly see them going on or off. And if you count
how many LEDs after the first LED the blinking frequency has been halved
so many times that this LED now blinks with about the same speed as the
first LED with above Python example, you can easily determine an
approximate speed-up: For example, if the blink frequency of the 8th LED
is now about as fast as the 1st LED before, then the speed-up is around
a factor of 2^7 = 128.

The reason for this is simply that Python is an interpreted language,
where even a simple operation like incrementing a variable requires many
"machine instructions" on the microcontroller to execute.

The C++ version, in contrast, is compiled first into a CPU instruction
set specific Assembler language, which is then translated into binary
"machine code", which the microcontroller can execute directly - and
incrementing an integer variable there is a single instruction.

When To Expect Large Speed-Up From Using C++
============================================

Generally speaking, if your software spends a lot of time outside of
calling "system" or "library" functions that were implemented in
efficient programming languages, then you can expect large speed-up
factors from using such languages instead of interpreted ones.

Also, sometimes an existing run-time environment, library or operating
system you have to use while running a certain programming language,
will simply not allow you to implement a more efficient way to solve a
given task. Looking once more at the above example, see how the Python
program need to create a new instance of class "Image" every time it
wants to update the display. That within the language interpreter
requires allocating memory for the new instance, initializing it with
values, then copying those values into the frame buffer, only to then
discard the "Image" instance again. The C++ version, on the other hand,
can just obtain a pointer to the anyway existing frame buffer of the
display driver, and directly write values there - no memory allocation
required, also no second copy and deallocation.

Can I Run My Software Even Faster?
==================================

If you directed a high-speed camera on the LEDs while above C++ example
runs, you would notice that the display actually does not change as fast
as the new values are written to the frame buffer. This is because the
MicroBitDisplay implemented as part of the Codal layer only updates the
actual I/O pins driving the LEDs about 60 times per second - not every
time the frame buffer content changes! Usually, that is a very
reasonable approach - after all, humans would not notice faster updates
with their eyes, anyway.

But let's assume you wanted to switch the LEDs as quickly as possible,
for whatever reason. Then you could circumvent the Codal software layer,
and implement your own display driver. You can do that in C++, as well,
but it involves learning about the I/O registers and how to use them.

Can I Run My Software Even Faster Than Possible In C++?
=======================================================

Compilers are very good these days in creating highly optimized
Assembler code, so "going more low level" by writing Assembler directly
will not often gain you a further speed-up.

But there are exceptions to this: For example, many CPUs support special
machine instructions to speed-up certain algorithms. Like AES
encryption. A compiler will not likely automatically use such
instructions if you needed to implement such an algorithm, so you would
have to write Assembler directly to gain the possible speed-up from
using them. Which can be very high - again a factor of 10 or more can
often be achieved by using specialized machine instructions tailored to
a certain algorithm.

Can I Run My Software Even Faster Than Possible In Assembler?
=============================================================

If even writing Assembler is not sufficient to run your task fast enough,
then you run out of "software" options.

But you can still look for additional hardware support! One approach
would be to use specialized, non-general-purpose processing units, such
as for example GPUs, which excel at running one sequence of instructions
on many many data at the same time.

Or you can use a "Field Programmable Gate Array" (FPGA), which
essentially allows you to arrange basic building blocks of processors,
down to the level of single NAND-gates, into specialized processing
units for your task.

If even FPGAs cannot do fast enough what you need to do, then you run
out of hardware options that are easy to buy, but you theoretically can
design "Application Specific Integrated Circuits" (ASICS), which when
manufactured as hardware, can again be a lot faster (and more efficient)
than FGPAs for the same task.

And yes, there are languages dedicated to the desciption of hardware,
for example "VHDL" or "Verilog", and using those you can simulate what
your hardware would do. But maybe that is for you to try another time?
