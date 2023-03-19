
.. _program_listing_file_libraries_codal-core_source_types_Matrix4.cpp:

Program Listing for File Matrix4.cpp
====================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_types_Matrix4.cpp>` (``libraries/codal-core/source/types/Matrix4.cpp``)

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
   #include "Matrix4.h"
   
   Matrix4::Matrix4(int rows, int cols)
   {
       this->rows = rows;
       this->cols = cols;
   
       int size = rows * cols;
   
       if (size > 0)
           data = new float[size];
       else
           data = NULL;
   }
   
   Matrix4::Matrix4(const Matrix4 &matrix)
   {
       this->rows = matrix.rows;
       this->cols = matrix.cols;
   
       int size = rows * cols;
   
       if (size > 0)
       {
           data = new float[size];
           for (int i = 0; i < size; i++)
               data[i] = matrix.data[i];
       }
       else
       {
           data = NULL;
       }
   
   }
   
   int Matrix4::width()
   {
       return cols;
   }
   
   int Matrix4::height()
   {
       return rows;
   }
   
   float Matrix4::get(int row, int col)
   {
       if (row < 0 || col < 0 || row >= rows || col >= cols)
           return 0;
   
       return data[width() * row + col];
   }
   
   void Matrix4::set(int row, int col, float v)
   {
       if (row < 0 || col < 0 || row >= rows || col >= cols)
           return;
   
       data[width() * row + col] = v;
   }
   
   Matrix4 Matrix4::transpose()
   {
       Matrix4 result = Matrix4(cols, rows);
   
       for (int i = 0; i < width(); i++)
           for (int j = 0; j < height(); j++)
               result.set(i, j, get(j, i));
   
       return result;
   }
   
   Matrix4 Matrix4::multiply(Matrix4 &matrix, bool transpose)
   {
       int w = transpose ? height() : width();
       int h = transpose ? width() : height();
   
       if (w != matrix.height())
           return Matrix4(0, 0);
   
       Matrix4 result(h, matrix.width());
   
       for (int r = 0; r < result.height(); r++)
       {
           for (int c = 0; c < result.width(); c++)
           {
               float v = 0.0;
   
               for (int i = 0; i < w; i++)
                   v += (transpose ? get(i, r) : get(r, i)) * matrix.get(i, c);
   
               result.set(r, c, v);
           }
       }
   
       return result;
   }
   
   Matrix4 Matrix4::invert()
   {
       // We only support square matrices of size 4...
       if (width() != height() || width() != 4)
           return Matrix4(0, 0);
   
       Matrix4 result(width(), height());
   
       result.data[0] = data[5] * data[10] * data[15] - data[5] * data[11] * data[14] - data[9] * data[6] * data[15] + data[9] * data[7] * data[14] + data[13] * data[6] * data[11] - data[13] * data[7] * data[10];
       result.data[1] = -data[1] * data[10] * data[15] + data[1] * data[11] * data[14] + data[9] * data[2] * data[15] - data[9] * data[3] * data[14] - data[13] * data[2] * data[11] + data[13] * data[3] * data[10];
       result.data[2] = data[1] * data[6] * data[15] - data[1] * data[7] * data[14] - data[5] * data[2] * data[15] + data[5] * data[3] * data[14] + data[13] * data[2] * data[7] - data[13] * data[3] * data[6];
       result.data[3] = -data[1] * data[6] * data[11] + data[1] * data[7] * data[10] + data[5] * data[2] * data[11] - data[5] * data[3] * data[10] - data[9] * data[2] * data[7] + data[9] * data[3] * data[6];
       result.data[4] = -data[4] * data[10] * data[15] + data[4] * data[11] * data[14] + data[8] * data[6] * data[15] - data[8] * data[7] * data[14] - data[12] * data[6] * data[11] + data[12] * data[7] * data[10];
       result.data[5] = data[0] * data[10] * data[15] - data[0] * data[11] * data[14] - data[8] * data[2] * data[15] + data[8] * data[3] * data[14] + data[12] * data[2] * data[11] - data[12] * data[3] * data[10];
       result.data[6] = -data[0] * data[6] * data[15] + data[0] * data[7] * data[14] + data[4] * data[2] * data[15] - data[4] * data[3] * data[14] - data[12] * data[2] * data[7] + data[12] * data[3] * data[6];
       result.data[7] = data[0] * data[6] * data[11] - data[0] * data[7] * data[10] - data[4] * data[2] * data[11] + data[4] * data[3] * data[10] + data[8] * data[2] * data[7] - data[8] * data[3] * data[6];
       result.data[8] = data[4] * data[9] * data[15] - data[4] * data[11] * data[13] - data[8] * data[5] * data[15] + data[8] * data[7] * data[13] + data[12] * data[5] * data[11] - data[12] * data[7] * data[9];
       result.data[9] = -data[0] * data[9] * data[15] + data[0] * data[11] * data[13] + data[8] * data[1] * data[15] - data[8] * data[3] * data[13] - data[12] * data[1] * data[11] + data[12] * data[3] * data[9];
       result.data[10] = data[0] * data[5] * data[15] - data[0] * data[7] * data[13] - data[4] * data[1] * data[15] + data[4] * data[3] * data[13] + data[12] * data[1] * data[7] - data[12] * data[3] * data[5];
       result.data[11] = -data[0] * data[5] * data[11] + data[0] * data[7] * data[9] + data[4] * data[1] * data[11] - data[4] * data[3] * data[9] - data[8] * data[1] * data[7] + data[8] * data[3] * data[5];
       result.data[12] = -data[4] * data[9] * data[14] + data[4] * data[10] * data[13] + data[8] * data[5] * data[14] - data[8] * data[6] * data[13] - data[12] * data[5] * data[10] + data[12] * data[6] * data[9];
       result.data[13] = data[0] * data[9] * data[14] - data[0] * data[10] * data[13] - data[8] * data[1] * data[14] + data[8] * data[2] * data[13] + data[12] * data[1] * data[10] - data[12] * data[2] * data[9];
       result.data[14] = -data[0] * data[5] * data[14] + data[0] * data[6] * data[13] + data[4] * data[1] * data[14] - data[4] * data[2] * data[13] - data[12] * data[1] * data[6] + data[12] * data[2] * data[5];
       result.data[15] = data[0] * data[5] * data[10] - data[0] * data[6] * data[9] - data[4] * data[1] * data[10] + data[4] * data[2] * data[9] + data[8] * data[1] * data[6] - data[8] * data[2] * data[5];
   
       float det = data[0] * result.data[0] + data[1] * result.data[4] + data[2] * result.data[8] + data[3] * result.data[12];
   
       if (det == 0)
           return Matrix4(0, 0);
   
       det = 1.0f / det;
   
       for (int i = 0; i < 16; i++)
           result.data[i] *= det;
   
       return result;
   }
   
   Matrix4::~Matrix4()
   {
       if (data != NULL)
       {
           delete data;
           data = NULL;
       }
   }
