from pymongo import MongoClient
from scrapy.utils.project import get_project_settings
from jobbank.transformations import clean_text, transform_title, transform_date, transform_job_link, add_source
import threading
import queue
from datetime import datetime  
from urllib.parse import urlparse  
import sys


class JobbankPipeline:
    def open_spider(self, spider):
        settings = get_project_settings()
        self.mongo_uri = settings.get('MONGO_URI')
        self.mongo_db = settings.get('MONGO_DATABASE')
        self.mongo_collection = settings.get('MONGO_COLLECTION')
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.mongo_collection]

        # Initialize the item queue
        self.item_queue = queue.Queue()
        spider.item_queue = self.item_queue  # Set the item queue for the spider

        # Start the worker threads (adjust the number as needed)
        self.spider = spider  # Store the spider instance
        for _ in range(6):  # Example: 6 worker threads
            worker_thread = threading.Thread(target=self.process_items)
            # Allow the main thread to exit even if workers are running
            worker_thread.daemon = True
            worker_thread.start()

    def close_spider(self, spider):
        self.client.close()
        # Optionally, wait for all threads to finish processing
        self.item_queue.join()

    def _validate_item(self, item):
        """
        Validates the JobbankItem to ensure it has essential data and conforms to
        expected formats.
        """

        errors = []  # Collect validation errors

        # 1. Required Fields
        for field in ['title', 'date', 'business', 'location', 'job_link']:
            if not item.get(field):
                errors.append(f"Missing '{field}' in item.")

        # 2. Data Type and Format Validation
        if item.get('date') and not isinstance(item['date'], str):
            errors.append("Invalid data type for 'date'. Should be a string.")
        if item.get('date') and not validate_date_format(item['date']):
            errors.append(f"Invalid date format: {
                          item['date']}. Expected format: Month Day, Year")

        # 3. URL Validation (Optional)
        if item.get('job_link') and not validate_url(item['job_link']):
            errors.append(f"Invalid job link: {item['job_link']}.")

        # 5. Raise Error if Validation Fails
        if errors:
            raise ValueError(f"Validation Errors: {errors}")

        return item

    def _process_data(self, item):
        try:
            item['title'] = transform_title(clean_text(
                item.get('title', '')), self.spider.unwanted_text)

            # Clean and process the date
            date_str = clean_text(item.get('date', ''))
            self.spider.logger.debug(
                f"Cleaned date: '{date_str}'")  # Log cleaned date

            # Use the updated transform_date function
            item['date'] = transform_date(date_str)

            item['job_link'] = transform_job_link(
                item.get('job_link', ''), self.spider.base_url)
            item = add_source(item, self.spider.start_urls[0])

        except Exception as e:
            self.spider.logger.error(f"Error processing item: {e}")

    def _insert_item(self, item):
        self.collection.update_one(
            {'job_link': item['job_link']}, {'$set': dict(item)}, upsert=True
        )
        return item

    def process_items(self):
        while True:
            try:
                item = self.item_queue.get()
                item = self._validate_item(item)  # Validate the item
                self._process_data(item)
                self._insert_item(item)
                self.spider.logger.info(f"Processed and saved: {item}")
            except queue.Empty:
                pass
            except Exception as e:
                self.spider.logger.error(f"Error in process_items: {e}")
            finally:  # Always call task_done() in a finally block
                self.item_queue.task_done()

    def signal_handler(self, sig, frame):
        # Close the MongoDB connection and exit
        self.client.close()
        sys.exit(0)

# Helper Functions for Validation


def validate_date_format(date_str):
    """Checks if the date string matches the expected format Month Day, Year."""
    try:
        datetime.strptime(date_str, '%B %d, %Y')
        return True
    except ValueError:
        return False


def validate_url(url):
    """Basic URL validation. Consider using a more robust URL validator if needed."""
    try:
        result = urlparse(url)
        return result.scheme in ('http', 'https') and result.netloc
    except ValueError:
        return False
