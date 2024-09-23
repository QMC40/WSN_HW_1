"""
    File: ./logging_config/logger.py
    Author: Aaron Fortner
    Date: 09/22/2024
    Version: 0.6

    Description: Config file for the logger used in the Wireless Sensor Network simulation.

    See the main README.md file for detailed information, installation instructions, and usage.
"""
import logging

# Set logging level
LOGGING_LEVEL = logging.DEBUG


# Configure logging
def get_logger() -> logging.Logger:
    """
    Configure the logger for the Wireless Sensor Network simulation.
    :return logging.Logger: The logger object
    """
    logger = logging.getLogger('wsn_simulation')
    logger.setLevel(LOGGING_LEVEL)

    # Set up logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Configure the console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # Add the handler if it doesn't already exist
    if not logger.hasHandlers():
        logger.addHandler(console_handler)

    return logger
