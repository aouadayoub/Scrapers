import scrapy
from scrapy.http import HtmlResponse
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from jobbank.items import JobbankItem
from jobbank.transformations import clean_text, transform_title, transform_job_link
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import queue
import signal


class JobbankSpider(scrapy.Spider):
    name = 'jobbank'
    start_urls = ['https://www.jobbank.gc.ca/jobsearch/']
    base_url = 'https://www.jobbank.gc.ca'
    unwanted_text = 'Unwanted Text Here'
    canada_logo_svg = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Flag_of_Canada_%28Pantone%29.svg/1200px-Flag_of_Canada_%28Pantone%29.svg.png'
    country = 'Canada'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Retrieve settings
        settings = get_project_settings()
        chrome_binary_location = settings.get('CHROME_BINARY_LOCATION')
        chrome_driver_path = settings.get('CHROME_DRIVER_EXECUTABLE_PATH')

        options = Options()
        if chrome_binary_location:
            options.binary_location = chrome_binary_location

        self.service = Service(executable_path=chrome_driver_path)
        self.driver = webdriver.Chrome(service=self.service, options=options)

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Initialize queue for items
        self.item_queue = queue.Queue()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)
        self._close_popup_if_present()
        self._scrape_pages()

    def _close_popup_if_present(self):
        try:
            close_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.ID, 'j_id_36:outOfCanadaCloseBtn')
                )
            )
            close_button.click()
        except (NoSuchElementException, TimeoutException) as e:
            self.logger.debug(f'Popup close failed: {e}')

    def _scrape_pages(self):
        while True:
            try:
                # Wait for the job listings to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'article.action-buttons'))
                )
                response = HtmlResponse(
                    url=self.driver.current_url,
                    body=self.driver.page_source,
                    encoding='utf-8',
                )
                self._parse_jobs(response)

                # Click the 'Show More Results' button
                if not self._click_more_button():
                    break

            except Exception as e:
                self.logger.error(f"Error in _scrape_pages: {e}")
                break

        self.driver.quit()

    def _parse_jobs(self, response):
        job_postings = response.css('article.action-buttons')

        for job in job_postings:
            try:
                title = job.css('h3.title span.noctitle::text').get()
                date = job.css('ul.list-unstyled li.date::text').get().strip()
                business = job.css('ul.list-unstyled li.business::text').get()
                location = job.css(
                    'ul.list-unstyled li.location::text').getall()
                salary = job.css('ul.list-unstyled li.salary::text').get()
                job_link = job.css('a.resultJobItem::attr(href)').get()

                location_text = ' '.join(location).strip(
                ) if location else 'Not specified'

                item = JobbankItem(
                    title=transform_title(
                        clean_text(title), self.unwanted_text),
                    date=date,
                    business=clean_text(business),
                    location=location_text,
                    salary=clean_text(salary),
                    job_link=transform_job_link(job_link, self.base_url),
                    logo=self.canada_logo_svg,
                    source='Job bank',
                    country=self.country,
                )

                self.item_queue.put(item)
            except Exception as e:
                self.logger.error(f"Error parsing job details: {e}")

    def _click_more_button(self):
        try:
            more_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'moreresultbutton'))
            )
            more_button.click()
            return True
        except (NoSuchElementException, TimeoutException) as e:
            self.logger.debug(f'Show more results button click failed: {e}')
            return False

    def signal_handler(self, sig, frame):
        try:
            self.driver.quit()
        except Exception as e:
            self.logger.error(f'Error closing the driver: {e}')

        # Wait for all items in the queue to be processed
        while not self.item_queue.empty():
            try:
                self.item_queue.get(block=False)
            except queue.Empty:
                pass

        sys.exit(0)
