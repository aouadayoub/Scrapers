from datetime import datetime
import logging
from urllib.parse import urljoin


class InvalidDateFormat(Exception):
    """Custom exception for invalid date formats."""
    pass


def clean_text(text):
    if text:
        return ' '.join(text.split())
    return text


def transform_title(title, unwanted_text):
    if title:
        return title.replace(unwanted_text, '').strip()
    return title


def transform_date(date_str):
    if not isinstance(date_str, str):
        raise TypeError(f"Expected a string for date, but got {
                        type(date_str)}: {date_str}")

    try:
        # Debug log the received date string
        logging.debug(f"Received date_str for transformation: '{date_str}'")

        # Adjust date parsing to handle 'Month Day, Year' format
        date_obj = datetime.strptime(date_str, '%B %d, %Y')
        return date_obj.strftime('%Y-%m-%d')  # Return as 'YYYY-MM-DD'
    except ValueError:
        # Log the error with the problematic date string
        logging.error(f'Invalid date format: {
                      date_str}. Expected format: "Month Day, Year"')
        raise ValueError(f'Invalid date format: {
                         date_str}. Expected format: "Month Day, Year"')


def transform_job_link(link, base_url):
    if not link.startswith('http'):
        link = urljoin(base_url, link)
    return link


def add_source(item):
    item['source'] = 'Job bank'
    return item
