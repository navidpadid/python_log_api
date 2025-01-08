import random
from datetime import datetime, timedelta

# Constants
LOG_LEVELS = ["INFO", "ERROR", "DEBUG", "WARN"]
MESSAGES = {
    "INFO": ["User logged in", "User logged out"],
    "ERROR": ["Failed to load resource", "Failed to save file", "Failed to connect to server", "Failed to upload file", "Failed to download file", "Failed to open file"],
    "DEBUG": ["Resource loaded successfully", "File saved successfully", "Connection established", "File uploaded successfully", "File downloaded successfully", "File opened successfully"],
    "WARN": ["Low disk space", "High memory usage", "Low battery", "High CPU usage", "Low memory", "High network usage"]
}
START_TIME = datetime(2024, 12, 26, 18, 30, 0)
TIME_INCREMENT = timedelta(minutes=1)

class LogGenerator:
    def __init__(self, log_levels, messages, start_time, time_increment):
        """
        Initialize the LogGenerator instance.

        Args:
            log_levels (list): List of log levels.
            messages (dict): Dictionary of messages for each log level.
            start_time (datetime): The start time for log entries.
            time_increment (timedelta): The time increment between log entries.
        """
        self.__log_levels = log_levels
        self.__messages = messages
        self.__current_time = start_time
        self.__time_increment = time_increment

    def __generate_log_entries(self, num_entries):
        """
        Generate log entries.

        Args:
            num_entries (int): Number of log entries to generate.

        Returns:
            list: List of generated log entries.
        """
        log_entries = []
        for _ in range(num_entries):
            log_level = random.choice(self.__log_levels)
            message = random.choice(self.__messages[log_level])
            log_entry = f"{log_level} {self.__current_time.strftime('%Y-%m-%d %H:%M:%S')} {message}"
            log_entries.append(log_entry)
            self.__current_time += self.__time_increment
        return log_entries

    def __write_log_file(self, filename, log_entries):
        """
        Write log entries to a file.

        Args:
            filename (str): The name of the log file.
            log_entries (list): List of log entries to write.
        """
        with open(filename, 'w') as file:
            for entry in log_entries:
                file.write(entry + '\n')

    def log_generate(self, name, num_entries):
        """
        Generate and write log entries to a file.

        Args:
            name (str): The base name of the log file.
            num_entries (int): Number of log entries to generate.
        """
        filename = f"{name}.log"
        log_entries = self.__generate_log_entries(num_entries)
        self.__write_log_file(filename, log_entries)
        print(f"Log file '{filename}' with {num_entries} entries created successfully.")

def main():
    log_generator = LogGenerator(LOG_LEVELS, MESSAGES, START_TIME, TIME_INCREMENT)
    log_generator.log_generate("tiny", 20000)
    log_generator.log_generate("small", 200000)
    log_generator.log_generate("medium", 2000000)
    log_generator.log_generate("huge", 25000000)

if __name__ == "__main__":
    main()
