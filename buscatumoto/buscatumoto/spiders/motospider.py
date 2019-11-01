#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy
import pprint

from pprint import pprint

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
			#print ("brand is %s" % brand.extract().strip())

			if brand.extract().strip() == "–Marca–":
				pass
			elif brand.extract().strip() == "Honda":
					item = BuscatumotoItem()
					item['brand'] = brand.extract().strip()

					urlBrand =  "https://www.motorbikemag.es/motos-marcas-modelos/?marca=%s" % (item['brand'])

					#print ("Trying to visit url %s" % urlBrand)		
					#print (brand.extract().strip())

					yield scrapy.Request(urlBrand, callback=self.parse_brand)

			#for each urlBrand, paginate obtaint url of each item and paginat
			#fetch("urlBrand")

		  #  catalog_item = Selector(response)


	def parse_brand(self, response):
		print ("Visited %s", response.url)

		next_pages_urls = Selector(response).xpath("//div[@class='pagination']/a[not(@class='next page-numbers')]/@href").extract()

		next_page_array = []

		first_page = response.url

		next_pages_urls.insert(0, first_page)

	#	next_page_array.append(next_pages_urls.extract())

		#print ("next page urls %s", next_pages_urls)


		pages_length = len(next_pages_urls)

		for num, next_page in enumerate(next_pages_urls):
			#print("Next page is %s and %d" % (next_page, num))
			absolute_next_page_url = response.urljoin(next_page)
			#print ("Absolute url is: %s" % absolute_next_page_url)
			priority_req = pages_length - num
			#print ("Priority is %d" % priority_req)
			yield scrapy.Request(absolute_next_page_url, callback = self.parse_item_catalog, priority = priority_req, dont_filter = True)


	def parse_item_catalog(self, response):
		#print ("Visited page %s" % response.url)

		items_url_catalog = Selector(response).xpath("//div[@class='thumb']//a/@href").extract()

		#print (items_url_catalog)

		for item_url_catalog in items_url_catalog:
			print (item_url_catalog)
			if item_url_catalog == 'https://www.motorbikemag.es/ficha-tecnica/honda-gl1800-gold-wing-2020/':
				yield scrapy.Request(item_url_catalog, callback = self.parse_moto_detalle, dont_filter = True)


	def parse_moto_detalle(self, response):

		print ("Visited moto page %s" % response.url)

				#tabla todo:
		#specs_sel = Selector(response).xpath("//div[@id='div-ficha-tecnica']//tr//td//text()")

	

		print("Response url is %s" %response.url)

		if response.url == 'https://www.motorbikemag.es/ficha-tecnica/honda-gl1800-gold-wing-2020/':

			specs_sel = Selector(response).xpath("//*[@id='div-ficha-tecnica']/div/table//tr/td[2]")
			print("Length of selector is %d" % len(specs_sel))

			#specs_sel_test = Selector(response).xpath("//*[@id='div-ficha-tecnica']/div/table//tr[25]/td[1]//text()").extract()
			specs_sel_test = Selector(response).xpath("//*[@id='div-ficha-tecnica']/div/table//tr[%d]/td[1]//text()" % 25).extract()
			pprint (specs_sel_test)

			specs_sel_test = Selector(response).xpath("//*[@id='div-ficha-tecnica']/div/table//tr[25]/td[2]//text()").extract()
			pprint (specs_sel_test)

			specs_sel_test = Selector(response).xpath("//*[@id='div-ficha-tecnica']/div/table//tr[31]/td[1]//text()").extract()
			pprint (specs_sel_test)

			specs_sel_test = Selector(response).xpath("//*[@id='div-ficha-tecnica']/div/table//tr[31]/td[2]//text()").extract()
			pprint (specs_sel_test)

			pprint("selector value is %s" % specs_sel)
			for index, tablerow in enumerate(specs_sel):
				pprint (tablerow)
				print("Index is %s" % index)
				#print("tablerow value is %s" % tablerow.xpath('text()').extract_first()) -> OK +-
				array = tablerow.xpath('text()').extract()
				print("Length of array is %d" % len(array))


				for val_array in array:
					print("array value is %s" % val_array)


				#print("tablerow value is %s" % )

				#tr = specs_sel.xpath('/tr[' + str(index) + ']')
				#td = tablerow.xpath('/td[1]')
				#print("Length of td1 is %d" % len(td))
				#print("Td value is %s" % td)

		

			#args = (index, specs_sel.xpath('td[2]').extract_first())
			#rint ('Table row %d value is %s' % args)
			#	for td in tablerow.xpath('//td'):
			#		print(td)
		else:
			print("NO GOLDWING")
				#for indextd, tdvalue in td:
				#	if indextd == 0:
				#		td1_array.append(tdvalue)
				#	if indextd == 1:
				#		td2_array.append(tdvalue)
			






		#foto principal
		picture_banner = response.xpath("//div[@id='imgPrincipal']//img/@src").extract()

		#entradilla
		highlight = response.xpath("//div[@class='entry-highlights']//text()").extract()
		print ("Higlight of moto detail is %s" % highlight)

		#precio
		precio_title = response.xpath("//div[@id='precio']/div[@class='info-precio']/h2").extract()
		print("Price of bike is %s" % precio_title)
		precio_desc = response.xpath("//div[@class='com-precio graybox']/div[@id='precio']/p").extract()

		#body
		main_desc = response.xpath("//div[@id='container']//div[@class='entry-content']//div[@class='post-banner banner-left']/following-sibling::p//text()").extract

		#permisos
		permit_title = response.xpath("//div[@id='carnets']").extract()
		permit_list = response.xpath("//div[@class='iconos']//div[@class='icon-carnet visible']//text()").extract()

		#especificaciones
		specs_title = response.xpath("//div[@id='ficha']/div[@class='cat-title']/h2/span").extract()



		#likewise motos
		likewise_list_name = response.xpath("//div[@class='moto-list']").extract()
		likewise_list_url = response.xpath("//div[@class='moto-list']/a/@href").extract()





















			