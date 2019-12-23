#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy
import pprint
import re

from pprint import pprint

from scrapy import Spider
from scrapy.selector import Selector

from buscatumoto.items import BuscatumotoItem


class MotospiderSpider(Spider):

	name = 'motospider'
	allowed_domains = \
		['motorbikemag.es']
	start_urls = ['https://www.motorbikemag.es/motos-marcas-modelos//']

	item = BuscatumotoItem()
	item_brand = ''
	item_model = ''
	item_imgThumbUrl = ''
	item_modelHighLights = ''


	def parse(self, response):
		bikeTypes = Selector(response).xpath("//select[@id='f_tipo']//text()")

		for bikeType in bikeTypes:
			if bikeType.extract().strip() == "–Tipo de moto–":
				pass
			else:
				bikeTypeStrip = bikeType.extract().replace('-','').strip()
				bikeTypeFormatted = bikeTypeStrip.replace(' ', '-')
				item_bikeType = bikeTypeFormatted.strip()
				urlBikeType =  "https://www.motorbikemag.es/motos-marcas-modelos/?tipo=%s" % item_bikeType
			#	print ("Trying to visit url %s" % urlBikeType)		

				yield scrapy.Request(urlBikeType, callback=self.parse_biketype, meta = {'item_bikeType': item_bikeType})
			#if bikeType.extract().strip() == "- Retro":
			#	bikeTypeStrip = bikeType.extract().replace('-','').strip()
			#	bikeTypeFormatted = bikeTypeStrip.replace(' ', '-')
			#	item_bikeType = bikeTypeFormatted.strip()
			#	urlBikeType =  "https://www.motorbikemag.es/motos-marcas-modelos/?tipo=%s" % item_bikeType
			#	print ("Trying to visit url %s" % urlBikeType)		

			#	yield scrapy.Request(urlBikeType, callback=self.parse_biketype, meta = {'item_bikeType': item_bikeType})


	def parse_biketype(self, response):
		print ("Visited parse_biketypee %s", response.url)
		item_bikeType = response.meta.get('item_bikeType')

		next_pages_urls = Selector(response).xpath("//div[@class='pagination']/a[not(@class='next page-numbers')]/@href").extract()
		next_page_array = []
		first_page = response.url
		next_pages_urls.insert(0, first_page)
		pages_length = len(next_pages_urls)

		for num, next_page in enumerate(next_pages_urls):
			#print("Next page is %s and %d" % (next_page, num))
			absolute_next_page_url = response.urljoin(next_page)
			#print ("Absolute url is: %s" % absolute_next_page_url)
			priority_req = pages_length - num
			#print ("Priority is %d" % priority_req)
			yield scrapy.Request(absolute_next_page_url, callback = self.parse_item_catalog, priority = priority_req, dont_filter = True, meta = {'item_bikeType': item_bikeType})


	def parse_item_catalog(self, response):
		print ("Visited page item catalog %s" % response.url)
		item_bikeType = response.meta.get('item_bikeType')

		#todo cambiar procesado de este motodo. En lugar de obtener solo URL, obtener info de modelo, thumbnail y highlight Y URL para enviar al pipeline.
		items_url_catalog = Selector(response).xpath("//div[@class='thumb']//a/@href").extract()
		page_models = Selector(response).xpath("//div[@class='archive-postlist']//strong//text()").extract()
		page_imgThumbUrls = Selector(response).xpath("//div[@class='archive-postlist']//div[@class='thumb']//a//img/@data-lazy-src").extract()
		page_highlights = Selector(response).xpath("//div[@class='archive-postlist']//div[@class='entry-meta']//text()").extract()

		#for each item in catalog
		for index, item_url_catalog in enumerate(items_url_catalog):
			item_model = page_models[index]
			item_imgThumbUrl = page_imgThumbUrls[index]
			item_modelHighLights = page_highlights[index]

			yield scrapy.Request(item_url_catalog, callback = self.parse_moto_detalle, dont_filter = True, meta = {'item_bikeType': item_bikeType,'item_model': item_model,
				'item_imgThumbUrl': item_imgThumbUrl, 'item_modelHighLights': item_modelHighLights})


	#this method crawls a detailed web page of a bike in the web's page catalogue.
	def parse_moto_detalle(self, response):

		print ("Visited moto page %s" % response.url)

		item_bikeType = response.meta.get('item_bikeType')
		item_model = response.meta.get('item_model')
		item_imgThumbUrl = response.meta.get('item_imgThumbUrl')
		item_modelHighLights = response.meta.get('item_modelHighLights')

		#regexp
		regexp = "src=\"(.+?)\""
		#pprint("Regexp chain is %s" % regexp)
		item_picture_banner_div = response.xpath("//div[@id='imgPrincipal']").extract()
		item_imgBannerUrl = re.search(regexp, item_picture_banner_div[0])
		item_imgBannerUrl = item_imgBannerUrl.group(1)


		#print ("Higlight of moto detail is %s" % highlight)

		#precio
		item_precio_title = response.xpath("//div[@id='precio']/div[@class='info-precio']/h2//text()").extract_first()
		#Grabbing selector value from crawler because it contains additional info that can get interpreted later on like urls, etc.
		item_precio_desc = response.xpath("//div[@class='com-precio graybox']/div[@id='precio']//p").extract()
		#item_precio_desc = response.xpath("//div[@class='com-precio graybox']/div[@id='precio']//p//text()").extract()


		#body
		item_main_desc = response.xpath("//div[@id='container']//div[@class='entry-content']//div[@class='post-banner banner-left']/following-sibling::p").extract()

		#permisos
		item_licenses_title = response.xpath("//div[@id='carnets']//text()").extract_first()
		item_licenses = response.xpath("//div[@class='iconos']//div[@class='icon-carnet visible']//text()").extract()

		#especificaciones
		item_specs_title = response.xpath("//div[@id='ficha']/div[@class='cat-title']/h2/span//text()").extract_first()

		#This block of code tries to crawl a n-colum table in order to store it inside an array of arrays

		table_number_of_rows = Selector(response).xpath("//*[@id='div-ficha-tecnica']/div/table//tr")
		#pprint ("Rows of table: %d" % len(table_number_of_rows))

		table_number_of_colums = Selector(response).xpath("//*[@id='div-ficha-tecnica']/div/table/tbody/tr[1]//td")
		#print ("Colums of table: %d" % len(table_number_of_colums))
		item_spec_table = []

		for column in range(1,len(table_number_of_colums)+1):
			pprint (column)
			td_array = []
			for index in range(1,len(table_number_of_rows)):
				item_spec_table_temp = Selector(response).xpath("//*[@id='div-ficha-tecnica']/div/table//tr[%d]/td[%d]//text()" % (index,column)).extract()
				td_array.append(" ".join(item_spec_table_temp))
			item_spec_table.append(td_array)
			pprint("Colum of table is %d and length of tdarray is: %d" % (column,len(item_spec_table[column-1])))

		#likewise motos
		item_relatedItems = response.xpath("//div[@class='moto-list']//text()").extract()
		item_relatedItemsUrl = response.xpath("//div[@class='moto-list']/a/@href").extract()


		############ NEW FIELDS (brand, price, power, displacement, seat height, weight)

		highlight = response.xpath("//div[@class='entry-highlights']/text()").extract()


		#brand
		item_brand = response.xpath("//div[@class='entry-meta nav-meta']/a[3]/text()").extract_first()
		#price
		price_regex = '(?<=precio: )(.*)(?=€)'
		price_result = re.search(price_regex, highlight[1], re.IGNORECASE)

		if price_result:
			item_price = price_result.group(0)
			#print("Item price after regex is %s" % item_price)
		else:
			#print("No regex match, should assign N.D value")
			item_price = 'N.D.'

		#POWER
		power_regex = '(?<=Potencia: )(.*)(?= cv)'
		power_result = re.search(power_regex, highlight[1], re.IGNORECASE)

		if power_result:
			item_power = power_result.group(0)
			#print("Item power is %s" % item_power)
		else:
			#print("No regex match, should assign N.D. value")
			item_power = 'N.D.'

		#displacement
		displacement_regex = '(?<=Cilindrada: )(.*)(?= cc)'
		displacement_result = re.search(displacement_regex, highlight[1], re.IGNORECASE)

		if displacement_result:
			item_displacement = displacement_result.group(0)
			#print("Item displacement is %s" % item_displacement)
		else:
			#print("No regex match, should assign N.D. value")
			item_displacement = 'N.D.'

		#weight
		weight_regex = '(?<=Peso: )(.*)(?= kg)'
		weight_result = re.search(weight_regex, highlight[1], re.IGNORECASE)

		if weight_result:
			item_weight = weight_result.group(0)
			#print("Item weight is %s" % item_weight)
		else:
			#print("No regex match, should assign N.D. value")
			item_weight = 'N.D.'

		############ NEW FIELS (brand, price, power, displacement, seat height, weight)

		#Sending items to pipeline

		#print("Item bike type is %s" % item_bikeType)
		#print("Item highlight is %s" % highlight)	
		#print("Item price is %s" % item_price)
		#print("Item brand is %s" % item_brand)
		#print( "Item model is %s" % item_model)
		#print("Item imgThumbUrl is %s" % item_imgThumbUrl)
		#print("Item modelHighlights are %s" % item_modelHighLights)

		#print("Item picture banner is %s" % item_imgBannerUrl)
		#print("Item precio title is %s" % item_precio_title)
		#print("Item precio desc is %s" % item_precio_desc)
		#print("Item main desc is %s" % item_main_desc)
		#print("Item licenses title is %s" % item_licenses_title)
		#print("Item licenses list is %s" % item_licenses)
		#print("Item specs title is %s" % item_specs_title)
		#print("Item specs table: %s" % item_spec_table)
		#print("Item related items are %s" % item_relatedItems)
		#print("Item related items url are %s" % item_relatedItemsUrl) 

		item = BuscatumotoItem()

		item['bikeType'] = item_bikeType
		item['brand'] = item_brand #plain text formatted
		item['model'] = item_model #plain text formatted	
		item['price'] = item_price
		item['power'] = item_power
		item['displacement'] = item_displacement
		item['weight'] = item_weight

		item['imgThumbUrl'] = item_imgThumbUrl #url text formatted?
		item['modelHighlights'] = item_modelHighLights #array
		item['imgBannerUrl'] = item_imgBannerUrl #url text formatted?
		item['modelDetailtHighlights'] = highlight #array
		item['priceTitle'] = item_precio_title #plain text formatted
		item['priceDesc'] = item_precio_desc #plain text NO formatted
		item['mainDesc'] = item_main_desc #plain text NO formatted
		item['licenses'] = item_licenses #array
		item['licenses_title'] = item_licenses_title #plain text formatted
		item['specs_title'] = item_specs_title #plain text formatted
		item['specs_table'] = item_spec_table #array of arrays (matrix)
		item['relatedItems'] = item_relatedItems #array  
		item['relatedItemsUrl'] = item_relatedItemsUrl #array

		yield item
	
























