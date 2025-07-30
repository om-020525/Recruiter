import os
import datetime

class Logger:
    def __init__(self, log_file_path="web_logger.log", show_timestamp=False):
        self.log_file_path = log_file_path
        self.show_timestamp = show_timestamp
        # Ensure the log file exists
        if not os.path.exists(self.log_file_path):
            open(self.log_file_path, 'w').close()
    
    def INFO(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.show_timestamp:
            log_entry = f"[{timestamp}] INFO: {message}\n"
        else:
            log_entry = f"INFO: {message}\n"
        
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(log_entry)
        except Exception as e:
            # Fallback to print if logging fails
            print(f"Logging failed: {e}")
            print(f"[{timestamp}] INFO: {message}")

# Create a global logger instance
_logger = Logger()

# Export the INFO method for easy import
INFO = _logger.INFO 