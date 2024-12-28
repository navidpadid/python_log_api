import random
from datetime import datetime, timedelta

log_levels = ["INFO", "ERROR", "DEBUG", "WARN"]
messages = {
    "INFO": ["User logged in", "User logged out"],
    "ERROR": ["Failed to load resource", "Failed to save file", "Failed to connect to server", "Failed to upload file", "Failed to download file", "Failed to open file"],
    "DEBUG": ["Resource loaded successfully", "File saved successfully", "Connection established", "File uploaded successfully", "File downloaded successfully", "File opened successfully"],
    "WARN": ["Low disk space", "High memory usage", "Low battery", "High CPU usage", "Low memory", "High network usage"]
}

def generate_log_entries(num_entries):
    log_entries = []
    current_time = datetime(2024, 12, 26, 18, 30, 0)
    for _ in range(num_entries):
        log_level = random.choice(log_levels)
        message = random.choice(messages[log_level])
        log_entry = f"{log_level} {current_time.strftime('%Y-%m-%d %H:%M:%S')} {message}"
        log_entries.append(log_entry)
        current_time += timedelta(minutes=1)
    return log_entries

def write_log_file(filename, log_entries):
    with open(filename, 'w') as file:
        for entry in log_entries:
            file.write(entry + '\n')
            
def log_generate(name, num_entries):
    filename = "{}.log".format(name)
    log_entries = generate_log_entries(num_entries)
    write_log_file(filename, log_entries)
    print(f"Log file '{filename}' with {num_entries} entries created successfully.")

def main():
    log_generate("tiny", 20000)
    log_generate("small", 200000)
    log_generate("medium", 2000000)
    log_generate("huge", 25000000)

if __name__ == "__main__":
    main()
