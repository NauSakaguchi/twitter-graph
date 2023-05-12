import json
import pandas as pd
import networkx as nx


def create_graph_from(filename):
    # log: start to read dataset
    print("Start to read dataset")

    # Do not separate by a comma if there is no space after the comma
    # If you use a regular expression as a delimiter, you need to specify the Python engine
    twitter_data = pd.read_csv(filename, sep=',(?=\S)', engine='python')
    # 1. removing unnecessary double quotes
    twitter_data["id"] = twitter_data["id"].apply(lambda x: x[1:-1])
    # 2. The list of friends (people followed) is saved as a single string. To convert it to a list of friend IDs,
    # use a JSON loader.
    for column in ["tags", "friends"]:
        twitter_data[column] = twitter_data[column].apply(lambda x: json.loads(x))
    # 3. drop unused column for this project
    twitter_data = twitter_data.drop(["lang", 'avatar', 'tweetId', 'screenName', 'lastSeen'], axis=1)
    # create a dictionary to find index from id
    id_index_dict = {}
    for index, row in twitter_data.iterrows():
        id_index_dict[row['id']] = index
    # log: start to create graph
    print("Start to create graph")
    # create directed graph: the node is the user, the edge is the connection between users
    G = nx.DiGraph()
    for _, row in twitter_data.iterrows():
        for friend in row['friends']:
            # ignore the users who are not in this dataset
            if friend in id_index_dict:
                G.add_edge(row['id'], friend)
    # show the number of nodes and edges
    print("Number of nodes: {}".format(G.number_of_nodes()))
    print("Number of edges: {}".format(G.number_of_edges()))
    return G, id_index_dict


def get_communities_from(G):
    print("Number of nodes: {}".format(G.number_of_nodes()))
    print("Number of edges: {}".format(G.number_of_edges()))
    # detect communities
    communities = list(nx.community.greedy_modularity_communities(G))
    print("Number of communities: {}".format(len(communities)))
    return communities


def reduce_graph_size(G):
    # k-core decomposition
    k_core = 20
    G = nx.k_core(G, k=k_core)

    # remove nodes with low in-degree
    min_in_degree = 20
    filtered_nodes = [node for node, in_degree in G.in_degree() if in_degree >= min_in_degree]
    G = G.subgraph(filtered_nodes)

    return G


def get_top_pr_from(communities, pr, list_size):
    # sort by page rank
    pr_sorted = sorted(pr.items(), key=lambda x: x[1], reverse=True)

    top_list = []
    # get top 1 node in each community
    for i in range(list_size):
        community = communities[i % len(communities)]
        pr_community = {node: pr[node] for node in community}
        pr_community_sorted = sorted(pr_community.items(), key=lambda x: x[1], reverse=True)
        # print("Community: {}, Node: {}, PageRank: {}".format(community, pr_community_sorted[0][0],
        #                                                      pr_community_sorted[0][1]))
        top_list.append(pr_community_sorted[0][0])
    return top_list
