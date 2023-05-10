#!/usr/bin/env python
# coding: utf-8

# # Import librarly

# In[1]:


import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import math
import numpy as np


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

communities = print_graph_summary(G)


# ### K-Core Decomposition:

# In[10]:


k_core = 20
G = nx.k_core(G, k=k_core)

communities = print_graph_summary(G)


# # Network Characterization

# In[11]:


# print number of nodes and edges with format
print("Number of nodes: {}\n".format(G.number_of_nodes()))
print("Number of edges: {}\n".format(G.number_of_edges()))


# In[12]:


# find the five nodes with the highest clustering coefficients with format
hi_clustring_coeff = sorted(nx.clustering(G).items(), key=lambda x: x[1], reverse=True)[:5]

# find the five nodes with the highest betweenness centrality with format
hi_betweeness_cen = sorted(nx.betweenness_centrality(G).items(), key=lambda x: x[1], reverse=True)[:5]


# In[13]:


# enumerate the five nodes with the highest clustering coefficients
for i, (node, coeff) in enumerate(hi_clustring_coeff):
    # get index from id
    index = id_index_dict[node]
    print("{}. clustering coefficient: {}".format(i+1, coeff))
    # print the row of the node
    print(twitterData.iloc[index])
    print()


# In[14]:


# enumerate the five nodes with the highest betweenness centrality
for i, (node, betweenness) in enumerate(hi_betweeness_cen):
    # get index from id
    index = id_index_dict[node]
    print("{}. betweenness centrality: {}".format(i+1, betweenness))
    # print the row of the node
    print(twitterData.iloc[index])
    print()


# In[15]:


# print number of connected components with format
print("Number of connected components: {}".format(nx.number_connected_components(G.to_undirected())))
# print the diameter of the graph with format
for i, component in enumerate(nx.connected_components(G.to_undirected())):
    print("Diameter of the component {}: {}".format(i + 1, nx.diameter(G.subgraph(component).to_undirected())))


# ### Visualization

# In[16]:


# combine the nodes in communities
community_dict = {node: -1 for node in G.nodes()}
community_dict = {node: cid for cid, community in enumerate(communities) for node in community}

# set the color of nodes
colors = list(mcolors.TABLEAU_COLORS.keys()) + list(mcolors.CSS4_COLORS.keys())
node_color = [colors[community_dict[node] % len(colors)] for node in G.nodes()]


# In[17]:


nx.draw(G, node_color=node_color, with_labels=False, node_size=10, alpha=0.5, width=0.1)
plt.show()


# In[19]:


# calculate the number of rows and columns of subplots
n_communities = len(communities)
n_columns = math.ceil(math.sqrt(n_communities))
n_rows = math.ceil(n_communities / n_columns)

# set the size of subplots
fig, axes = plt.subplots(nrows=n_rows, ncols=n_columns, figsize=(3 * n_columns, 3 * n_rows))

# draw subgraphs
for i, community in enumerate(communities):
    # サブグラフの生成
    subgraph = G.subgraph(community)

    # サブグラフのノードの色を設定
    subgraph_node_color = [colors[community_dict[node] % len(colors)] for node in subgraph.nodes()]

    # サブグラフの描画
    ax = axes[i // n_columns, i % n_columns]
    ax.set_title(f"Community {i + 1}")
    nx.draw(subgraph, node_color=subgraph_node_color, with_labels=False, node_size=10, alpha=0.5, width=0.1, ax=ax)

# delete empty subplots
for i in range(n_communities, n_rows * n_columns):
    fig.delaxes(axes[i // n_columns, i % n_columns])

# グラフを表示
plt.tight_layout()
plt.show()


# In[44]:


# create a list of graph of all communities
graphs = [G.subgraph(community) for community in communities]

# community_tags: the list of sets of tags in each community
# community_ratios: the list of ratios of tags in each community
community_tags = []
community_ratios = []

for i, graph in enumerate(graphs):
    # グラフのノード数とエッジ数を表示
    print(f"Community {i + 1}")
    print("\tNumber of nodes: {}".format(graph.number_of_nodes()))
    print("\tNumber of edges: {}".format(graph.number_of_edges()))

    # using id_index_dict, get the index of nodes in the graph
    # then, get the tags of the nodes
    # finally, get the set of tags in the graph
    tags = set()
    for node in graph.nodes():
        tags.update(twitterData['tags'][id_index_dict[node]])
        
    # count the number of tags in the graph
    tag_count = {tag: 0 for tag in tags}
    total_count = 0
    for node in graph.nodes():
        for tag in twitterData['tags'][id_index_dict[node]]:
            tag_count[tag] += 1
            total_count += 1

    # sort the tags by the number of appearance
    tag_count = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)
    
    # display the top 3 tags and their ratios
    top_tags = []
    top_ratios = []
    for tag, count in tag_count[:3]:
        ratio = count / total_count * 100
        print(f"\t- {tag}: {ratio:.2f}%")
        top_tags.append(tag)
        top_ratios.append(ratio)

    # if the number of tags is less than 3, add empty strings and 0s
    # to make the length of the list 3
    if len(top_tags) < 3:
        top_tags = top_tags + ["", ""]
        top_ratios = top_ratios + [0, 0]
    community_tags.append(top_tags)
    community_ratios.append(top_ratios)

    print()


# In[47]:


# 描画
n_communities = len(communities)
bar_width = 0.3
index = np.arange(3)

fig, axes = plt.subplots(nrows=n_rows, ncols=n_columns, figsize=(4 * n_columns, 4 * n_rows))

for i in range(n_communities):
    ax = axes[i // n_columns, i % n_columns]
    ax.bar(index - bar_width / 2, community_ratios[i], width=bar_width, tick_label=community_tags[i])
    ax.set_title(f"Community {i + 1}")
    ax.set_ylim(0, 110)  # fix the range of y-axis
#     ax.set_xlabel('Hashtags')
    ax.set_ylabel('Occurrence Ratio (%)')
    # rotate the labels of x-axis for readability
    ax.tick_params(axis='x', rotation=45)

# delete empty subplots
for i in range(n_communities, n_rows * n_columns):
    fig.delaxes(axes[i // n_columns, i % n_columns])

plt.tight_layout()
plt.show()

