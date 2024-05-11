from typing import Any
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Response
import re
import scrapy.spiders
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

class ScrapEmailsSpider(scrapy.Spider):

    name = 'ScrapEmailsSpider'
    
    search_url = ''
    start_urls = [
        f"https://www.google.com/search?q=''"
    ]

    def __init__(self, query=None, name = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.search_url = f"https://www.google.com/search?q={query}"
        self.rules = [scrapy.spiders.Rule(LinkExtractor(), callback='parse_website', follow=True)]
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)

    def get_base_url(self, url):
        parts = url.split('/')
        substring = '/'.join(parts[:3])
        return substring
      
    
    def parse(self, response: Response, **kwargs: Any) -> Any:
        self.driver.get(self.search_url)

        previous_height = self.driver.execute_script('return document.body.scrollHeight')
        while True :
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')  
            sleep(2)
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            urls = []
            for link in links:
                link = link.get_attribute("href")
                if link:
                    if not (link.__contains__('google') or link.__contains__('linkedin')):
                        
                        urls.append(self.get_base_url(link))
            
            for url in list(set(urls)):
                yield scrapy.Request(url, callback=self.parse_website)
             
            new_height = self.driver.execute_script('return document.body.scrollHeight')
            if new_height == previous_height:
                break
            previous_height = new_height
  
        
    def parse_website(self, response):
        social_media_links = self.extract_social_media_links(response)
        support_email = self.extract_support_email(response)
        if not (support_email or response.url.__contains__('contact')):
            contact_url = ''
            if response.url.endswith('/'):
                contact_url = f'{response.url}contact'
            else:
                contact_url = f'{response.url}/contact'
            
            yield scrapy.Request(contact_url, self.parse_website)

        yield {
            'url': response.url,
            'facebook': social_media_links[0],
            'twitter': social_media_links[1],
            'linkedin': social_media_links[2],
            'support_email': support_email
        }


    def extract_social_media_links(self, response):
    
        social_media_fb = response.css('a[href*="facebook.com/"]::attr("href")').extract_first()
        social_media_tw = response.css('a[href*="twitter.com/"]::attr("href")').extract_first()
        social_media_in = response.css('a[href*="linkedin.com/"]::attr("href")').extract_first()
        return [social_media_fb, social_media_tw, social_media_in]


    def extract_support_email(self, response: Response):

        email = response.css('a[href*="mailto:"]::attr(href)').extract_first()
        if email:
            return email.split(':')[1]
            
        elif email is None :
        
            text_content = response.text
            email_pattern = r'\b[A-Za-z]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails_list = re.findall(email_pattern, text_content)
            emails = []
            for text in emails_list:
                if not (text.__contains__('.webp') or text.__contains__('.jpg')):
                    emails.append(text.strip())
            print('emails:', emails)
            return ','.join(list(set(emails)))
       