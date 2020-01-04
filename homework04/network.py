from api import get_friends
from api import get_req
from igraph import Graph, plot
import numpy as np
import igraph
import config
import time


def get_network(users_ids, as_edgelist=True):

	users={str(user):'' for user in users_ids}
	#связи друзей
	for friends in users_ids:
		friendslist=get_friends(int(friends),'')
		try:
			friendslist=friendslist.get('response')['items']
		except TypeError: 
			# если закрыт акк
			continue
		for friend in friendslist:
			if users.get(str(friend))!=None:
				users[str(friends)]+=str(friend)
				users[str(friends)]+=' '

	mainperson=str(users_ids.pop())+' '
	#выкидываем людей которые сами по себе
	for us in users_ids:
		if users[str(us)]=='' or users[str(us)]==mainperson or users[str(us)].split(' ')[1]=='':
			users.pop(str(us))

	users_ids=list(users.keys())
	users=list(users.items())
	print(len(users))

	edges=list()
	vertices=list()
	if as_edgelist==True:
		#группировка по группам
		count=0
		for i in range(len(users)):
			id_number=users[i][1].split(' ')
			vertices.append(int(users[i][0]))
			for number in id_number:
				if number!='':
					res=int(users[i][0]),int(number)
					edges.append(res)
	# каждой вершине даем имя как в ВК
	count=0
	for name in vertices:
		url=config.VK_CONFIG['url']+'users.get?'
		config.VK_CONFIG['user_id']=str(name)
		time.sleep(0.35)
		values=get_req(url,params=config.VK_CONFIG)
		values=values.get('response')
		if values!=None:
			vertices[count]=values[0]['first_name']+' '+values[0]['last_name']
		count+=1


	#каждому id даем номер
	users={user:'' for user in users_ids}
	count=0
	for i in users:
		users[str(i)]=count
		count+=1
	#строим список ребер
	edges1=list()
	for i in edges:
		k=i[0]
		temp1=users.get(str(k))
		k=i[1]
		temp2=users.get(str(k))
		if temp2!=None:
			value=temp1,temp2
			edges1.append(value)
	plot_graph(edges1,vertices)

def plot_graph(edges1,vertices):
	g = Graph(vertex_attrs={"label":vertices},
    edges=edges1, directed=False)
	N = len(vertices)
	visual_style = {}

	visual_style["layout"] = g.layout_fruchterman_reingold(
    maxiter=10000,
    area=N**2,
    repulserad=N**4,
    maxdelta=N/2
    )

	g.simplify(multiple=True, loops=True,)
	communities = g.community_edge_betweenness(directed=False)
	clusters = communities.as_clustering()
	print(clusters)

	pal = igraph.drawing.colors.ClusterColoringPalette(len(clusters))
	g.vs['color'] = pal.get_many(clusters.membership)

    # Отрисовываем граф

	plot(g, "social_network02.pdf",bbox = (30*N, 30*N) , **visual_style)

if __name__=='__main__':
	user_id=input('Введите id для составления графа:')
	users=get_friends(int(user_id),'')
	users_ids=list(users.get('response')['items'])
	full_users=[i for i in range(len(users_ids)+1)]
	for i in range(len(full_users)):
		if i<len(users_ids):
			full_users[i]=users_ids[i]
		else:
			full_users[i]=user_id
	get_network(full_users)


	

