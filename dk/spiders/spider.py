import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import DkItem
from itemloaders.processors import TakeFirst
import json

pattern = r'(\xa0)?'
base = 'https://www.almbrand.dk/api/v1/news/search?id=65020&page={}'
class DkSpider(scrapy.Spider):
	name = 'dk'
	start_urls = ['https://www.almbrand.dk/api/v1/news/search?id=65020&page=1']

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['newsItems'])):
			for i in range(len(data['newsItems'][index])):
				link = data['newsItems'][index][i]['url']
				yield response.follow(link, self.parse_post)
		for index in data['pages']:
			yield response.follow(base.format(index), self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="grid-2-3 manchet centercontent datestyle"]/p/span[last()]/text()').get()
		date = re.findall(r'\w+\s\d+\,\s\d+', date)
		title = response.xpath('(//h3)[last()]/text()').get()
		content = response.xpath('//div[@class="grid-2-3 centercontent"][position()>2]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=DkItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
