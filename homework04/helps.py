from igraph import Graph, plot
import numpy as np
from random import randint
from igraph import graph_from_adjacency_matrix
# Создание вершин и ребер
vertices = [i for i in range(7)]
matrix=[[i for i in range(7)] for i in range(7)]
print(matrix)
count=0
count1=0
for i in range(len(matrix)):
    for j in range(len(matrix)):
        if i!=0 and j!=0:
            matrix[i][j]=randint(0,1)
        elif i!=0:
            matrix[i][j]=count
    count+=1
print(matrix)


# Создание графа
g = graph_from_adjacency_matrix(matrix)
# Задаем стиль отображения графа
N = len(vertices)
visual_style = {}
visual_style["layout"] = g.layout_fruchterman_reingold(
    maxiter=1000,
    area=N**3,
    repulserad=N**3)

# Отрисовываем граф
plot(g, **visual_style)