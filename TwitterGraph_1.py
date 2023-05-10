#!/usr/bin/env python
# coding: utf-8

# # Import librarly

# In[1]:


import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# # Read dataset

# In[2]:


# Do not separate by a comma if there is no space after the comma
# If you use a regular expression as a delimiter, you need to specify the Python engine
twitterData = pd.read_csv("data.csv", sep=',(?=\S)', engine='python')

twitterData.head()


# ## Modify dataset

# In[3]:


# 1. removing unnecessary double quotes
twitterData["id"] = twitterData["id"].apply(lambda x: x[1:-1])
    
# 2. The list of friends (people followed) is saved as a single string. To convert it to a list of friend IDs, use a JSON loader.
for column in ["tags", "friends"]:
    twitterData[column] = twitterData[column].apply(lambda x: json.loads(x))

# 3. drop unused column for this project
twitterData = twitterData.drop(["lang", 'avatar', 'tweetId', 'screenName', 'lastSeen'], axis=1)

twitterData.head()


# In[4]:


twitterData.info()


# # Prerpocess

# In[5]:


# friends: the list of IDs the user follows
# friendsCount: the length of the friends list
twitterData.describe()


# In[6]:


# create a dictionary to find index from id
id_index_dict = {}
for index, row in twitterData.iterrows():
    id_index_dict[row['id']] = index


# In[7]:


# show the number of nodes, edges and the number of communities
def print_graph_summary(G):
    print("Number of nodes: {}".format(G.number_of_nodes()))
    print("Number of edges: {}".format(G.number_of_edges()))
    # detect communities
    communities = list(nx.community.greedy_modularity_communities(G))
    print("Number of communities: {}".format(len(communities)))
    return communities


# In[8]:


# create directed graph: the node is the user, the edge is the connection between users
G = nx.DiGraph()

for _, row in twitterData.iterrows():
    for friend in row['friends']:
        # ignore the users who are not in this dataset
        if friend in id_index_dict:
            G.add_edge(row['id'], friend)
            
# show the number of nodes and edges
print("Number of nodes: {}".format(G.number_of_nodes()))
print("Number of edges: {}".format(G.number_of_edges()))


# ### Degree-based filtering:

# In[9]:


min_in_degree = 20
filtered_nodes = [node for node, in_degree in G.in_degree() if in_degree >= min_in_degree]
G = G.subgraph(filtered_nodes)

print_graph_summary(G)


# ### K-Core Decomposition:

# In[12]:


k_core = 20
G = nx.k_core(G, k=k_core)

communities = print_graph_summary(G)


# # Network Characterization

# In[ ]:
# print number of nodes and edges with format
print("Number of nodes: {}\n".format(G.number_of_nodes()))
print("Number of edges: {}\n".format(G.number_of_edges()))

# print the five nodes with the highest clustering coefficients with format
hi_clustring_coeff = sorted(nx.clustering(G).items(), key=lambda x: x[1], reverse=True)[:5]
print("Five nodes with the highest clustering coefficients: \n{}\n".format(hi_clustring_coeff))
# enumerate the five nodes with the highest clustering coefficients
for i, (node, coeff) in enumerate(hi_clustring_coeff):
    # get index from id
    index = id_index_dict[node]
    print("{}. node: {}, clustering coefficient: {}".format(i+1, node, coeff))
    # print the row of the node
    print(twitterData.iloc[index])

# print the five nodes with the highest betweenness centrality with format
hi_betweeness_cen = sorted(nx.betweenness_centrality(G).items(), key=lambda x: x[1], reverse=True)[:5]
print("Five nodes with the highest betweenness centrality: \n{}\n".format(hi_betweeness_cen))

# print number of connected components with format
print("Number of connected components: {}".format(nx.number_connected_components(G.to_undirected())))
# print the diameter of the graph with format
for component in nx.connected_components(G.to_undirected()):
    print("Diameter of the component: {}".format(nx.diameter(G.subgraph(component).to_undirected())))
# print("Diameter of the graph: {}".format(nx.diameter(G.to_undirected())))
