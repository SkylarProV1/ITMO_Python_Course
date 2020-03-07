from bottle import (
    route, run, template, request, redirect
)
import string
from scraputils import get_news
from db import News, session
from bayes import NaiveBayesClassifier

@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)
#http://localhost:8000/news
@route("/add_label/")
def add_label():
    s = session()
    #Получаем значения парамтеров lable и id из GET запросаx
#    mark = request.data.get("label")
    mark=str(request).split('label=')[1].split('&')[0]
    id=str(request).split('id=')[1].split('>')[0]
    #Получить запись из бд по полученному id
    post=s.query(News).get(int(id))
    print(post)
    #заносим в Sqlite
    post.label=mark
    s.commit()
    redirect("/news")

#http://localhost:8000/news
@route("/update")
def update_news():
    # Получение данных
    s=session()
    url='https://news.ycombinator.com/newest'
    page=5
    data=get_news(url,page)
    base=s.query(News).all()
    count2=0
    for post in data:
        count=0
        news = News(title=post.get('title'),
            author=post.get('author'),
            url=post.get('url'),
            comments=post.get('comments'),
            points=post.get('points'))
        for row in base:
            if row.author == post.get('author') and row.title == post.get('title'):
                count+=1
        if count == 0:
            count2+=1
            print("{} Add new post".format(count2))
            s.add(news)
            s.commit()
    redirect("/news")

def clean(s):
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator)

def test():
    s=session()
    learn = s.query(News).filter(News.label != None).all()
    X,y=[],[]
    for sent in learn:
        X.append(sent.title)
        y.append(sent.label)
    X = [clean(x).lower() for x in X]
    model=NaiveBayesClassifier()
    X_train,y_train=X,y
    model.fit(X_train, y_train)
    treatment=s.query(News).filter(News.label == None).all()
    data=[]
    for row in treatment:
        data.append(row.title)
    classify=model.predict(data)
    print(sorted(classify))

@route("/classify")
def classify_news():
    s=session()
    learn = s.query(News).filter(News.label != None).all()
    X,y=[],[]
    for sent in learn:
        X.append(sent.title)
        y.append(sent.label)
    X = [clean(x).lower() for x in X]
    model=NaiveBayesClassifier()
    X_train,y_train=X,y
    model.fit(X_train, y_train)
    treatment=s.query(News).filter(News.label == None).all()
    data=[]
    apdata=[]
    
    for row in treatment:
        data.append(row.title)
        val=row.url,row.author,row.points,row.comments
        apdata.append(val)
    classify=model.predict(data)
    
    for i in range(len(classify)):
        val=classify[i][2],classify[i][1]
        apdata[i]=val+apdata[i]
    j=0
    for i in range(len(apdata)):
        if classify[i][1]=='good':
            treatment[j].title=apdata[i][0]
            treatment[j].url=apdata[i][2]
            treatment[j].author=apdata[i][3]
            treatment[j].points=apdata[i][4]
            treatment[j].comments=apdata[i][5]
            j+=1
    for i in range(len(apdata)):
        if classify[i][1]=='maybe':
            treatment[j].title=apdata[i][0]
            treatment[j].url=apdata[i][2]
            treatment[j].author=apdata[i][3]
            treatment[j].points=apdata[i][4]
            treatment[j].comments=apdata[i][5]
            j+=1
    for i in range(len(apdata)):
        if classify[i][1]=='never':
            treatment[j].title=apdata[i][0]
            treatment[j].url=apdata[i][2]
            treatment[j].author=apdata[i][3]
            treatment[j].points=apdata[i][4]
            treatment[j].comments=apdata[i][5]
            j+=1
    return template('news_template', rows=treatment)
    
if __name__ == "__main__":
    run(host="localhost", port=8000)
#The Use of Knowledge in Society
#http://localhost:8000/classify
