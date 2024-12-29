# log_viewer/log_viewer.py
import os
import re
from collections import deque

class LogViewer:
    def __init__(self, file_path, keyword, num_lines):
        self.file_path = file_path
        self.keyword = keyword
        self.num_lines = num_lines
        self.lines = deque(maxlen=num_lines)

    def is_valid_filename(self):
        return re.match(r'^[\w,\s-]+\.[A-Za-z]{3}$', self.file_path) is not None

    def is_valid_keyword(self):
        return re.match(r'^[\w\s-]*$', self.keyword) is not None

    def read_small_file(self):
        with open(self.file_path, 'r') as file:
            read_lines = file.readlines()
            if self.keyword == '':
                self.lines = read_lines[-1:-(self.num_lines+1):-1]
            else:
                cntr = 0
                for line in reversed(read_lines):
                    if cntr == self.num_lines:
                        break
                    if self.keyword in line:
                        self.lines.append(line)
                        cntr += 1

    def read_large_file(self):
        with open(self.file_path, 'rb') as file:
            file.seek(0, os.SEEK_END)
            buffer_size = 500 * 1024  # Read in chunks of 500 lines (approx. 500 KB)
            buffer = b''
            position = file.tell()

            while position > 0 and len(self.lines) < self.num_lines:
                position = max(0, position - buffer_size)
                file.seek(position)
                buffer = file.read(buffer_size) + buffer
                cur_lines = buffer.split(b'\n')
                buffer = cur_lines.pop(0)  # Keep the last partial line for the next read

                for line in reversed(cur_lines):
                    if len(line) > 0 and self.keyword.encode() in line:
                        self.lines.append(line.decode().strip())
                        if len(self.lines) == self.num_lines:
                            break

    def get_lines(self):
        file_size = os.path.getsize(self.file_path)
        if file_size <= 5 * 1024 * 1024:  # 5 MB
            self.read_small_file()
        else:
            self.read_large_file()
        return list(self.lines)
