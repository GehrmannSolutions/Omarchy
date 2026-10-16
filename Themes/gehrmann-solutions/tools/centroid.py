#!/usr/bin/env python3
"""Print the alpha-weighted centroid of a PNG as fractions of its width and height.

The logo's visual mass is not at the centre of its bounding box (the cloud
reaches further right than left), so the backgrounds centre the logo by its
centroid instead. Reads a binary PGM of the alpha channel from stdin:

  magick logo.png -alpha extract -resize 512x512 pgm:- | centroid.py
"""
import sys

data = sys.stdin.buffer.read()
fields, pos = [], 0
while len(fields) < 4:
    while data[pos:pos + 1].isspace():
        pos += 1
    if data[pos:pos + 1] == b"#":
        pos = data.index(b"\n", pos)
        continue
    end = pos
    while not data[end:end + 1].isspace():
        end += 1
    fields.append(data[pos:end])
    pos = end
pos += 1
if fields[0] != b"P5" or int(fields[3]) > 255:
    sys.exit("expected an 8-bit binary PGM")
width, height = int(fields[1]), int(fields[2])
pixels = data[pos:pos + width * height]

total = sx = sy = 0
for y in range(height):
    row = pixels[y * width:(y + 1) * width]
    for x, a in enumerate(row):
        if a:
            total += a
            sx += a * x
            sy += a * y
if not total:
    sys.exit("image is fully transparent")
print(f"{(sx / total + 0.5) / width:.5f} {(sy / total + 0.5) / height:.5f}")
