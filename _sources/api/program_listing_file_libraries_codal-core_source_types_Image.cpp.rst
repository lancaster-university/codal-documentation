
.. _program_listing_file_libraries_codal-core_source_types_Image.cpp:

Program Listing for File Image.cpp
==================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_types_Image.cpp>` (``libraries/codal-core/source/types/Image.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

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
   
   #include "CodalConfig.h"
   #include "Image.h"
   #include "BitmapFont.h"
   #include "CodalCompat.h"
   #include "ManagedString.h"
   #include "ErrorNo.h"
   
   
   using namespace codal;
   
   #define REF_TAG REF_TAG_IMAGE
   #define EMPTY_DATA ((ImageData*)(void*)emptyData)
   
   REF_COUNTED_DEF_EMPTY(1, 1, 0)
   
   Image Image::EmptyImage(EMPTY_DATA);
   
   Image::Image()
   {
       // Create new reference to the EmptyImage and we're done.
       init_empty();
   }
   
   
   Image::Image(const int16_t x, const int16_t y)
   {
       this->init(x,y,NULL);
   }
   
   Image::Image(const Image &image)
   {
       ptr = image.ptr;
       ptr->incr();
   }
   
   Image::Image(const char *s)
   {
       int width = 0;
       int height = 0;
       int count = 0;
       int digit = 0;
   
       char parseBuf[10];
   
       const char *parseReadPtr;
       char *parseWritePtr;
       uint8_t *bitmapPtr;
   
       if (s == NULL)
       {
           init_empty();
           return;
       }
   
       // First pass: Parse the string to determine the geometry of the image.
       // We do this from first principles to avoid unecessary load of the strtok() libs etc.
       parseReadPtr = s;
   
       while (*parseReadPtr)
       {
           if (isdigit(*parseReadPtr))
           {
               // Ignore numbers.
               digit = 1;
           }
           else if (*parseReadPtr =='\n')
           {
               if (digit)
               {
                   count++;
                   digit = 0;
               }
   
               height++;
   
               width = count > width ? count : width;
               count = 0;
           }
           else
           {
               if (digit)
               {
                   count++;
                   digit = 0;
               }
           }
   
           parseReadPtr++;
       }
   
       this->init(width, height, NULL);
   
       // Second pass: collect the data.
       parseReadPtr = s;
       parseWritePtr = parseBuf;
       bitmapPtr = this->getBitmap();
   
       while (*parseReadPtr)
       {
           if (isdigit(*parseReadPtr))
           {
               *parseWritePtr = *parseReadPtr;
               parseWritePtr++;
           }
           else
           {
               *parseWritePtr = 0;
               if (parseWritePtr > parseBuf)
               {
                   *bitmapPtr = atoi(parseBuf);
                   bitmapPtr++;
                   parseWritePtr = parseBuf;
               }
           }
   
           parseReadPtr++;
       }
   }
   
   Image::Image(ImageData *p)
   {
       if(p == NULL)
       {
           init_empty();
           return;
       }
   
       ptr = p;
       ptr->incr();
   }
   
   ImageData *Image::leakData()
   {
       ImageData* res = ptr;
       init_empty();
       return res;
   }
   
   
   Image::Image(const int16_t x, const int16_t y, const uint8_t *bitmap)
   {
       this->init(x,y,bitmap);
   }
   
   Image::~Image()
   {
       ptr->decr();
   }
   
   void Image::init_empty()
   {
       ptr = EMPTY_DATA;
   }
   
   void Image::init(const int16_t x, const int16_t y, const uint8_t *bitmap)
   {
       //sanity check size of image - you cannot have a negative sizes
       if(x < 0 || y < 0)
       {
           init_empty();
           return;
       }
   
   
       // Create a copy of the array
       ptr = (ImageData*)malloc(sizeof(ImageData) + x * y);
       REF_COUNTED_INIT(ptr);
       ptr->width = x;
       ptr->height = y;
   
   
       // create a linear buffer to represent the image. We could use a jagged/2D array here, but experimentation
       // showed this had a negative effect on memory management (heap fragmentation etc).
   
       if (bitmap)
           this->printImage(x,y,bitmap);
       else
           this->clear();
   }
   
   Image& Image::operator = (const Image& i)
   {
       if(ptr == i.ptr)
           return *this;
   
       ptr->decr();
       ptr = i.ptr;
       ptr->incr();
   
       return *this;
   }
   
   bool Image::operator== (const Image& i)
   {
       if (ptr == i.ptr)
           return true;
       else
           return (ptr->width == i.ptr->width && ptr->height == i.ptr->height && (memcmp(getBitmap(), i.ptr->data, getSize())==0));
   }
   
   
   void Image::clear()
   {
       memclr(getBitmap(), getSize());
   }
   
   int Image::setPixelValue(int16_t x , int16_t y, uint8_t value)
   {
       //sanity check
       if(x >= getWidth() || y >= getHeight() || x < 0 || y < 0)
           return DEVICE_INVALID_PARAMETER;
   
       this->getBitmap()[y*getWidth()+x] = value;
       return DEVICE_OK;
   }
   
   int Image::getPixelValue(int16_t x , int16_t y)
   {
       //sanity check
       if(x >= getWidth() || y >= getHeight() || x < 0 || y < 0)
           return DEVICE_INVALID_PARAMETER;
   
       return this->getBitmap()[y*getWidth()+x];
   }
   
   int Image::printImage(int16_t width, int16_t height, const uint8_t *bitmap)
   {
       const uint8_t *pIn;
       uint8_t *pOut;
       int pixelsToCopyX, pixelsToCopyY;
   
       // Sanity check.
       if (width <= 0 || width <= 0 || bitmap == NULL)
           return DEVICE_INVALID_PARAMETER;
   
       // Calcualte sane start pointer.
       pixelsToCopyX = min(width,this->getWidth());
       pixelsToCopyY = min(height,this->getHeight());
   
       pIn = bitmap;
       pOut = this->getBitmap();
   
       // Copy the image, stride by stride.
       for (int i=0; i<pixelsToCopyY; i++)
       {
           memcpy(pOut, pIn, pixelsToCopyX);
           pIn += width;
           pOut += this->getWidth();
       }
   
       return DEVICE_OK;
   }
   
   int Image::paste(const Image &image, int16_t x, int16_t y, uint8_t alpha)
   {
       uint8_t *pIn, *pOut;
       int cx, cy;
       int pxWritten = 0;
   
       // Sanity check.
       // We permit writes that overlap us, but ones that are clearly out of scope we can filter early.
       if (x >= getWidth() || y >= getHeight() || x+image.getWidth() <= 0 || y+image.getHeight() <= 0)
           return 0;
   
       //Calculate the number of byte we need to copy in each dimension.
       cx = x < 0 ? min(image.getWidth() + x, getWidth()) : min(image.getWidth(), getWidth() - x);
       cy = y < 0 ? min(image.getHeight() + y, getHeight()) : min(image.getHeight(), getHeight() - y);
   
       // Calculate sane start pointer.
       pIn = image.ptr->data;
       pIn += (x < 0) ? -x : 0;
       pIn += (y < 0) ? -image.getWidth()*y : 0;
   
       pOut = getBitmap();
       pOut += (x > 0) ? x : 0;
       pOut += (y > 0) ? getWidth()*y : 0;
   
       // Copy the image, stride by stride
       // If we want primitive transparecy, we do this byte by byte.
       // If we don't, use a more efficient block memory copy instead. Every little helps!
   
       if (alpha)
       {
           for (int i=0; i<cy; i++)
           {
               for (int j=0; j<cx; j++)
               {
                   // Copy this byte if appropriate.
                   if (*(pIn+j) != 0){
                       *(pOut+j) = *(pIn+j);
                       pxWritten++;
                   }
               }
   
               pIn += image.getWidth();
               pOut += getWidth();
           }
       }
       else
       {
           for (int i=0; i<cy; i++)
           {
               memcpy(pOut, pIn, cx);
   
               pxWritten += cx;
               pIn += image.getWidth();
               pOut += getWidth();
           }
       }
   
       return pxWritten;
   }
   
   int Image::print(char c, int16_t x, int16_t y)
   {
       const uint8_t *v;
       int x1, y1;
   
       BitmapFont font = BitmapFont::getSystemFont();
   
       // Sanity check. Silently ignore anything out of bounds.
       if (x >= getWidth() || y >= getHeight() || c < BITMAP_FONT_ASCII_START || c > font.asciiEnd)
           return DEVICE_INVALID_PARAMETER;
   
       // Paste.
       v = font.get(c);
   
       for (int row=0; row<BITMAP_FONT_HEIGHT; row++)
       {
           // Update our Y co-ord write position
           y1 = y+row;
   
           for (int col = 0; col < BITMAP_FONT_WIDTH; col++)
           {
               // Update our X co-ord write position
               x1 = x+col;
   
               if (x1 < getWidth() && y1 < getHeight())
                   this->getBitmap()[y1*getWidth()+x1] = ((*v) & (0x10 >> col)) ? 255 : 0;
           }
           v++;
       }
   
       return DEVICE_OK;
   }
   
   
   int Image::shiftLeft(int16_t n)
   {
       uint8_t *p = getBitmap();
       int pixels = getWidth()-n;
   
       if (n <= 0 )
           return DEVICE_INVALID_PARAMETER;
   
       if(n >= getWidth())
       {
           clear();
           return DEVICE_OK;
       }
   
       for (int y = 0; y < getHeight(); y++)
       {
           // Copy, and blank fill the rightmost column.
           memcpy(p, p+n, pixels);
           memclr(p+pixels, n);
           p += getWidth();
       }
   
       return DEVICE_OK;
   }
   
   int Image::shiftRight(int16_t n)
   {
       uint8_t *p = getBitmap();
       int pixels = getWidth()-n;
   
       if (n <= 0)
           return DEVICE_INVALID_PARAMETER;
   
       if(n >= getWidth())
       {
           clear();
           return DEVICE_OK;
       }
   
       for (int y = 0; y < getHeight(); y++)
       {
           // Copy, and blank fill the leftmost column.
           memmove(p+n, p, pixels);
           memclr(p, n);
           p += getWidth();
       }
   
       return DEVICE_OK;
   }
   
   
   int Image::shiftUp(int16_t n)
   {
       uint8_t *pOut, *pIn;
   
       if (n <= 0 )
           return DEVICE_INVALID_PARAMETER;
   
       if(n >= getHeight())
       {
           clear();
           return DEVICE_OK;
       }
   
       pOut = getBitmap();
       pIn = getBitmap()+getWidth()*n;
   
       for (int y = 0; y < getHeight(); y++)
       {
           // Copy, and blank fill the leftmost column.
           if (y < getHeight()-n)
               memcpy(pOut, pIn, getWidth());
           else
               memclr(pOut, getWidth());
   
           pIn += getWidth();
           pOut += getWidth();
       }
   
       return DEVICE_OK;
   }
   
   
   int Image::shiftDown(int16_t n)
   {
       uint8_t *pOut, *pIn;
   
       if (n <= 0 )
           return DEVICE_INVALID_PARAMETER;
   
       if(n >= getHeight())
       {
           clear();
           return DEVICE_OK;
       }
   
       pOut = getBitmap() + getWidth()*(getHeight()-1);
       pIn = pOut - getWidth()*n;
   
       for (int y = 0; y < getHeight(); y++)
       {
           // Copy, and blank fill the leftmost column.
           if (y < getHeight()-n)
               memcpy(pOut, pIn, getWidth());
           else
               memclr(pOut, getWidth());
   
           pIn -= getWidth();
           pOut -= getWidth();
       }
   
       return DEVICE_OK;
   }
   
   
   ManagedString Image::toString()
   {
       //width including commans and \n * height
       int stringSize = getSize() * 2;
   
       //plus one for string terminator
       char parseBuffer[stringSize + 1];
   
       parseBuffer[stringSize] = '\0';
   
       uint8_t *bitmapPtr = getBitmap();
   
       int parseIndex = 0;
       int widthCount = 0;
   
       while (parseIndex < stringSize)
       {
           if(*bitmapPtr)
               parseBuffer[parseIndex] = '1';
           else
               parseBuffer[parseIndex] = '0';
   
           parseIndex++;
   
           if(widthCount == getWidth()-1)
           {
               parseBuffer[parseIndex] = '\n';
               widthCount = 0;
           }
           else
           {
               parseBuffer[parseIndex] = ',';
               widthCount++;
           }
   
           parseIndex++;
           bitmapPtr++;
       }
   
       return ManagedString(parseBuffer);
   }
   
   Image Image::crop(int startx, int starty, int cropWidth, int cropHeight)
   {
       int newWidth = startx + cropWidth;
       int newHeight = starty + cropHeight;
   
       if (newWidth >= getWidth() || newWidth <=0)
           newWidth = getWidth();
   
       if (newHeight >= getHeight() || newHeight <= 0)
           newHeight = getHeight();
   
       //allocate our storage.
       uint8_t cropped[newWidth * newHeight];
   
       //calculate the pointer to where we want to begin cropping
       uint8_t *copyPointer = getBitmap() + (getWidth() * starty) + startx;
   
       //get a reference to our storage
       uint8_t *pastePointer = cropped;
   
       //go through row by row and select our image.
       for (int i = starty; i < newHeight; i++)
       {
           memcpy(pastePointer, copyPointer, newWidth);
   
           copyPointer += getWidth();
           pastePointer += newHeight;
       }
   
       return Image(newWidth, newHeight, cropped);
   }
   
   bool Image::isReadOnly()
   {
       return ptr->isReadOnly();
   }
   
   Image Image::clone()
   {
       return Image(getWidth(), getHeight(), getBitmap());
   }
