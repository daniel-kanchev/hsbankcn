import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from hsbankcn.items import Article
from scrapy.http import FormRequest


class hsbankcnSpider(scrapy.Spider):
    name = 'hsbankcn'
    start_urls = ['http://www.hsbank.com.cn/Channel/312347?_tp_t1207473816328=1']
    page = 1

    def parse(self, response):
        links = response.xpath('//td[@class="huikuang"]//a[@target="_blank"]/@href').getall()
        if links:
            yield from response.follow_all(links, self.parse_article)

            self.page += 1

            next_page = f'http://www.hsbank.com.cn/Channel/312347?_tp_t1207473816328={self.page}'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        title = response.xpath('//printinfo/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('(//printinfo)[last()]/text()').get()
        if date:
            date = " ".join(date.split())

        iframe_link = response.urljoin(response.xpath('//iframe/@src').get())
        yield response.follow(iframe_link, self.parse_iframe, cb_kwargs=dict(title=title, date=date,
                                                                             link=response.url))

    def parse_iframe(self, response, title, date, link):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        content = response.xpath('//body//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', link)
        item.add_value('content', content)

        return item.load_item()
