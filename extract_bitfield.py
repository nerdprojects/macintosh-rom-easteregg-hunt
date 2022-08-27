#!/usr/bin/env python3

import sys
from pathlib import Path


def readBitfield(input_file, input_file_offset):

  input_file_name = input_file.name
  input_file.seek(input_file_offset)

  # operation_count is stored in register d0 in the mac rom code
  operation_count = int.from_bytes(input_file.read(4), byteorder='big', signed=False)
  # bitfield_start is stored in register a1 in the mac rom code 
  bitfield_start = input_file.tell() + int.from_bytes(input_file.read(2), byteorder='big', signed=False)
  # bitfield_offset is stored in register d1 in the mac rom code
  bitfield_offset = 0

  output_bytes = bytearray()
  
  if operation_count <= 14:
    return

  #print("trying offset "+hex(input_file_offset)+" with PICT size "+hex(operation_count))

  for count in range(operation_count):

    # check for valid PICT2 version
    if count == 14:
      if output_bytes[10] == 0x00 and output_bytes[11] == 0x11 and output_bytes[12] == 0x02 and output_bytes[13] == 0xff:
        print("found PICT header at offset "+hex(input_file_offset)+" with PICT size "+hex(operation_count))
      else:
        return

    input_file.seek(bitfield_start + (bitfield_offset // 8))
    tmp_int = int.from_bytes(input_file.read(2), byteorder='big', signed=False)
    tmp_int = tmp_int >> (7 - (bitfield_offset % 8)) 
    # check if bit 9 is set
    if tmp_int & 0x100 == 0x100:
      # if so, make the number negative, overwriting upper 3 bytes
      tmp_int = tmp_int | 0xffffff00
      # shift right 4 places, according to the mac os code
      tmp_int = tmp_int >> 4
      # make negative again, because of the previous shift
      tmp_int = tmp_int | 0xffffff00
      # manually convert it to signed
      tmp_int = tmp_int - 0xffffffff - 1
      #print("negative int "+hex(tmp_int)+" "+str(tmp_int))
      seek = bitfield_start + tmp_int
      # prevent invalid seek
      if seek < 0:
        return
      input_file.seek(seek)
      tmp_byte = input_file.read(1)
      output_bytes.append(int.from_bytes(tmp_byte, byteorder='big', signed=False))

    else:
      # else make it positive and discard upper 3 bytes
      tmp_int = tmp_int & 0x000000ff
      #print("positive int "+hex(tmp_int)+" "+str(tmp_int))
      output_bytes.append(tmp_int)
      bitfield_offset += 4

    bitfield_offset += 5
      
  #print("output bytes: "+output_bytes.hex())
  output_file_name = "./output_bitfield/" + input_file_name + "_" + hex(input_file_offset) + ".pct"
  print("writing file to " + output_file_name)
  output_file = open(output_file_name, "wb")
  output_file.write(output_bytes)


f_name = sys.argv[1]
f_size = Path(f_name).stat().st_size
f = open(f_name, "rb")

for f_offset in range(f_size):
  readBitfield(f, f_offset)
