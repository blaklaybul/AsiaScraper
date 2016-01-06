from sqlalchemy.orm import sessionmaker
from models import StartupUrls, db_connect, create_startupUrls_table

class TechInAsiaPipeline(object):

    def __init__(self):

        engine = db_connect()
        create_startupUrls_table(engine)
        self.Session = sessionmaker(bind=engine)

    def proess_item(self, item, spider):
        """saves the url"""

        session = self.Session()
        url = StartupUrls(**item)

        try:
            session.add(url)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item
