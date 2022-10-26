#!/usr/bin/env python3

import sys
import os

input_file_path = sys.argv[1]
with open(input_file_path, "rb") as f:
  byte = f.read(1)
  while byte != b"":
    if byte == b"\x11":
      byte = f.read(1)
      if byte == b"\x01":
        byte = f.read(1)
        if byte == b"\x01":
          start_match = f.tell()
          print("found start match at "+hex(f.tell()))
          f.seek(start_match - 13)
          match_size = int.from_bytes(f.read(2), byteorder='big', signed=False)
          print("size of pic: "+hex(match_size))
          f.seek(start_match - 13)
          match_file_start = f.tell()
          match_file_data = f.read(match_size)
          # check if last byte is 0xff
          if match_file_data[-1] != 0xff:
            print("last byte not 0xff, probably a false match")
            match_file = open("./output_PICT1/" + os.path.basename(input_file_path) + "_INVALID_" + hex(match_file_start) + ".pict", "wb")
          else:
            match_file = open("./output_pict1/" + os.path.basename(input_file_path) + "_" + hex(match_file_start) + ".pict", "wb")
          # we need to append 512 zero bytes to create a valid standalone PICT file
          match_file.write(512 * b'\x00')
          match_file.write(match_file_data)
          match_file.close()

    byte = f.read(1)
