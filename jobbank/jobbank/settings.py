# Scrapy settings for jobbank project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "jobbank"

SPIDER_MODULES = ["jobbank.spiders"]
NEWSPIDER_MODULE = "jobbank.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "jobbank (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "jobbank.middlewares.JobbankSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "jobbank.middlewares.JobbankDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "jobbank.pipelines.JobbankPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 3

# The maximum number of concurrent requests per domain (default: 8)
CONCURRENT_REQUESTS_PER_DOMAIN = 16

# The maximum number of concurrent requests per IP (default: 0)
CONCURRENT_REQUESTS_PER_IP = 16

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800,
}

# Enable or disable extensions
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'jobbank.pipelines.JobbankPipeline': 1,
}

# Specify the path to the Chrome driver executable
CHROME_DRIVER_PATH = r"C:\Users\aouad\OneDrive\Bureau\stage_ine2\projet_emplois\backend\app\data_collection\jobbank\chromedriver.exe"

# Specify the path to the Chrome binary executable
CHROME_BINARY_LOCATION = r"C:\Users\aouad\OneDrive\Bureau\stage_ine2\projet_emplois\backend\app\data_collection\jobbank\chrome-win64\chrome.exe"

# MongoDB Connection Settings
MONGO_URI = 'mongodb://localhost:27017/'  # Update if your MongoDB is on a different host/port
MONGO_DATABASE = '2JOBS'  # The name of your MongoDB database
MONGO_COLLECTION = 'Jobs'  


# jobbank/settings.py

BOT_NAME = 'jobbank'

SPIDER_MODULES = ['jobbank.spiders']
NEWSPIDER_MODULE = 'jobbank.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 3

# Enable or disable extensions
EXTENSIONS = {
    'scrapy.extensions.closespider.CloseSpider': 1,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'jobbank.pipelines.JobbankPipeline': 300,
}
