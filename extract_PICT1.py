#!/usr/bin/env python3

import sys

input_file_name = sys.argv[1]
with open(input_file_name, "rb") as f:
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
          match_file = open("./output_pict1/"+input_file_name + hex(match_file_start) + ".pct", "wb")
          match_file.write(match_file_data)
          match_file.close()

    byte = f.read(1)
