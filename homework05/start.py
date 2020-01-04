import requests
import config
from bs4 import BeautifulSoup
response = requests.get('http://www.ifmo.ru/ru/schedule/raspisanie_zanyatiy.htm')
web_page = response.text
soup = BeautifulSoup(web_page, "html5lib")

schedule_table = soup.find("div", attrs=dict(id = "content"))
schedule_table=schedule_table.findAll("div", attrs={"class":"groups"})

list1=str(schedule_table)
helps=list1.split('.htm">')

End_list= list()
for i in range(0,len(helps)-1):
	ls=helps[i].split('zanyatiy_')
	End_list.append(ls[1].lower())

Full_group={a:[['' for i in range(5)]  for j in range(22)] for a in End_list}

for i in End_list:
	Full_group[i][0][0]=i