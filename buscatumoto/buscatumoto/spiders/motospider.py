# -*- coding: utf-8 -*-
import scrapy


class MotospiderSpider(scrapy.Spider):
    name = 'motospider'
    allowed_domains = ['https://www.motorbikemag.es/motos-marcas-modelos/']
    start_urls = ['http://https://www.motorbikemag.es/motos-marcas-modelos//']

    def parse(self, response):
        pass
