
.. _program_listing_file_libraries_codal-microbit-v2_source_MicroBitFileSystem.cpp:

Program Listing for File MicroBitFileSystem.cpp
===============================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_MicroBitFileSystem.cpp>` (``libraries/codal-microbit-v2/source/MicroBitFileSystem.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
   The MIT License (MIT)
   Copyright (c) 2016 British Broadcasting Corporation.
   This software is provided by Lancaster University by arrangement with the BBC.
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
   
   #include "MicroBitConfig.h"
   #include "MicroBitFileSystem.h"
   #include "MicroBitFlash.h"
   #include "MicroBitStorage.h"        
   #include "MicroBitCompat.h"
   #include "ErrorNo.h"
   
   static uint32_t *defaultScratchPage = (uint32_t *)MICROBIT_DEFAULT_SCRATCH_PAGE;
   
   MicroBitFileSystem* MicroBitFileSystem::defaultFileSystem = NULL;
   
   uint16_t MicroBitFileSystem::getFreeBlock()
   {
       // Walk the File Table and allocate the first free block - starting immediately after the last block allocated,
       // and wrapping around the filesystem space if we reach the end.
       uint16_t block;
       uint16_t deletedBlock = 0;
   
       for (block = (lastBlockAllocated + 1) % fileSystemSize; block != lastBlockAllocated; block++)
       {
           if (fileSystemTable[block] == MBFS_UNUSED)
           {
               lastBlockAllocated = block;
               return block;
           }
   
           if (fileSystemTable[block] == MBFS_DELETED)
               deletedBlock = block;
       }
   
       // if no UNUSED blocks are available, try to recycle one marked as DELETED.
       block = deletedBlock;
   
       // If no blocks are available - either UNUSED or marked as DELETED, then we're out of space and there's nothing we can do.
       if (block)
       {
           // recycle the FileTable, such that we can mark all previously deleted blocks as re-usable.
           // Better to do this in bulk, rather than on a block by block basis to improve efficiency. 
           recycleFileTable();
   
           // Record the block we just allocated, so we can round-robin around blocks for load balancing.
           lastBlockAllocated = block;
       }
   
       return block;
   }
   
   uint32_t* MicroBitFileSystem::getFreePage()
   {
       // Walk the file table, starting at the last allocated block, looking for an unused page.
       int blocksPerPage = (MICROBIT_CODEPAGESIZE / MBFS_BLOCK_SIZE);
   
       // get a handle on the next physical page.
       uint16_t currentPage = getBlockNumber(getPage(lastBlockAllocated));
       uint16_t page = (currentPage + blocksPerPage) % fileSystemSize;
       uint16_t recyclablePage = 0;
   
       // Walk around the file table, looking for a free page.
       while (page != currentPage)
       {
           bool empty = true;
           bool deleted = false;
           uint16_t next;
   
           for (int i = 0; i < blocksPerPage; i++)
           {
               next = getNextFileBlock(page + i);
               
               if (next == MBFS_DELETED)
                   deleted = true;
               
               else if (next != MBFS_UNUSED)
               {
                   empty = false;
                   break;
               }
           }
   
           // See if we found one...
           if (empty)
           {
               lastBlockAllocated = page;
               return getBlock(page);
           }
   
           // make note of the first unused but un-erased page we find (if any).
           if (deleted && !recyclablePage)
               recyclablePage = page;
   
           page = (page + blocksPerPage) % fileSystemSize;
       }
   
       // No empty pages are available, but we may be able to recycle one.
       if (recyclablePage)
       {
           uint32_t *address = getBlock(recyclablePage);
           flash.erase_page(address);
           return address;
       }
   
       // Nothing available at all. Use the default.
       flash.erase_page(defaultScratchPage);
       return defaultScratchPage;
   }
   
   
   MicroBitFileSystem::MicroBitFileSystem(uint32_t flashStart, int flashPages)
   {
       // Initialise status flags to default value
       this->status = 0;
   
       // Attempt tp load an existing filesystem, if it exisits
       init(flashStart, flashPages);
   
       // If this is the first FileSystem created, so it as the default.
       if(MicroBitFileSystem::defaultFileSystem == NULL)
           MicroBitFileSystem::defaultFileSystem = this;
   }
   
   int MicroBitFileSystem::init(uint32_t flashStart, int flashPages)
   {
       // Protect against accidental re-initialisation
       if (status & MBFS_STATUS_INITIALISED)
           return MICROBIT_NOT_SUPPORTED;
   
       // Validate parameters
       if (flashPages < 0)
           return MICROBIT_INVALID_PARAMETER;
   
       // Zero initialise default parameters (mbed/ARMCC does not permit this is the class definition).
       fileSystemTable = NULL;
       lastBlockAllocated = 0;
       rootDirectory = NULL;
       openFiles = NULL;
   
       // If we have a zero length, then dynamically determine our geometry.
       if (flashStart == 0)
       {
           // Flash start is on the first page after the programmed ROM contents.
           // This is: __etext (program code) for GCC and Image$$RO$$Limit for ARMCC.
           flashStart = FLASH_PROGRAM_END;
   
           // Round up to the nearest free page.
           if (flashStart % MICROBIT_CODEPAGESIZE != 0)
               flashStart = ((uint32_t)flashStart & ~(MICROBIT_CODEPAGESIZE-1)) + MICROBIT_CODEPAGESIZE;
       }
   
       if (flashPages == 0)
           flashPages = (MICROBIT_APP_REGION_END - flashStart) / MICROBIT_CODEPAGESIZE;
   
       // The FileTable alays resides at the start of the file system.
       fileSystemTable = (uint16_t *)flashStart;
   
       // First, try to load an existing file system at this location.
       if (load() != MICROBIT_OK)
       {
           // No file system was found, so format a fresh one.
           // Bring up a freshly formatted file system here.
           fileSystemSize = flashPages * (MICROBIT_CODEPAGESIZE / MBFS_BLOCK_SIZE);
           fileSystemTableSize = calculateFileTableSize();
   
           format();
       }
   
       // indicate that we have a valid FileSystem
       status = MBFS_STATUS_INITIALISED;
       return MICROBIT_OK;
   }
   
   int MicroBitFileSystem::load()
   {
       uint16_t rootOffset = fileSystemTable[0];
   
       // A valid MBFS has the first 'N' blocks set to the value 'N' followed by a valid root directory block with magic signature.
       for (int i = 0; i < rootOffset; i++)
       {
           if (fileSystemTable[i] >= MBFS_EOF || fileSystemTable[i] != rootOffset)
               return MICROBIT_NO_DATA;
       }
   
       // Check for a valid signature at the start of the root directory
       DirectoryEntry *root = (DirectoryEntry *) getBlock(rootOffset);
       if (strcmp(root->file_name, MBFS_MAGIC) != 0)
           return MICROBIT_NO_DATA;
   
       rootDirectory = root;
       fileSystemSize = root->length;
       fileSystemTableSize = calculateFileTableSize();
   
       return MICROBIT_OK;
   }
   
   
   int MicroBitFileSystem::format()
   {
       uint16_t value = fileSystemTableSize;
   
       // Mark the FileTable blocks themselves as used.
       for (uint16_t block = 0; block < fileSystemTableSize; block++)
           flash.flash_write(&fileSystemTable[block], &value, 2);
   
       // Create a root directory
       value = MBFS_EOF;
       flash.flash_write(&fileSystemTable[fileSystemTableSize], &value, 2);
       
       // Store a MAGIC value in the first root directory entry. 
       // This will let us identify a valid File System later.
       DirectoryEntry magic;
   
       strcpy(magic.file_name, MBFS_MAGIC);
       magic.first_block = fileSystemTableSize;
       magic.flags = MBFS_DIRECTORY_ENTRY_VALID;
       magic.length = fileSystemSize;
   
       // Cache the root directory entry for later use.
       rootDirectory = (DirectoryEntry *)getBlock(fileSystemTableSize);
       flash.flash_write(rootDirectory, &magic, sizeof(DirectoryEntry));
   
       return MICROBIT_OK;
   }
   
   DirectoryEntry* MicroBitFileSystem::getDirectoryEntry(char const * filename, const DirectoryEntry *directory)
   {
       Directory *dir;
       char const *file;
       uint16_t block;
       DirectoryEntry *dirent;
   
       // Determine the filename from the (potentially) fully qualified filename.
       file = filename + strlen(filename);
       while (file >= filename && *file != '/')
           file--;
       file++;
   
       // Obtain a handle on the directory to search.
       if (directory == NULL)
           directory = rootDirectory;
   
       block = directory->first_block;
       dir = (Directory *) getBlock(block);
       dirent = &dir->entry[0];
   
       // Iterate through the directory entries until we find our file, or run out of space.
       while (1)
       {
           if ((uint32_t)(dirent + 1) > (uint32_t)dir + MBFS_BLOCK_SIZE)
           {
               block = getNextFileBlock(block);
               if (block == MBFS_EOF)
                   return NULL;
   
               dir = (Directory *)getBlock(block);
               dirent = &dir->entry[0];
           }
   
           // Check for a valid match
           if (dirent->flags & MBFS_DIRECTORY_ENTRY_VALID && strcmp(dirent->file_name, file) == 0)
               return dirent;
   
           // Move onto the next entry.
           dirent++;
       }
   
       return NULL;
   }
   
   uint16_t MicroBitFileSystem::calculateFileTableSize()
   {
       uint16_t size = (fileSystemSize * 2) / MBFS_BLOCK_SIZE;
       if ((fileSystemSize * 2) % MBFS_BLOCK_SIZE)
           size++;
   
       return size;
   }
   
   uint32_t *MicroBitFileSystem::getPage(uint16_t block)
   {
       uint32_t address = (uint32_t) getBlock(block);
       return (uint32_t *) (address - address % MICROBIT_CODEPAGESIZE);
   }
   
   uint32_t *MicroBitFileSystem::getBlock(uint16_t block)
   {
       return (uint32_t *)((uint32_t)fileSystemTable + block * MBFS_BLOCK_SIZE);
   }
   
   uint16_t MicroBitFileSystem::getNextFileBlock(uint16_t block)
   {
       return fileSystemTable[block];
   }
   
   uint16_t MicroBitFileSystem::getBlockNumber(void *address)
   {
       return (((uint32_t) address - (uint32_t) fileSystemTable) / MBFS_BLOCK_SIZE);
   }
   
   int MicroBitFileSystem::fileTableWrite(uint16_t block, uint16_t value)
   {
       flash.flash_write(&fileSystemTable[block], &value, 2);
       return MICROBIT_OK;
   }
   
   
   
   DirectoryEntry* MicroBitFileSystem::getDirectoryOf(char const * filename)
   {
       DirectoryEntry* directory;
   
       // If not path is provided, return the root diretory.
       if (filename == NULL || filename[0] == 0)
           return rootDirectory;
   
       char s[MBFS_FILENAME_LENGTH + 1];
   
       uint8_t i = 0;
   
       directory = rootDirectory;
   
       while (*filename != '\0') {
           if (*filename == '/') {
               s[i] = '\0';
   
               // Ensure each level of the filename is valid
               if (i == 0 || i > MBFS_FILENAME_LENGTH + 1)
                   return NULL;
   
               // Extract the relevant entry from the directory.
               directory = getDirectoryEntry(s, directory);
   
               // If file / directory does not exist, then there's nothing more we can do.
               if (!directory)
                   return NULL;
   
               i = 0;
           }
           else
               s[i++] = *filename;
   
           filename++;
       }
   
       return directory;
   }
   
   int MicroBitFileSystem::recycleBlock(uint16_t block, int type)
   {
       uint32_t *page = getPage(block);
       uint32_t* scratch = getFreePage();
       uint8_t *write = (uint8_t *)scratch;
       uint16_t b = getBlockNumber(page);
   
       for (int i = 0; i < (int)( MICROBIT_CODEPAGESIZE / MBFS_BLOCK_SIZE); i++)
       {
           // If we have an unused or deleted block, there's nothing to do - allow the block to be recycled.
           if (fileSystemTable[b] == MBFS_DELETED || fileSystemTable[b] == MBFS_UNUSED) 
           {}
   
           // If we have been asked to recycle a valid directory block, recycle individual entries where possible.
           else if (b == block && type == MBFS_BLOCK_TYPE_DIRECTORY)
           {
               DirectoryEntry *direntIn = (DirectoryEntry *)getBlock(b);
               DirectoryEntry *direntOut = (DirectoryEntry *)write;
   
               for (uint16_t entry = 0; entry < MBFS_BLOCK_SIZE / sizeof(DirectoryEntry); entry++)
               {
                   if (direntIn->flags & MBFS_DIRECTORY_ENTRY_VALID)
                       flash.flash_write((uint32_t *)direntOut, (uint32_t *)direntIn, sizeof(DirectoryEntry));
   
                   direntIn++;
                   direntOut++;
               }
           }
   
           // All blocks before the root directory are the FileTable. 
           // Recycle any entries marked as DELETED to UNUSED.
           else if (getBlock(b) < (uint32_t *)rootDirectory)
           {
               uint16_t *tableIn = (uint16_t *)getBlock(b);
               uint16_t *tableOut = (uint16_t *)write;
               
               for (int entry = 0; entry < MBFS_BLOCK_SIZE / 2; entry++)
               {
                   if (*tableIn != MBFS_DELETED)
                       flash.flash_write(tableOut, tableIn, 2);
   
                   tableIn++;
                   tableOut++;
               }
           }
   
           // Copy all other VALID blocks directly into the scratch page.
           else
               flash.flash_write(write, getBlock(b), MBFS_BLOCK_SIZE);
           
           // move on to next block.
           write += MBFS_BLOCK_SIZE;
           b++;
       }
   
       // Now refresh the page originally holding the block.
       flash.erase_page(page);
       flash.flash_write(page, scratch, MICROBIT_CODEPAGESIZE);
       flash.erase_page(scratch);
   
       return MICROBIT_OK;
   }
   
   int MicroBitFileSystem::recycleFileTable()
   {
       bool pageRecycled = false;
       
       for (uint16_t block = 0; block < fileSystemSize; block++)
       {
           // if we just crossed a page boundary, reset pageRecycled.
           if (block % (MICROBIT_CODEPAGESIZE / MBFS_BLOCK_SIZE) == 0)
               pageRecycled = false;
   
           if (fileSystemTable[block] == MBFS_DELETED && !pageRecycled)
           {
               recycleBlock(block);
               pageRecycled = true;
           }
       }
   
       // now, recycle the FileSystemTable itself, upcycling entries marked as DELETED to UNUSED as we go.
       for (uint16_t block = 0; getPage(block) < (uint32_t *)rootDirectory; block += MICROBIT_CODEPAGESIZE / MBFS_BLOCK_SIZE)
           recycleBlock(block);
   
       return MICROBIT_OK;
   }
   
   
   DirectoryEntry* MicroBitFileSystem::createDirectoryEntry(DirectoryEntry *directory)
   {
       Directory *dir;
       uint16_t block;
       DirectoryEntry *dirent;
       DirectoryEntry *empty = NULL;
       DirectoryEntry *invalid = NULL;
   
       // Try to find an unused entry in the directory.
       block = directory->first_block;
       dir = (Directory *)getBlock(block);
       dirent = &dir->entry[0];
   
       // Iterate through the directory entries until we find and unused entry, or run out of space.
       while (1)
       {
           // Scan through each of the blocks in the directory
           if ((uint32_t)(dirent+1) > (uint32_t)dir + MBFS_BLOCK_SIZE)
           {
               block = getNextFileBlock(block);
               if (block == MBFS_EOF)
                   break;
   
               dir = (Directory *)getBlock(block);
               dirent = &dir->entry[0];
           }
   
           // If we find an empty slot, use that.
           if (dirent->flags & MBFS_DIRECTORY_ENTRY_FREE)
           {
               empty = dirent;
               break;
           }
   
           // Record the first invalid block we find (used, but then deleted).
           if ((dirent->flags & MBFS_DIRECTORY_ENTRY_VALID) == 0 && invalid == NULL)
               invalid = dirent;
   
           // Move onto the next entry.
           dirent++;
       }
   
   
       // Now choose the best available slot, giving preference to entries that would avoid a FLASH page erase opreation.
       dirent = NULL;
   
       // Ideally, choose an unused entry within an existing block.
       if (empty)
       {
           dirent = empty;
       }
   
       // if not possible, try to re-use a second-hand block that has been freed. This will result in an erase operation of the block,
       // but will not consume any more resources.
       else if (invalid)
       {
           dirent = invalid;
           uint16_t b = getBlockNumber(dirent);
           recycleBlock(b, MBFS_BLOCK_TYPE_DIRECTORY);
       }
   
       // If nothing is available, extend the directory with a new block.
       else
       {
           // Allocate a new logical block
           uint16_t newBlock = getFreeBlock();
           if (newBlock == 0)
               return NULL;
   
           // Append this to the directory
           uint16_t lastBlock = directory->first_block;
           while (getNextFileBlock(lastBlock) != MBFS_EOF)
               lastBlock = getNextFileBlock(lastBlock);
   
           // Append the block.
           fileTableWrite(lastBlock, newBlock);
           fileTableWrite(newBlock, MBFS_EOF);
   
           dirent = (DirectoryEntry *)getBlock(newBlock);
       }
   
       return dirent;
   }
   
   DirectoryEntry* MicroBitFileSystem::createFile(char const * filename, DirectoryEntry *directory, bool isDirectory)
   {
       char const *file;
       DirectoryEntry *dirent;
   
       // Determine the filename from the (potentially) fully qualified filename.
       file = filename + strlen(filename);
       while (file >= filename && *file != '/')
           file--;
       file++;
   
       // Allocate a directory entry for our new file.
       dirent = createDirectoryEntry(directory);
       if (dirent == NULL)
           return NULL;
   
       // Create a new block to represent the file.
       uint16_t newBlock = getFreeBlock();
       if (newBlock == 0)
           return NULL;
   
       // Populate our assigned Directory Entry.
       DirectoryEntry d;
       strcpy(d.file_name, file);
       d.first_block = newBlock;
   
       if (isDirectory)
       {
           // Mark as a directory, and set a zero length (special case for directories, to minimize unecessary FLASH erases).
           d.flags = MBFS_DIRECTORY_ENTRY_VALID | MBFS_DIRECTORY_ENTRY_DIRECTORY;
           d.length = 0;
       }
       else
       {
           // We leave the file size as unwritten for regular files - pending a possible forthcoming write/close operation.
           d.flags = MBFS_DIRECTORY_ENTRY_NEW;
           d.length = 0xffffffff;
       }
   
       // Push the new data back to FLASH memory
       flash.flash_write(dirent, &d, sizeof(DirectoryEntry));
       fileTableWrite(d.first_block, MBFS_EOF);
       return dirent;
   }
   
   FileDescriptor* MicroBitFileSystem::getFileDescriptor(int fd, bool remove)
   {
       FileDescriptor *file = openFiles;
       FileDescriptor *prev = NULL;
   
       while (file)
       {
           if (file->id == fd)
           {
               if (remove)
               {
                   if (prev)
                       prev->next = file->next;
                   else
                       openFiles = file->next;
               }
               return file;
           }
   
           prev = file;
           file = file->next;
       }
   
       return NULL;
   }
   
   
   int MicroBitFileSystem::createDirectory(char const *name)
   {
       DirectoryEntry* directory;        // Directory holding this file.
       DirectoryEntry* dirent;            // Entry in the direcoty of this file.
   
       // Protect against accidental re-initialisation
       if ((status & MBFS_STATUS_INITIALISED) == 0)
           return MICROBIT_NOT_SUPPORTED;
   
       // Reject invalid filenames.
       if (!isValidFilename(name))
           return MICROBIT_INVALID_PARAMETER;
   
       // Determine the directory for this file.
       directory = getDirectoryOf(name);
   
       if (directory == NULL)
           return MICROBIT_INVALID_PARAMETER;
   
       // Find the DirectoryEntry associated with the given name (if it exists).
       // We don't permit files or directories with the same name.
       dirent = getDirectoryEntry(name, directory);
   
       if (dirent)
           return MICROBIT_INVALID_PARAMETER;
   
       dirent = createFile(name, directory, true);
       if (dirent == NULL)
           return MICROBIT_NO_RESOURCES;
   
       return MICROBIT_OK;
   }
   
   
   int MicroBitFileSystem::open(char const * filename, uint32_t flags)
   {
       FileDescriptor *file;               // File Descriptor of this file.
       DirectoryEntry* directory;          // Directory holding this file.
       DirectoryEntry* dirent;             // Entry in the direcoty of this file.
       int id;                             // FileDescriptor id to be return to the caller.
   
       // Protect against accidental re-initialisation
       if ((status & MBFS_STATUS_INITIALISED) == 0)
           return MICROBIT_NOT_SUPPORTED;
   
       // Reject invalid filenames.
       if(!isValidFilename(filename))
           return MICROBIT_INVALID_PARAMETER;
   
       // Determine the directory for this file.
       directory = getDirectoryOf(filename);
   
       if (directory == NULL)
           return MICROBIT_INVALID_PARAMETER;
   
       // Find the DirectoryEntry assoviate with the given file (if it exists).
       dirent = getDirectoryEntry(filename, directory);
   
       // Only permit files to be opened once... 
       // also, detemrine a valid ID for this open file as we go.
       file = openFiles;
       id = 0;
       
       while (file && dirent)
       {
           if (file->dirent == dirent)
               return MICROBIT_NOT_SUPPORTED;
   
           if (file->id == id)
           {
               id++;
               file = openFiles;
               continue;
           }
   
           file = file->next;
       }
   
       if (dirent == NULL)
       {
           // If the file doesn't exist, and we haven't been asked to create it, then there's nothing we can do.
           if (!(flags & MB_CREAT))
               return MICROBIT_INVALID_PARAMETER;
   
           dirent = createFile(filename, directory, false);
           if (dirent == NULL)
               return MICROBIT_NO_RESOURCES;
       }
   
       // Try to add a new FileDescriptor into this directory.
       file = new FileDescriptor;
       if (file == NULL)
           return MICROBIT_NO_RESOURCES;
   
       // Populate the FileDescriptor
       file->flags = (flags & ~(MB_CREAT));
       file->id = id;
       file->length = dirent->flags == MBFS_DIRECTORY_ENTRY_NEW ? 0 : dirent->length;
       file->seek = (flags & MB_APPEND) ? file->length : 0;
       file->dirent = dirent;
       file->directory = directory;
       file->cacheLength = 0;
   
       // Add the file descriptor to the chain of open files.
       file->next = openFiles;
       openFiles = file;
   
       // Return the FileDescriptor id to the user
       return file->id;
   }
   
   
   int MicroBitFileSystem::flush(int fd)
   {
       // Protect against accidental re-initialisation
       if ((status & MBFS_STATUS_INITIALISED) == 0)
           return MICROBIT_NOT_SUPPORTED;
   
       FileDescriptor *file = getFileDescriptor(fd);
   
       // Ensure the file is open.
       if(file == NULL)
           return MICROBIT_INVALID_PARAMETER;
   
       // Flush any data in the writeback cache.
       writeBack(file);
   
       // If the file has changed size, create an updated directory entry for the file, reflecting it's new length.
       if (file->dirent->length != file->length)
       {
           DirectoryEntry d = *file->dirent;
           d.length = file->length;
   
           // Do some optimising to reduce FLASH churn if this is the first write to a file. No need then to create a new dirent...
           if (file->dirent->flags == MBFS_DIRECTORY_ENTRY_NEW)
           {
               d.flags = MBFS_DIRECTORY_ENTRY_VALID;
               flash.flash_write(file->dirent, &d, sizeof(DirectoryEntry));
           }
   
           // Otherwise, replace the dirent with a freshly allocated one, and mark the other as INVALID.
           else
           {
               DirectoryEntry *newDirent;
               uint16_t value = MBFS_DELETED;
   
               // invalidate the old directory entry and create a new one with the updated data.
               flash.flash_write(&file->dirent->flags, &value, 2);
               newDirent = createDirectoryEntry(file->directory);
               flash.flash_write(newDirent, &d, sizeof(DirectoryEntry));
           }
       }
   
       return MICROBIT_OK;
   }
   
   int MicroBitFileSystem::close(int fd)
   {
       // Firstly, ensure all unwritten data is flushed.
       int r = flush(fd);
   
       // If the flush called failed on validation, pass the error code onto the caller.
       if (r != MICROBIT_OK)
           return r;
   
       // Remove the file descriptor from the list of open files, and free it.
       // n.b. we know this is safe, as flush() validates this.
       delete getFileDescriptor(fd, true);
   
       return MICROBIT_OK;
   }
   
   int MicroBitFileSystem::seek(int fd, int offset, uint8_t flags)
   {
       FileDescriptor *file;
       int position;
   
       // Protect against accidental re-initialisation
       if ((status & MBFS_STATUS_INITIALISED) == 0)
           return MICROBIT_NOT_SUPPORTED;
   
       // Ensure the file is open.
       file = getFileDescriptor(fd);
   
       if (file == NULL)
           return MICROBIT_INVALID_PARAMETER;
       
       // Flush any data in the writeback cache.
       writeBack(file);
   
       position = file->seek;
   
       if(flags == MB_SEEK_SET)
           position = offset;
       
       if(flags == MB_SEEK_END)
           position = file->length + offset;
       
       if (flags == MB_SEEK_CUR)
           position = file->seek + offset;
       
       if (position < 0 || (uint32_t)position > file->length)
           return MICROBIT_INVALID_PARAMETER;
   
       file->seek = position;
       
       return position;
   }
   
   int MicroBitFileSystem::read(int fd, uint8_t* buffer, int size)
   {
       FileDescriptor *file;
       uint16_t block;
       uint8_t *readPointer;
       uint8_t *writePointer;
   
       uint32_t offset;
       uint32_t position = 0;
       int bytesCopied = 0;
       int segmentLength;
   
       // Protect against accidental re-initialisation
       if ((status & MBFS_STATUS_INITIALISED) == 0)
           return MICROBIT_NOT_SUPPORTED;
   
       // Ensure the file is open.
       file = getFileDescriptor(fd);
   
       if (file == NULL || buffer == NULL || size == 0)
           return MICROBIT_INVALID_PARAMETER;
   
       // Flush any data in the writeback cache before we change the seek pointer.
       writeBack(file);
   
       // Validate the read length.
       size = min(size, file->length - file->seek);
   
       // Find the read position.
       block = file->dirent->first_block; 
   
       // Walk the file table until we reach the start block
       while (file->seek - position > MBFS_BLOCK_SIZE)
       {
           block = getNextFileBlock(block);
           position += MBFS_BLOCK_SIZE;
       }
   
       // Once we have the correct start block, handle the byte offset.
       offset = file->seek - position;
   
       // Now, start copying bytes into the requested buffer.
       writePointer = buffer;
       while (bytesCopied < size)
       {
           // First, determine if we need to write a partial block.
           readPointer = (uint8_t *)getBlock(block) + offset;
           segmentLength = min(size - bytesCopied, MBFS_BLOCK_SIZE - offset);
   
           if(segmentLength > 0)
               memcpy(writePointer, readPointer, segmentLength);
   
           bytesCopied += segmentLength;
           writePointer += segmentLength;
           offset += segmentLength;
   
           if (offset == MBFS_BLOCK_SIZE)
           {
               block = getNextFileBlock(block);
               offset = 0;
           }
       }
   
       file->seek += bytesCopied;
   
       return bytesCopied;
   }
   
   int MicroBitFileSystem::writeBack(FileDescriptor *file)
   {
       if (file->cacheLength)
       {
           int r = writeBuffer(file, file->cache, file->cacheLength);
           file->cacheLength = 0;
           return r;
       }
   
       return 0;
   }
   
   int MicroBitFileSystem::writeBuffer(FileDescriptor *file, uint8_t *buffer, int size)
   {
       uint16_t block, newBlock;
       uint8_t *readPointer;
       uint8_t *writePointer;
   
       uint32_t offset;
       uint32_t position = 0;
       int bytesCopied = 0;
       int segmentLength;
   
       // Find the read position.
       block = file->dirent->first_block;
   
       // Walk the file table until we reach the start block
       while (file->seek - position > MBFS_BLOCK_SIZE)
       {
           block = getNextFileBlock(block);
           position += MBFS_BLOCK_SIZE;
       }
   
       // Once we have the correct start block, handle the byte offset.
       offset = file->seek - position;
       writePointer = (uint8_t *)getBlock(block) + offset;
   
       // Now, start copying bytes from the requested buffer.
       readPointer = buffer;
       while (bytesCopied < size)
       {
           // First, determine if we need to write a partial block.
           segmentLength = min(size - bytesCopied, MBFS_BLOCK_SIZE - offset);
   
           if (segmentLength != 0)
               flash.flash_write(writePointer, readPointer, segmentLength, file->seek + bytesCopied < file->length ? getFreePage() : NULL);
   
           offset += segmentLength;
           bytesCopied += segmentLength;
           readPointer += segmentLength;
   
           if (offset == MBFS_BLOCK_SIZE && bytesCopied < size)
           {
               newBlock = getFreeBlock();
               if (newBlock == 0)
                   break;
   
               fileTableWrite(newBlock, MBFS_EOF);
               fileTableWrite(block, newBlock);
   
               block = newBlock;
   
               writePointer = (uint8_t *)getBlock(block);
               offset = 0;
           }
       }
   
       // update the filelength metadata and seek position such that multiple writes are sequential.
       file->length = max(file->length, file->seek + bytesCopied);
       file->seek += bytesCopied;
   
       return bytesCopied;
   }
   
   bool MicroBitFileSystem::isValidFilename(const char *name)
   {
       if (name == NULL || strlen(name) == 0)
           return false;
   
       for (unsigned int i=0; i<strlen(name); i++)
           if(name[i] < 32 || name[i] > 126) 
               return false;
   
       return true;
   }
   
   
   int MicroBitFileSystem::write(int fd, uint8_t* buffer, int size)
   {
       FileDescriptor *file;
       int bytesCopied = 0;
       int segmentSize;
   
       // Protect against accidental re-initialisation
       if ((status & MBFS_STATUS_INITIALISED) == 0)
           return MICROBIT_NOT_SUPPORTED;
   
       // Ensure the file is open.
       file = getFileDescriptor(fd);
   
       if (file == NULL || buffer == NULL || size == 0)
           return MICROBIT_INVALID_PARAMETER;
   
       // Determine how to handle the write. If the buffer size is less than our cache size, 
       // write the data via the cache. Otherwise, a direct write through is likely more efficient.
       // This may take a few iterations if the cache is already quite full.
       if (size < MBFS_CACHE_SIZE)
       {
           while (bytesCopied < size)
           {
               segmentSize = min(size, MBFS_CACHE_SIZE - file->cacheLength);
               memcpy(&file->cache[file->cacheLength], buffer, segmentSize);
   
               file->cacheLength += segmentSize;
               bytesCopied += segmentSize;
               
               if (file->cacheLength == MBFS_CACHE_SIZE)
                   writeBack(file);
   
   
           }
   
           return bytesCopied;
       }
   
       // If we have a relatively large block, then write it directly (
       writeBack(file);
   
       return writeBuffer(file, buffer, size);
   }
   
   int MicroBitFileSystem::remove(char const * filename)
   {
       int fd = open(filename, MB_READ);
       uint16_t block, nextBlock;
       uint16_t value;
   
       // If the file can't be opened, then it is impossible to delete. Pass through any error codes.
       if (fd < 0)
           return fd;
   
       FileDescriptor *file = getFileDescriptor(fd, true);
   
       // To erase a file, all we need to do is mark its directory entry and data blocks as INVALID.
       // First mark the file table
       block = file->dirent->first_block;
       while (block != MBFS_EOF)
       {
           nextBlock = fileSystemTable[block];
           fileTableWrite(block, MBFS_DELETED);
           block = nextBlock;
       }
   
       // Mark the directory entry of this file as invalid.
       value = MBFS_DIRECTORY_ENTRY_DELETED;
       flash.flash_write(&file->dirent->flags, &value, 2);
   
       // release file metadata
       delete file;
   
       return MICROBIT_OK;
   }
   
