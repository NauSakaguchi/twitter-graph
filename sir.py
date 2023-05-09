import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import json
import random


def create_graph_from(filename):
    # log: start to read dataset
    print("Start to read dataset")

    # Do not separate by a comma if there is no space after the comma
    # If you use a regular expression as a delimiter, you need to specify the Python engine
    twitterData = pd.read_csv(filename, sep=',(?=\S)', engine='python')
    # 1. removing unnecessary double quotes
    twitterData["id"] = twitterData["id"].apply(lambda x: x[1:-1])
    # 2. The list of friends (people followed) is saved as a single string. To convert it to a list of friend IDs, use a JSON loader.
    for column in ["tags", "friends"]:
        twitterData[column] = twitterData[column].apply(lambda x: json.loads(x))
    # 3. drop unused column for this project
    twitterData = twitterData.drop(["lang", 'avatar', 'tweetId', 'screenName', 'lastSeen'], axis=1)
    # create a dictionary to find index from id
    id_index_dict = {}
    for index, row in twitterData.iterrows():
        id_index_dict[row['id']] = index
    # log: start to create graph
    print("Start to create graph")
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
    return G, id_index_dict


def draw_result(cnt_list, title):
    print("Number of infected nodes: {}".format(cnt_list))
    # グラフの描画
    fig, ax = plt.subplots()
    x = list(range(len(cnt_list)))  # x軸の座標を作成
    ax.bar(x, cnt_list, width=1)
    # 軸ラベルとタイトルの設定
    ax.set_xlabel('hours')
    ax.set_ylabel('People')
    ax.set_title(title)
    # グラフの表示
    plt.show()


def sir_simulation(G, initial_infected_nodes, init_cnt, steps, infection_rate=0.01, bias=0.00005):
    # すべてのノードをSusceptibleに設定
    # infection_rate = 0.01
    cnt = init_cnt
    cnt_list = []
    status = {node: 'S' for node in G.nodes()}
    for node in initial_infected_nodes:
        status[node] = 'I'
    for t in range(steps):
        # show step number
        print("Step: {}".format(t + 1))
        # タイムステップごとの感染と回復のプロセス
        new_status = status.copy()
        for node in G.nodes():
            if status[node] == 'I':
                # 感染プロセス
                neighbors = list(G.successors(node))
                for neighbor in neighbors:
                    if status[neighbor] == 'S' and random.random() < infection_rate:
                        new_status[neighbor] = 'I'
                        cnt += 1
        cnt_list.append(cnt)
        status = new_status
        infection_rate = infection_rate - bias
        # print cnt
        print("Number of infected nodes: {}".format(cnt))
    return cnt_list


# show the number of nodes, edges and the number of communities
def get_communities_from(G):
    print("Number of nodes: {}".format(G.number_of_nodes()))
    print("Number of edges: {}".format(G.number_of_edges()))
    # detect communities
    communities = list(nx.community.greedy_modularity_communities(G))
    print("Number of communities: {}".format(len(communities)))
    return communities


def reduce_graph_size(G):
    k_core = 20
    G = nx.k_core(G, k=k_core)

    min_in_degree = 20
    filtered_nodes = [node for node, in_degree in G.in_degree() if in_degree >= min_in_degree]
    G = G.subgraph(filtered_nodes)

    return G


def get_top_pr_from(communities, pr):
    # sort by page rank
    pr_sorted = sorted(pr.items(), key=lambda x: x[1], reverse=True)

    top_list = []
    # show top 1 node in each community
    print("Top 1 node in each community by PageRank")
    for community in communities:
        pr_community = {node: pr[node] for node in community}
        pr_community_sorted = sorted(pr_community.items(), key=lambda x: x[1], reverse=True)
        print("Community: {}, Node: {}, PageRank: {}".format(community, pr_community_sorted[0][0],
                                                             pr_community_sorted[0][1]))
        top_list.append(pr_community_sorted[0][0])
    return top_list


# main function
def main():
    G, id_index_dict = create_graph_from("data.csv")

    # 情報伝搬の方向はフォロー関係とは逆になる。
    # つまり、フォローされている人の情報がフォロワーに伝わる
    G = G.reverse()

    # First Strategy
    # setup
    # ランダムにいくつかのノードをInfectedに設定
    init_cnt = 5
    hours = 200
    initial_infected_nodes = random.sample(list(G.nodes), init_cnt)  # 5は初期感染ノードの数を表します

    # execute SIR simulation
    cnt_list = sir_simulation(G, initial_infected_nodes, init_cnt, hours)
    draw_result(cnt_list, "Random")

    # Second Strategy
    # setup
    init_cnt = 5
    hours = 200
    preprocessed_graph = reduce_graph_size(G)
    initial_infected_nodes = get_top_pr_from(get_communities_from(preprocessed_graph),  nx.pagerank(preprocessed_graph))

    # execute SIR simulation
    cnt_list = sir_simulation(G, initial_infected_nodes, init_cnt, hours)
    draw_result(cnt_list, "PageRank")


if __name__ == "__main__":
    main()
