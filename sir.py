import shutil

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import json
import random
import os
import numpy as np

output_dir = './result'


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
    path = output_dir + '/' + title + '.png'
    # print("Number of infected nodes: {}".format(cnt_list))

    fig, ax = plt.subplots()
    x = list(range(len(cnt_list)))  # create x axis
    ax.bar(x, cnt_list, width=1)
    # set x axis label and y axis label
    ax.set_xlabel('hours')
    ax.set_ylabel('People')
    ax.set_title(title)
    plt.gca().margins(x=0)

    # save graph
    plt.savefig(path)
    # plt.show() # show graph

    plt.close()


####################
# SIR model ########
# G: graph
# initial_infected_nodes: the list of initial infected nodes
# init_cnt: the number of initial infected nodes
# steps: the number of steps
# infection_rate: the probability of infection
# bias: the bias of infection rate
# return: the list of the number of infected nodes
def sir_simulation(G, initial_infected_nodes, init_cnt, steps, infection_rate=0.01, bias=0.00005):
    cnt = init_cnt
    cnt_list = []
    # set all nodes to susceptible
    status = {node: 'S' for node in G.nodes()}
    for node in initial_infected_nodes:
        status[node] = 'I'
    for t in range(steps):
        # show step number
        # print("Step: {}".format(t + 1))
        # process of infection for each time step
        new_status = status.copy()
        for node in G.nodes():
            if status[node] == 'I':
                # infection process
                neighbors = list(G.successors(node))
                for neighbor in neighbors:
                    if status[neighbor] == 'S' and random.random() < infection_rate:
                        new_status[neighbor] = 'I'
                        cnt += 1
        cnt_list.append(cnt)
        status = new_status
        infection_rate = infection_rate - bias
        # print cnt
        # print("Number of infected nodes: {}".format(cnt))
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


# main function
def main():
    ###############################
    # create a directory to save the result
    ###############################
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    else:
        shutil.rmtree(output_dir)
        os.mkdir(output_dir)
    ###########################

    ###############################
    # create a graph from the dataset
    ###############################
    G, id_index_dict = create_graph_from("data.csv")

    # the direction of information propagation is opposite to the follow relationship.
    # In other words, the information of the person who is followed is propagated to the follower.
    G = G.reverse()
    ###########################

    ###############################
    # set parameters for SIR simulation
    ###############################
    hours = 200
    trial_cnt = 1
    first_s_result = []
    second_s_result = []
    # (start, end, step)
    experiment_range = (1, 5, 2)
    ###########################
    for init_cnt in range(experiment_range[0], experiment_range[1], experiment_range[2]):
        print("{}/{}".format(init_cnt, experiment_range[1]))
        result = first_strategy(G, hours, init_cnt, trial_cnt)
        first_s_result.append(result)

        result = second_strategy(G, hours, init_cnt)
        second_s_result.append(result)

    # create x axis index
    index = np.arange(experiment_range[0], experiment_range[1], experiment_range[2])

    bar_width = 1
    plt.bar(index, first_s_result, width=bar_width, color='blue', label='First Strategy')
    plt.bar(index + bar_width, second_s_result, width=bar_width, color='orange', label='Second Strategy')

    # set x axis label
    plt.xlabel('Initial Infected Count')
    # plt.xticks(index + bar_width / 2, range(1, 11, 2))

    # set y axis label
    plt.ylabel('Results')

    # set title
    plt.title('Comparison of First Strategy and Second Strategy')
    plt.legend()

    plt.gca().margins(x=0)

    plt.show()


def first_strategy(G, hours, init_cnt, trial_cnt):
    ###############################
    # First Strategy
    ###############################
    max_cnt = 0
    best_result = []
    total_cnt = 0
    for i in range(trial_cnt):
        print("Trial: {}".format(i + 1))
        # setup
        # ランダムにいくつかのノードをInfectedに設定
        initial_infected_nodes = random.sample(list(G.nodes), init_cnt)  # 5は初期感染ノードの数を表します

        # execute SIR simulation
        cnt_list = sir_simulation(G, initial_infected_nodes, init_cnt, hours)
        total_cnt += cnt_list[-1]
        if cnt_list[-1] > max_cnt:
            max_cnt = cnt_list[-1]
            best_result = cnt_list
    # show the average number of infected nodes
    print("Average number of infected nodes: {}".format(total_cnt / trial_cnt))
    draw_result(best_result, str(init_cnt).zfill(3) + "-Random")

    return total_cnt / trial_cnt
    ###########################


def second_strategy(G, hours, init_cnt):
    ###############################
    # Second Strategy
    ###############################
    # setup
    preprocessed_graph = reduce_graph_size(G)
    initial_infected_nodes = get_top_pr_from(get_communities_from(preprocessed_graph), nx.pagerank(preprocessed_graph),
                                             init_cnt)
    # execute SIR simulation
    cnt_list = sir_simulation(G, initial_infected_nodes, init_cnt, hours)
    print("Infected nodes: {}".format(cnt_list[-1]))
    draw_result(cnt_list, str(init_cnt).zfill(3) + "-PageRank")

    return cnt_list[-1]
    ###########################


if __name__ == "__main__":
    main()
