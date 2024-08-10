from scrapy import signals
from itemadapter import is_item


class JobbankSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        # Initialize the middleware and connect to spider_opened signal
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider middleware and into the spider
        spider.logger.debug(f"Processing spider input: {response.url}")
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after it has processed the response
        spider.logger.debug(f"Processing spider output: {response.url}")
        for i in result:
            if is_item(i):
                spider.logger.debug(f"Yielding item: {i}")
            else:
                spider.logger.debug(f"Yielding request: {i}")
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method raises an exception
        spider.logger.error(f"Spider exception: {exception}")
        return None

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider
        for r in start_requests:
            spider.logger.debug(f"Processing start request: {r.url}")
            yield r

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


class JobbankDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        # Initialize the middleware and connect to spider_opened signal
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader middleware
        spider.logger.debug(f"Processing request: {request.url}")
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader
        spider.logger.debug(f"Processing response: {response.url}")
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or process_request() method raises an exception
        spider.logger.error(f"Downloader exception for request {
                            request.url}: {exception}")
        return None

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")
