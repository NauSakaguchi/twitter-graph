import random


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
