ManagedString
=============

ManagedString represents a sequence of characters (a 'string'), and is tracked automatically by CODAL.

A string is simply a sequence of characters such as "joe" or "micro:bit".
In the C language, the end of the string is marked by a special character (a NULL character, commonly with the value zero).

Simple strings are often represented as literal character arrays:

.. code-block:: c++

    uBit.display.scroll("HELLO");

Which is almost exactly the same as:

.. code-block:: c++

    char message[6] = {'H', 'E', 'L', 'L', 'O', 0};
    uBit.display.scroll(message);

Although fantastically simple, strings of this form are well known to lead to memory leaks and be sources of bugs in code (especially when the programmers are still learning!).

As a result, most modern high level languages such as Java, C#, Javascript and TouchDevelop do not use strings of this format. Instead, they provide code that is capable of
ensuring strings remain safe.

ManagedString provides this equivalent functionality for the micro:bit, as a building block for higher level languages. However, it can also makes programming the micro:bit in
C easier too!

.. note::
    This is a managed type. This means that it will automatically use and release memory as needed. There is no need for you to explicitly free or release memory when your done;
    the memory will be freed as soon as the last piece of code stops using the data.

Creating Strings
----------------

Images are simple to create - just create them like a variable, and provide the text or number you would like to build the string from.

For example:

.. code-block:: c++

    ManagedString hi("HELLO");
    ManagedString message("micro:bit");
    ManagedString n(42);

The runtime will also create a ManagedString for you from a number or quoted literal anytime a function requires a ManagedString.

In the example below, even though the scroll function of MicroBitDisplay expects a ManagedString, it is totally fine to pass a literal value in quotes or a number (or in fact,
any parameter that is listed in the API section as a legal constructor will work):

.. code-block:: c++

    ManagedString hi("HELLO");
    ManagedString message("micro:bit");
    ManagedString n(42);

    // All these calls are legal:
    uBit.display.scroll(hi);
    uBit.display.scroll(n);
    uBit.display.scroll("THANKS!");

Manipulating Strings
--------------------

ManagedStrings are immutable, meaning that once created, they cannot be changed. However, you can join them, search them, extract characters from them and create other strings!

The micro:bit runtime makes use of operator overloading to keep this easy to use.

In other words, we make use of the :code:`= + < >` and :code:`==` operators to let you easily assign and compare strings.

Although this may sound complex, it is easy once you see how to do it.

Here is how you would join together more than one string, and assign it to a new one:

.. code-block:: c++

    ManagedString hi("HELLO");
    ManagedString message("micro:bit");
    ManagedString space(" ");
        
    ManagedString s = hi + space + message;

    // This would say "HELLO micro:bit" on the LED display.
    uBit.display.scroll(s);

You can compare strings (alphabetically) in a similar way:

.. code-block:: c++

    ManagedString hi("HELLO");
    ManagedString message("micro:bit");

    if (hi == message)
        uBit.display.scroll("SAME");

    if (hi < message)
        uBit.display.scroll("LESS");

    if (hi > message)
        uBit.display.scroll("MORE");

You can also determine the length of a string, extract parts of strings, retrieve individual characters at a given index or convert a ManagedString to a C-style character
array using the length, substring, charAt and toCharArray functions respectively.