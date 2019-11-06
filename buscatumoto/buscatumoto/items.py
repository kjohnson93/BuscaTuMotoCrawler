# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class BuscatumotoItem(Item):

	brand = Field()
	model = Field()
	imgThumbUrl = Field()
	modelHighlights = Field()

	imgBannerUrl = Field()
	modelDetailtHighlights = Field()
	priceTitle = Field()
	priceDesc = Field()
	mainDesc = Field()
	licenses = Field() 
	licenses_title = Field()
	specs_title = Field() 
	specs_table = Field()
	relatedItems = Field() 
	relatedItemsUrl = Field() 