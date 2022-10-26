#!/usr/bin/env python3

import sys
import os

input_file_path = sys.argv[1]
with open(input_file_path, "rb") as f:

  file_size = os.path.getsize(input_file_path)

  byte = f.read(1)
  while byte != b"":
    if byte == b"\x00":
      byte = f.read(1)
      if byte == b"\x11":
        byte = f.read(1)
        if byte == b"\x02":
          byte = f.read(1)
          if byte == b"\xff":
            start_match = f.tell()
            print("found start match at "+hex(f.tell()))
            f.seek(start_match - 14)
            match_size = int.from_bytes(f.read(2), byteorder='big', signed=False)
            f.seek(start_match - 14)
            match_file_start = f.tell()
            match_file_data = f.read(match_size)
            if match_file_data[-2] == 0x00 and match_file_data[-1] == 0xff:
              print("valid size assumed, saving file")
              # if the last bytes are 0x00ff, we probably have a correct size value and can save the file 
              match_file = open("./output_PICT2/" + os.path.basename(input_file_path) + "_" + hex(match_file_start) + ".pict", "wb")
              # we need to append 512 zero bytes to create a valid standalone PICT file
              match_file.write(512 * b'\x00')
              match_file.write(match_file_data)
              match_file.close()

            else:
              # if we haven't, we probably have an incorrect size value and just save it with all remaining ROM data
              # this is a bit a brute force method, but I would need to write a PICT parser to correctly handle this
              # as it seems there is no valid size present in the PICT2 file specification
              # 
              # i observed that most PICT2 files end with 0x000000FF instead of 0x00FF
              # so we could search for this here instead, but why bother, we have enough space nowadays
              print("invalid size of picture detected, saving file with all remaining data")
              f.seek(start_match - 14)
              match_file_start = f.tell()
              match_file_data = f.read(file_size - match_file_start)
              match_file = open("./output_pict2/" + os.path.basename(input_file_path) + "_INCORRECTSIZE_" + hex(match_file_start) + ".pict", "wb")
              # we need to append 512 zero bytes to create a valid standalone PICT file
              match_file.write(512 * b'\x00')
              match_file.write(match_file_data)
              match_file.close()
              # continue were we left of
              f.seek(match_file_start + match_size)

    byte = f.read(1)
