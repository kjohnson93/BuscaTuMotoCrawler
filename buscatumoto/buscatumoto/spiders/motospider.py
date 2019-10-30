#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.selector import Selector

from buscatumoto.items import BuscatumotoItem


class MotospiderSpider(Spider):

	name = 'motospider'
	allowed_domains = \
		['motorbikemag.es']
	start_urls = ['https://www.motorbikemag.es/motos-marcas-modelos//']

	def parse(self, response):
		brands = \
			Selector(response).xpath("//select[@name='marca']//text()")

		for brand in brands:
			print ("brand is %s", brand.extract().strip())

			if brand.extract().strip() == "–Marca–":
				pass
			elif brand.extract().strip() == "Honda":
					item = BuscatumotoItem()
					item['brand'] = brand.extract().strip()

					urlBrand =  "https://www.motorbikemag.es/motos-marcas-modelos/?marca=%s" % (item['brand'])

					print ("Trying to visit url %s", urlBrand)		
					print (brand.extract().strip())

					yield scrapy.Request(urlBrand, callback=self.parse_brand)

			#for each urlBrand, paginate obtaint url of each item and paginat
			#fetch("urlBrand")

		  #  catalog_item = Selector(response)


	def parse_brand(self, response):
		print ("Visited %s", response.url)


		next_pages_urls = Selector(response).xpath("//div[@class='pagination']/a[not(@class='next page-numbers')]/@href")


		for next_page in next_pages_urls:
			print(next_page.extract())
			absolute_next_page_url = response.urljoin(next_page.extract())
			print ("Absolute url is: %s", absolute_next_page_url)
			yield scrapy.Request(absolute_next_page_url, callback = self.parse_item_catalog)


	def parse_item_catalog(self, response):
		print ("Visited page %s", response.url)

		items_url_catalog = Selector(response).xpath("//div[@class='thumb']//a/@href")

		for item_url_catalog in items_url_catalog:
			print (item_url_catalog.extract())














			