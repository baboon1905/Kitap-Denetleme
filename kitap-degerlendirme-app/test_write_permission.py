#!/usr/bin/env python3
import os
with open('test_write_direct.txt', 'w') as f:
    f.write('test from python script')
print(f"✅ Can write to: {os.getcwd()}")
