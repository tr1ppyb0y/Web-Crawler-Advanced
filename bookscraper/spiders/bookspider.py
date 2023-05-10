import re
from string import punctuation

import scrapy
from bookscraper.items import BookItem


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css('article.product_pod')

        for book in books:
            detail = response.urljoin(book.css('h3 a').attrib['href'])
            yield response.follow(detail, callback=self.parse_detail)
        
        next_page = response.css("li.next a ::attr(href)").get()
        if next_page:
            url = response.urljoin(next_page)
            yield response.follow(url, callback=self.parse)

    def parse_detail(self, response):
        book = BookItem(
            **{
                "url": response.url,
                "category" : response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
                "title" : response.css(".product_main h1::text").get(),
                "price" : response.css(".product_main .price_color::text").get(),
                "ratings" : response.css(".product_main .star-rating").attrib["class"].split()[1].lower(),
                "description" : response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
                # This is for CSV file in case of outputting json file, re.sub('**', 'information: ')
                **{
                    re.sub(r'['+punctuation+']', '', row.css('th::text').get()).lower().replace(' ', '_'):row.css('td::text').get() 
                    for row in response.css("table tr")
                }
            }
        )
        return book
