import os
import re
from collections import deque

# Constants
SMALL_FILE_SIZE_LIMIT = 5 * 1024 * 1024  # 5 MB
BUFFER_SIZE = 500 * 1024  # 500 KB

class LogViewer:
    def __init__(self, filename, filepath, keyword, num_lines):
        """
        Initialize the LogViewer instance.

        Args:
            filename (str): The name of the log file.
            filepath (str): The path to the log file.
            keyword (str): The keyword to filter log lines.
            num_lines (int): The number of log lines to retrieve.
        """
        self.__file_name = filename
        self.__file_path = filepath
        self.__keyword = keyword
        self.__num_lines = num_lines
        self.__lines = deque(maxlen=num_lines)

    def is_valid_filename(self):
        """
        Check if the filename is valid.

        Returns:
            bool: True if the filename is valid, False otherwise.
        """
        return re.match(r'^[\w,\s-]+\.[A-Za-z]{3}$', self.__file_name) is not None

    def is_valid_keyword(self):
        """
        Check if the keyword is valid.

        Returns:
            bool: True if the keyword is valid, False otherwise.
        """
        return re.match(r'^[\w\s-]*$', self.__keyword) is not None

    def __read_small_file(self):
        """
        Read a small log file (one time in memory) and filter lines based on the keyword.
        """
        with open(self.__file_path, 'r') as file:
            read_lines = file.readlines()
            if self.__keyword == '':
                self.__lines.extend(read_lines[-1:-(self.__num_lines+1):-1])
            else:
                cntr = 0
                for line in reversed(read_lines):
                    if cntr == self.__num_lines:
                        break
                    if self.__keyword in line:
                        self.__lines.append(line)
                        cntr += 1

    def __read_small_file_generator(self):
        """
        Generator (used for streaming) to read a small log file and filter lines based on the keyword.

        Yields:
            str: The filtered log lines.
        """
        with open(self.__file_path, 'r') as file:
            read_lines = file.readlines()
            if self.__keyword == '':
                for line in read_lines[-1:-(self.__num_lines+1):-1]:
                    yield line
            else:
                cntr = 0
                for line in reversed(read_lines):
                    if cntr == self.__num_lines:
                        break
                    if self.__keyword in line:
                        yield line
                        cntr += 1


    def __read_large_file(self):
        """
        Read a large log file (load chunks into memory) and filter lines based on the keyword.
        """
        with open(self.__file_path, 'rb') as file:
            file.seek(0, os.SEEK_END)
            buffer = b''
            position = file.tell()

            while position > 0 and len(self.__lines) < self.__num_lines:
                position = max(0, position - BUFFER_SIZE)
                file.seek(position)
                buffer = file.read(BUFFER_SIZE) + buffer
                cur_lines = buffer.split(b'\n')
                buffer = cur_lines.pop(0)  # Keep the last partial line for the next read

                for line in reversed(cur_lines):
                    if len(line) > 0 and self.__keyword.encode() in line:
                        self.__lines.append(f"{line.decode().strip()}\n")
                        if len(self.__lines) == self.__num_lines:
                            break


    def __read_large_file_generator(self):
        """
        Generator (used for streaming) to read a large log file (load chunks into memory) and filter lines based on the keyword.

        Yields:
            str: The filtered log lines.
        """
        with open(self.__file_path, 'rb') as file:
            file.seek(0, os.SEEK_END)
            buffer = b''
            position = file.tell()
            cntr = 0

            while position > 0 and cntr < self.__num_lines:
                position = max(0, position - BUFFER_SIZE)
                file.seek(position)
                buffer = file.read(BUFFER_SIZE) + buffer
                cur_lines = buffer.split(b'\n')
                buffer = cur_lines.pop(0)  # Keep the last partial line for the next read

                for line in reversed(cur_lines):
                    if len(line) > 0 and self.__keyword.encode() in line:
                        yield line.decode().strip()
                        cntr += 1
                        if cntr == self.__num_lines:
                            break

    def get_lines(self):
        """
        Get the filtered log lines.

        Returns:
            list: The filtered log lines.
        """
        file_size = os.path.getsize(self.__file_path)
        if file_size <= SMALL_FILE_SIZE_LIMIT:
            self.__read_small_file()
        else:
            self.__read_large_file()
        return list(self.__lines)

    def get_lines_generator(self):
        """
        Get the filtered log lines as a generator.

        Returns:
            generator: The filtered log lines.
        """
        file_size = os.path.getsize(self.__file_path)
        if file_size <= SMALL_FILE_SIZE_LIMIT:
            return self.__read_small_file_generator()
        else:
            return self.__read_large_file_generator()
