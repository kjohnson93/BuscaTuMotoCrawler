from scrapy import Spider
from scrapy.selector import Selector

from buscatumoto.items import BuscatumotoItem


class MotospiderSpider(Spider):
    name = 'motospider'
    allowed_domains = ['https://www.motorbikemag.es/motos-marcas-modelos/']
    start_urls = ['https://www.motorbikemag.es/motos-marcas-modelos//']

    def parse(self, response):
        brands = Selector(response).xpath("//select[@name='marca']//text()")

        for brand in brands:
        	print(brand)
