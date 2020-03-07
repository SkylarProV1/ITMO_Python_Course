from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scraputils import get_news

Base = declarative_base()
engine = create_engine("sqlite:///news.db")
session = sessionmaker(bind=engine)


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)

Base.metadata.create_all(bind=engine)

if __name__=='__main__':
    s = session()
    url='https://news.ycombinator.com/newest'
    n_pages=int(input('Enter the number of pages: '))
    data=get_news(url,n_pages)
    for post in data:
        news = News(title=post.get('title'),
            author=post.get('author'),
            url=post.get('url'),
            comments=post.get('comments'),
            points=post.get('points'))
        s.add(news)
        s.commit()
