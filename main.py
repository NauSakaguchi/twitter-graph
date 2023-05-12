import networkx as nx
import random

from graph import create_graph_from, reduce_graph_size, get_communities_from, get_top_pr_from
from sir import sir_simulation
from visualizer import draw_result, draw_final_result, create_directory


# main function
def main():
    ###############################
    # create a directory to save the result
    ###############################
    create_directory()
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
    trial_cnt = 10
    first_s_result = []
    second_s_result = []
    # (start, end, step)
    experiment_range = (1, 122, 2)
    ###########################
    for init_cnt in range(experiment_range[0], experiment_range[1], experiment_range[2]):
        print("{}/{}".format(init_cnt, experiment_range[1]))
        result = first_strategy(G, hours, init_cnt, trial_cnt)
        first_s_result.append(result)

        result = second_strategy(G, hours, init_cnt, trial_cnt)
        second_s_result.append(result)

    draw_final_result(experiment_range, first_s_result, second_s_result)


def first_strategy(G, hours, init_cnt, trial_cnt):
    ###############################
    # First Strategy
    ###############################
    # setup
    max_cnt = 0
    best_result = []
    total_cnt = 0
    for i in range(trial_cnt):
        print("Trial: {}".format(i + 1))
        # set nodes to infected randomly
        initial_infected_nodes = random.sample(list(G.nodes), init_cnt)

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


def second_strategy(G, hours, init_cnt, trial_cnt):
    ###############################
    # Second Strategy
    ###############################
    # setup
    max_cnt = 0
    best_result = []
    total_cnt = 0
    # setup
    preprocessed_graph = reduce_graph_size(G)
    communities = get_communities_from(preprocessed_graph)
    pr = nx.pagerank(preprocessed_graph)
    for i in range(trial_cnt):
        print("Trial: {}".format(i + 1))
        initial_infected_nodes = get_top_pr_from(communities, pr, init_cnt)
        # execute SIR simulation
        cnt_list = sir_simulation(G, initial_infected_nodes, init_cnt, hours)
        total_cnt += cnt_list[-1]
        if cnt_list[-1] > max_cnt:
            max_cnt = cnt_list[-1]
            best_result = cnt_list

    print("Infected nodes: {}".format(total_cnt / trial_cnt))
    draw_result(best_result, str(init_cnt).zfill(3) + "-PageRank")

    return total_cnt / trial_cnt
    ###########################


if __name__ == "__main__":
    main()
