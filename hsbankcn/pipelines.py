from itemadapter import ItemAdapter
import sqlite3


class DatabasePipeline:
    # Database setup
    conn = sqlite3.connect('hsbankcn.db')
    c = conn.cursor()

    def open_spider(self, spider):
        # c.execute(""" DROP TABLE IF EXISTS articles """)

        self.c.execute(""" CREATE TABLE IF NOT EXISTS articles (
        title text, 
        date text,
        link text, 
        content text
        ) """)

    def process_item(self, item, spider):
        # Insert values
        self.c.execute("SELECT * FROM articles WHERE link = ?", (item.get('link'),))
        duplicate = self.c.fetchone()
        if duplicate:
            self.c.execute("UPDATE articles SET title = ?, date = ?, content = ? WHERE link = ?",
                           (item.get('title'),
                            item.get('date'),
                            item.get('content'),
                            item.get('link')))

            print(f"Updated article: {item['link']}")

        else:
            self.c.execute("INSERT INTO articles ("
                           "title, "
                           "date, "
                           "link, "
                           "content)"
                           " VALUES (?,?,?,?)",
                           (item.get('title'),
                            item.get('date'),
                            item.get('link'),
                            item.get('content')
                            ))

            print(f"New article: {item['link']}")

        self.conn.commit()  # commit after every entry

        return item

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()
