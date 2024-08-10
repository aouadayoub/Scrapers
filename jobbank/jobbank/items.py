import scrapy
from urllib.parse import urlparse, urlunparse


class JobbankItem(scrapy.Item):
    title = scrapy.Field() 
    date = scrapy.Field()  
    business = scrapy.Field()  
    location = scrapy.Field()  
    salary = scrapy.Field()  
    job_link = scrapy.Field(serializer=lambda value: urlunparse(urlparse(
        # The link to the job listing
        value)) if isinstance(value, str) else value)
    logo = scrapy.Field()  
    source = scrapy.Field()  
    country = scrapy.Field()  
