
.. _program_listing_file_libraries_codal-core_source_types_ManagedString.cpp:

Program Listing for File ManagedString.cpp
==========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_types_ManagedString.cpp>` (``libraries/codal-core/source/types/ManagedString.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   ManagedString s("abcd");
   ManagedString p("efgh")
   
   display.scroll(s + p) // scrolls "abcdefgh"
   /*
   The MIT License (MIT)
   
   Copyright (c) 2017 Lancaster University.
   
   Permission is hereby granted, free of charge, to any person obtaining a
   copy of this software and associated documentation files (the "Software"),
   to deal in the Software without restriction, including without limitation
   the rights to use, copy, modify, merge, publish, distribute, sublicense,
   and/or sell copies of the Software, and to permit persons to whom the
   Software is furnished to do so, subject to the following conditions:
   
   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.
   
   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
   THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
   DEALINGS IN THE SOFTWARE.
   */
   
   #include <string.h>
   #include <stdlib.h>
   
   #include "CodalConfig.h"
   #include "ManagedString.h"
   #include "CodalCompat.h"
   
   using namespace codal;
   
   #define REF_TAG REF_TAG_STRING
   #define EMPTY_DATA ((StringData*)(void*)emptyData)
   
   REF_COUNTED_DEF_EMPTY(0, 0)
   
   
   
   void ManagedString::initEmpty()
   {
       ptr = EMPTY_DATA;
   }
   
   void ManagedString::initString(const char *str, int len)
   {
       // Initialise this ManagedString as a new string, using the data provided.
       // We assume the string is sane, and null terminated.
       ptr = (StringData *) malloc(sizeof(StringData) + len + 1);
       REF_COUNTED_INIT(ptr);
       ptr->len = len;
       memcpy(ptr->data, str, len);
       ptr->data[len] = 0;
   }
   
   ManagedString::ManagedString(StringData *p)
   {
       if(p == NULL)
       {
           initEmpty();
           return;
       }
   
       ptr = p;
       ptr->incr();
   }
   
   StringData* ManagedString::leakData()
   {
       StringData *res = ptr;
       initEmpty();
       return res;
   }
   
   ManagedString::ManagedString(const int value)
   {
       char str[12];
   
       itoa(value, str);
       initString(str, strlen(str));
   }
   
   ManagedString::ManagedString(const char value)
   {
       char str[2] = {value, 0};
       initString(str, 1);
   }
   
   
   ManagedString::ManagedString(const char *str)
   {
       // Sanity check. Return EmptyString for anything distasteful
       if (str == NULL || *str == 0)
       {
           initEmpty();
           return;
       }
   
       initString(str, strlen(str));
   }
   
   ManagedString::ManagedString(const ManagedString &s1, const ManagedString &s2)
   {
       // Calculate length of new string.
       int len = s1.length() + s2.length();
   
       // Create a new buffer for holding the new string data.
       ptr = (StringData*) malloc(sizeof(StringData) + len + 1);
       REF_COUNTED_INIT(ptr);
       ptr->len = len;
   
       // Enter the data, and terminate the string.
       memcpy(ptr->data, s1.toCharArray(), s1.length());
       memcpy(ptr->data + s1.length(), s2.toCharArray(), s2.length());
       ptr->data[len] = 0;
   }
   
   
   ManagedString::ManagedString(ManagedBuffer buffer)
   {
       initString((char*)buffer.getBytes(), buffer.length());
   }
   
   ManagedString::ManagedString(const char *str, const int16_t length)
   {
       // Sanity check. Return EmptyString for anything distasteful
       if (str == NULL || *str == 0 || (uint16_t)length > strlen(str)) // XXX length should be unsigned on the interface
       {
           initEmpty();
           return;
       }
   
       initString(str, length);
   }
   
   ManagedString::ManagedString(const ManagedString &s)
   {
       ptr = s.ptr;
       ptr->incr();
   }
   
   
   ManagedString::ManagedString()
   {
       initEmpty();
   }
   
   ManagedString::~ManagedString()
   {
       ptr->decr();
   }
   
   ManagedString& ManagedString::operator = (const ManagedString& s)
   {
       if (this->ptr == s.ptr)
           return *this;
   
       ptr->decr();
       ptr = s.ptr;
       ptr->incr();
   
       return *this;
   }
   
   bool ManagedString::operator== (const ManagedString& s)
   {
       return ((length() == s.length()) && (strcmp(toCharArray(),s.toCharArray())==0));
   }
   
   bool ManagedString::operator!= (const ManagedString& s)
   {
       return !(*this == s);
   }
   
   bool ManagedString::operator< (const ManagedString& s)
   {
       return (strcmp(toCharArray(), s.toCharArray())<0);
   }
   
   bool ManagedString::operator> (const ManagedString& s)
   {
       return (strcmp(toCharArray(), s.toCharArray())>0);
   }
   
   ManagedString ManagedString::substring(int16_t start, int16_t length)
   {
       // If the parameters are illegal, just return a reference to the empty string.
       if (start >= this->length())
           return ManagedString(EMPTY_DATA);
   
       // Compute a safe copy length;
       length = min(this->length()-start, length);
   
       // Build a ManagedString from this.
       return ManagedString(toCharArray()+start, length);
   }
   
   ManagedString (codal::operator+) (const ManagedString& lhs, const ManagedString& rhs)
   {
   
       // If the either string is empty, nothing to do!
       if (rhs.length() == 0)
           return lhs;
   
       if (lhs.length() == 0)
           return rhs;
   
       return ManagedString(lhs, rhs);
   }
   
   
   char ManagedString::charAt(int16_t index)
   {
       return (index >=0 && index < length()) ? ptr->data[index] : 0;
   }
   
   ManagedString ManagedString::EmptyString(EMPTY_DATA);
