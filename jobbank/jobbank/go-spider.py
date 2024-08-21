# go-spider.py
import subprocess
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from jobbank.spiders.jobbank_spider import JobbankSpider
import time

def start_mongodb():
    # Start MongoDB in the background
    subprocess.Popen(["mongod"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def wait_for_mongodb():
    # Wait for MongoDB to start up
    time.sleep(10)  # Adjust this as needed based on your system

if __name__ == "__main__":
    # Start MongoDB
    start_mongodb()
    
    # Wait for MongoDB to be fully up and running
    wait_for_mongodb()

    # Get Scrapy settings
    settings = get_project_settings()

    # Create a CrawlerProcess with the settings
    process = CrawlerProcess(settings)

    # Run the JobbankSpider
    process.crawl(JobbankSpider)

    # Start the crawling process
    process.start()
