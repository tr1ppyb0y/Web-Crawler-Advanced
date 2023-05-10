# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re

class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Stripping whitespaces.
        description = adapter.pop('description')
        for val in adapter:
            adapter[val] = adapter[val].strip()
        adapter['description'] = description
        
        # Converting ratings into integers.
        ratings = {
            'zero': 0,
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5
        }
        adapter['ratings'] = ratings[adapter['ratings']]

        # Lower casing Category & Product type.
        adapter['category'] = adapter['category'].lower()
        adapter['product_type'] = adapter['product_type'].lower()

        # Prices to integer.
        price_key = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for key in price_key:
            adapter[key] = float(adapter[key].replace('£', ''))
        
        # Extracting count from availability string.
        adapter['availability'] = [int(avail) for avail in re.findall(r'\d+', adapter['availability']) or [0]][0]

        # Type casting # of reviews to int.
        adapter['number_of_reviews'] = int(adapter.get('number_of_reviews', 0))

        return item