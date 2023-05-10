# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
from mysql import connector

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
            'zero': 0, 'one': 1,
            'two': 2, 'three': 3,
            'four': 4, 'five': 5
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

class SaveToMySQLPipeline:
    
    def __init__(self) -> None:
        self.conn = connector.connect(
            host='localhost',
            user='root',
            password='',
            database='books'
        )

        # Create cursor.
        self.cur = self.conn.cursor()

        # Create Book table if not exists.
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS books(
                id int NOT NULL auto_increment,
                url VARCHAR(255), title text,
                upc VARCHAR(255), product_type VARCHAR(255),
                price DECIMAL, price_excl_tax DECIMAL,
                price_incl_tax DECIMAL, tax DECIMAL,
                availability INTEGER,
                number_of_reviews INTEGER,
                category VARCHAR(255), ratings INTEGER,
                description text, PRIMARY KEY (id)
            )
            """
        )
    
    def process_item(self, item, spider):

        # Define Insert statement.
        self.cur.execute(
            """
            INSERT INTO books(
                url, title, upc, product_type,
                price_excl_tax, price_incl_tax,
                tax, price, availability, number_of_reviews,
                ratings, category, description
            ) values(
                %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s
            )
            """, (
                item['url'], item['title'], item['upc'],
                item['product_type'], item['price_excl_tax'],
                item['price_incl_tax'], item['tax'], item['price'],
                item['availability'], item['number_of_reviews'],
                item['ratings'], item['category'], item['description']
            )
        )
        self.conn.commit()
        return item
    
    def close_spider(self, spider):

        # Close database connection.
        self.cur.close()
        self.conn.close()