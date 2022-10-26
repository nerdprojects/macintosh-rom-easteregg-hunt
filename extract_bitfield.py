#!/usr/bin/env python3

import sys
import os
from pathlib import Path

def readBitfield(input_file, input_file_offset, input_file_size):

  input_file_name = os.path.basename(input_file.name)
  input_file.seek(input_file_offset)

  # operation_count is stored in register d0 in the mac rom code
  operation_count = int.from_bytes(input_file.read(4), byteorder='big', signed=False)
  # bitfield_start is stored in register a1 in the mac rom code 
  bitfield_start = input_file.tell() + int.from_bytes(input_file.read(2), byteorder='big', signed=False)
  # bitfield_offset is stored in register d1 in the mac rom code
  bitfield_offset = 0

  output_bytes = bytearray()
  
  remaining_file_size = input_file_size - input_file_offset
  if operation_count <= 14 or operation_count > remaining_file_size:
    return

  #print("trying offset "+hex(input_file_offset)+" with PICT size "+hex(operation_count))

  pict_version = "INVALIDPICT"
  for count in range(operation_count):

    # check for valid PICT headers
    if count == 14:
      # note that the size field (named operation count here) of a PICT2 image is not reliable, as it is only 2 bytes long
      # images bigger that 0xffff will not be saved correctly by this script at the moment
      if output_bytes[10] == 0x00 and output_bytes[11] == 0x11 and output_bytes[12] == 0x02 and output_bytes[13] == 0xff:
        print("found PICT2 header at offset "+hex(input_file_offset)+" with PICT size "+hex(operation_count))
        pict_version = "PICT2"
      elif output_bytes[10] == 0x11 and output_bytes[11] == 0x01 and output_bytes[12] == 0x01:
        print("found PICT1 header at offset "+hex(input_file_offset)+" with PICT size "+hex(operation_count))
        pict_version = "PICT1"
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
  if output_bytes[-1] != 0xff:
    print("end byte not matching 0xff")
    pict_version = "INVALID"

  output_file_path = "./output_bitfield/" + input_file_name + "_" + pict_version + "_" + hex(input_file_offset) + ".pict"
  print("writing file to " + output_file_path)
  output_file = open(output_file_path, "wb")
  # we need to append 512 zero bytes to create a valid PICT file
  output_file.write(512 * b'\x00')
  output_file.write(output_bytes)


f_path = sys.argv[1]
f_size = Path(f_path).stat().st_size
f = open(f_path, "rb")

for f_offset in range(f_size):
  readBitfield(f, f_offset, f_size)
