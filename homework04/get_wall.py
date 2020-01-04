import requests
import time 
import textwrap

code ="""var i=0;
var mass={};
var count1=0;
var i=0;
while(i<25) {
var posts=API.wall.get({
    "owner_id": "",
    "domain": "wf_overheard",
    "offset": i*100,
    "count": 100,
    "filter": "owner",
    "extended": 0,
    "fields": "",
    "v": "5.103"
    });
mass.push(posts);
if (posts.count-count1*100<100){
    return mass;
};
count1=count1+1;
i=i+1;
};
return mass;
"""

response = requests.post(
url="https://api.vk.com/method/execute",
data={
    "code": code,
    "access_token": '2efc4ae10d033205dee7fa701d394005feaa859a11341c7646fa9cf7a45c7151c0e553090f51f5e0c2de6',
    "v": "5.103"
    }
    )
maxit=response.json().get('response')[0].get('count')
res=''
information=list()
res=response.json().get('response')
er=0
if maxit>100:
    maxit2=100
    if maxit>2500:
        maxit1=25
    elif maxit%100==0:
        maxit1=maxit//100
        er=1
    else:
        maxit1=maxit//100+1
else:
    maxit2=maxit
    maxit1=1
for i in range(maxit1):
    if er!=1 and i==maxit1-1:
        maxit2=maxit%100
    for j in range(maxit2):
        if res[i].get('items')[j].get('text').lower()!='':
            information.append(res[i].get('items')[j].get('text').lower())