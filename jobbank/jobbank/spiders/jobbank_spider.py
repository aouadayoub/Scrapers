import datetime
import scrapy
#import os
import json
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
import logging
import signal
import sys
import pymongo

class JobbankSpider(scrapy.Spider):
    name = 'jobbank'
    start_urls = ['https://www.jobbank.gc.ca/jobsearch/']
    base_url = 'https://www.jobbank.gc.ca'
    unwanted_text = 'Unwanted Text Here'  # Set this to the unwanted text to be removed

    # Updated to use the SVG image link for the Canada flag
    canada_logo_svg = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Flag_of_Canada_%28Pantone%29.svg/1200px-Flag_of_Canada_%28Pantone%29.svg.png'

    def __init__(self, *args, **kwargs):
        super(JobbankSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        
        # Register signal handler for interrupt early
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        """# MongoDB setup
        self.mongo_uri = settings.get('MONGO_URI')
        self.mongo_db = settings.get('MONGO_DATABASE')
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db['job_data']"""
        
        # Selenium setup
        options = Options()
        options.binary_location = settings.get('CHROME_BINARY_LOCATION')
        self.service = Service(settings.get('CHROME_DRIVER_PATH'))
        self.driver = webdriver.Chrome(service=self.service, options=options)
        self.job_data_list = []
        self.seen_jobs = set()  

        # Set up logging
        logging.basicConfig(filename='jobbank.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)
        logging.info("Started scraping...")
        try:
            # Close the initial popup if present
            close_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "j_id_39:outOfCanadaCloseBtn"))
            )
            close_button.click()
        except Exception as e:
            logging.warning(f"Popup close error: {e}")

        while True:
            # Wait for dynamic content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article.action-buttons'))
            )

            # Convert Selenium page source to Scrapy response
            response = HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')
            self.parse_jobs(response)

            # Try to click the "Show more results" button
            try:
                more_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'moreresultbutton'))
                )
                more_button.click()
                logging.info("Clicked 'Show more results' button.")
            except Exception:
                logging.info("No more results button found or clickable.")
                break

        self.save_data()  # Save all collected data
        self.driver.quit()

    def parse_jobs(self, response):
        job_postings = response.css('article.action-buttons')
        logging.info(f"Found {len(job_postings)} job postings on the page.")
        
        for job in job_postings:
            title = job.css('h3.title span.noctitle::text').get()
            date = job.css('ul.list-unstyled li.date::text').get()
            business = job.css('ul.list-unstyled li.business::text').get()
            location = job.css('ul.list-unstyled li.location::text').getall()
            salary = job.css('ul.list-unstyled li.salary::text').get()
            job_link = job.css('a.resultJobItem::attr(href)').get()

            location_text = ' '.join(location).strip() if location else "Not specified"

            job_data = {
                'title': self.transform_title(self.clean_text(title)),
                'date': self.transform_date(self.clean_text(date)),
                'business': self.clean_text(business),
                'location': location_text,
                'salary': self.clean_text(salary),
                'job_link': self.transform_job_link(job_link),
                'logo_image': self.canada_logo_svg,
                'country': 'Canada' 
            }

            logging.debug(f"Extracted job data: {job_data}")

            self.job_data_list.append(job_data)

        logging.info(f"Collected and updated job postings.")

    def clean_text(self, text):
        return ' '.join(text.split())

    def transform_title(self, title):
        if self.unwanted_text in title:
            title = title.replace(self.unwanted_text, "")
        return title

    def transform_date(self, date_element):
        """ Transform date from 'July 19, 2024' to '2024-07-19' """
        if date_element:
            date_str = self.clean_text(date_element.strip())
            try:
                date_obj = datetime.datetime.strptime(date_str, '%B %d, %Y')
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                logging.error(f"Date transformation failed for date: {date_str}")
                return None
        return None

    def transform_job_link(self, job_link):
        if job_link and not job_link.startswith(self.base_url):
            job_link = f"{self.base_url}{job_link}"
        return str(job_link) if job_link else None

    def save_data(self):
        filename = 'job_data.json'

        # 1. Read existing data (if any)
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = []  

        # 2. Combine and deduplicate data
        all_data = existing_data + self.job_data_list
        unique_data = []
        seen_jobs = set()

        for job in all_data:
            job_key = (job['title'], job['business'], job['location']) 
            if job_key not in seen_jobs:
                unique_data.append(job)
                seen_jobs.add(job_key)

        # 3. Save the unique data to the JSON file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(unique_data, f, ensure_ascii=False, indent=4)
            logging.info(f"Job data saved to {filename}")
        except Exception as e:
            logging.error(f"Failed to save job data: {e}")

        # 4. Save data to MongoDB
        """try:
            for job in unique_data:
                self.collection.update_one({'job_link': job['job_link']}, {'$set': job}, upsert=True)
            logging.info("Job data saved to MongoDB")
        except Exception as e:
            logging.error(f"Failed to save job data to MongoDB: {e}")"""

    def signal_handler(self, sig, frame):
        logging.info('Interrupted! Saving data...')
        self.save_data()
        try:
            self.driver.quit()
        except Exception as e:
            logging.error(f"Error while quitting the driver: {e}")
        #self.client.close()
        sys.exit(0)
