import signal
import sys
import json
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import pymongo
import re
from datetime import datetime
import time

# Set up logging
logging.basicConfig(filename='scraping.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Selenium setup
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Path to the Chrome binary
chrome_binary_path = r"C:\Users\aouad\OneDrive\Bureau\stage_ine2\chrome-win64\chrome.exe"
chrome_options.binary_location = chrome_binary_path

# Path to the ChromeDriver executable
driver_path = r"C:\Users\aouad\OneDrive\Bureau\stage_ine2\chromedriver-win64\chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# List to store job data
job_data_list = []

def clean_text(text):
    """Clean text by removing unwanted characters and extra spaces."""
    return re.sub(r'\s+', ' ', text).strip()

def transform_date(date_str):
    """Transform date string to a datetime object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")  # Update format as needed
    except ValueError:
        return None

def scroll_within_element(driver, element, scroll_pause_time=1):
    """Scroll within an element to ensure all content is loaded."""
    last_height = driver.execute_script("return arguments[0].scrollHeight;", element)
    while True:
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", element)
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return arguments[0].scrollHeight;", element)
        if new_height == last_height:
            break
        last_height = new_height

def save_data():
    """Save data to MongoDB and JSON file."""
    if job_data_list:
        for job_data in job_data_list:
            print(json.dumps(job_data, ensure_ascii=False, indent=4))
        logging.info("Data printed to console.")
    else:
        logging.info("No data to print.")

def signal_handler(sig, frame):
    """Handle signals for graceful shutdown."""
    logging.info('Interrupt received, saving data and closing browser...')
    save_data()
    driver.quit()
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    url = 'https://www.simplyhired.ca/search?q=&l=Canada'
    driver.get(url)

    # Increase the timeout duration
    timeout = 30

    try:
        # Wait for the page to load
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.css-0 div[data-testid="searchSerpJob"]'))
        )
    except Exception as e:
        logging.error(f"Timeout waiting for job elements: {e}")
        driver.save_screenshot('timeout_error.png')
        raise

    # Extract job listings
    job_elements = driver.find_elements(By.CSS_SELECTOR, 'li.css-0 div[data-testid="searchSerpJob"]')
    logging.info(f"Found {len(job_elements)} job elements.")
    
    for job in job_elements:
        try:
            # Click on the job offer to make the details appear in the aside
            job.click()

            # Wait for the aside to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'aside[aria-label]'))
            )

            # Extract job details from the aside
            aside = driver.find_element(By.CSS_SELECTOR, 'aside[aria-label]')

            # Scroll within the aside element to load all content
            scroll_within_element(driver, aside)

            title = clean_text(aside.find_element(By.CSS_SELECTOR, 'h2[data-testid="viewJobTitle"]').text)
            company = clean_text(aside.find_element(By.CSS_SELECTOR, 'span[data-testid="viewJobCompanyName"] span[data-testid="detailText"]').text)
            location = clean_text(aside.find_element(By.CSS_SELECTOR, 'span[data-testid="viewJobCompanyLocation"] span[data-testid="detailText"]').text)
            description = clean_text(aside.find_element(By.CSS_SELECTOR, 'div[data-testid="viewJobBodyJobFullDescriptionContent"]').text)

            # Extract job type if available
            job_type = clean_text(aside.find_element(By.CSS_SELECTOR, 'span[data-testid="viewJobBodyJobDetailsJobType"] span[data-testid="detailText"]').text) if aside.find_elements(By.CSS_SELECTOR, 'span[data-testid="viewJobBodyJobDetailsJobType"] span[data-testid="detailText"]') else 'Not provided'

            # Extract compensation if available
            compensation = clean_text(aside.find_element(By.CSS_SELECTOR, 'span[data-testid="viewJobBodyJobCompensation"] span[data-testid="detailText"]').text) if aside.find_elements(By.CSS_SELECTOR, 'span[data-testid="viewJobBodyJobCompensation"] span[data-testid="detailText"]') else 'Not provided'

            # Extract posting timestamp
            posting_timestamp = clean_text(aside.find_element(By.CSS_SELECTOR, 'span[data-testid="viewJobBodyJobPostingTimestamp"] span[data-testid="detailText"]').text)
            posting_date = transform_date(posting_timestamp)

            # Extract qualifications if available
            qualifications_elements = aside.find_elements(By.CSS_SELECTOR, 'div[data-testid="viewJobQualificationsContainer"] li[data-testid="viewJobQualificationItem"]')
            qualifications = [clean_text(qual.text) for qual in qualifications_elements]

            # Extract schedule if available
            schedule_elements = aside.find_elements(By.CSS_SELECTOR, 'div[data-testid="viewJobBodyJobFullDescriptionContent"] ul:nth-of-type(2) li')
            schedule = [clean_text(sched.text) for sched in schedule_elements]

            # Extract supplemental pay types if available
            pay_types_elements = aside.find_elements(By.CSS_SELECTOR, 'div[data-testid="viewJobBodyJobFullDescriptionContent"] ul:nth-of-type(3) li')
            pay_types = [clean_text(pay.text) for pay in pay_types_elements]

            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'job_type': job_type,
                'compensation': compensation,
                'posting_date': posting_date,
                'qualifications': qualifications,
                'schedule': schedule,
                'supplemental_pay_types': pay_types
            }

            # Add job data to list
            job_data_list.append(job_data)
            logging.info(f"Job data added: {job_data}")

        except Exception as e:
            logging.error(f"Error extracting job details: {e}")

finally:
    driver.quit()
    save_data()