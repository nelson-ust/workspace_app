


# import logging
# from logging.handlers import TimedRotatingFileHandler
# import concurrent.futures
# import os
# from datetime import datetime

# # Determine the base directory
# base_dir = os.path.dirname(os.path.abspath(__file__))

# # Ensure the logs directory exists in the base directory
# logs_dir = os.path.join(base_dir, 'workplanlogs')
# os.makedirs(logs_dir, exist_ok=True)

# # Get the current date to use in the log file name
# current_date = datetime.now().strftime("%Y-%m-%d")
# log_filename = os.path.join(logs_dir, f'workplan_{current_date}.log')

# # Configure logging
# logger = logging.getLogger('workplan_logger')
# logger.setLevel(logging.INFO)

# # Create a TimedRotatingFileHandler that appends the current date to the log file name
# handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1, backupCount=30)
# handler.suffix = "%Y-%m-%d"
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# # Set up ThreadPoolExecutor for asynchronous logging
# log_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# def async_log(level):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             # Extract the log message from the function's return value
#             if args:
#                 self = args[0]
#                 message = func(self, *args[1:], **kwargs)
#             else:
#                 message = func(*args, **kwargs)
#             # Submit the log message to the logger asynchronously
#             log_executor.submit(logger.log, level, message)
#             return message
#         return wrapper
#     return decorator



#logging_config.py
import logging
from logging.handlers import TimedRotatingFileHandler
import concurrent.futures
import os
from datetime import datetime

# Determine the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Ensure the logs directory exists in the base directory
logs_dir = os.path.join(base_dir, 'workplanlogs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
logger = logging.getLogger('workplan_logger')
logger.setLevel(logging.INFO)

# Create a TimedRotatingFileHandler that appends the current date to the log file name
current_date = datetime.now().strftime("%Y-%m-%d")
log_filename = os.path.join(logs_dir, f'workplan_{current_date}.log')
handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1, backupCount=30)
handler.suffix = "%Y-%m-%d"
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Set up ThreadPoolExecutor for asynchronous logging
log_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# def async_log(level):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             # Extract the log message from the function's return value
#             if args:
#                 self = args[0]
#                 message = func(self, *args[1:], **kwargs)
#             else:
#                 message = func(*args, **kwargs)
#             # Submit the log message to the logger asynchronously
#             log_executor.submit(logger.log, level, message)
#             return message
#         return wrapper
#     return decorator


def async_log(level):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract the log message from the function's return value
            message = func(*args, **kwargs)
            # Submit the log message to the logger asynchronously
            log_executor.submit(logger.log, level, message)
            return message
        return wrapper
    return decorator