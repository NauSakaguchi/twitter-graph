#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json 
import datetime

import numpy as np 
import pandas as pd

import networkx as nx
import matplotlib.pyplot as plt


# In[2]:


twitterData = pd.read_csv("data.csv", sep=',(?=\S)', engine='python')
twitterData.head()


# In[3]:


def delete_quotes(x):
    return x[1:-1]
for column in ["id", "screenName", "avatar", "lang", "tweetId"]:
    twitterData[column] = twitterData[column].apply(delete_quotes)
    
for column in ["tags", "friends"]:
    twitterData[column] = twitterData[column].apply(lambda x: json.loads(x))


# In[4]:


twitterData.head()


# In[5]:


twitterData.info()


# In[6]:


twitterData.describe()


# In[7]:


twitterData['lang'].value_counts()


# In[8]:


twitterData = twitterData.drop(["lang", 'avatar', 'tweetId', 'screenName', 'lastSeen'], axis=1)
twitterData.head()


# In[9]:


print(len(twitterData['friends'][1]))


# In[10]:


twitterData.info()


# ## 辞書を作成

# In[11]:


id_index_dict = {}
for index, row in twitterData.iterrows():
    id_index_dict[row['id']] = index


# In[12]:


print('1969527638' in id_index_dict)


# ## グラフの作成

# In[13]:


G = nx.DiGraph()

for _, row in twitterData.iterrows():
    for friend in row['friends']:
        if friend in id_index_dict:
            G.add_edge(row['id'], friend)


# show the number of nodes and edges
print(G.number_of_nodes())
print(G.number_of_edges())


# In[18]:
min_in_degree = 20  # 最小入次数
filtered_nodes = [node for node, in_degree in G.in_degree() if in_degree >= min_in_degree]
G_filtered = G.subgraph(filtered_nodes)
print(G_filtered.number_of_nodes())
print(G_filtered.number_of_edges())

k_core = 20  # k-コアのk値
G_filtered = nx.k_core(G_filtered, k=k_core)
print(G_filtered.number_of_nodes())
print(G_filtered.number_of_edges())

# detect communities
communities = list(nx.community.greedy_modularity_communities(G_filtered))
print(len(communities))

# コミュニティのインデックス付け
community_dict = {node: -1 for node in G_filtered.nodes()}
community_dict = {node: cid for cid, community in enumerate(communities) for node in community}

# ノードの色をコミュニティに応じて設定
import matplotlib.colors as mcolors
colors = list(mcolors.TABLEAU_COLORS.keys()) + list(mcolors.CSS4_COLORS.keys())
node_color = [colors[community_dict[node] % len(colors)] for node in G_filtered.nodes()]

# グラフの描画
nx.draw(G_filtered, node_color=node_color, with_labels=False, node_size=10, alpha=0.5, width=0.1)
plt.show()


