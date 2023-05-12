import matplotlib.pyplot as plt
import numpy as np
import os
import shutil

output_dir = './result'


def create_directory():
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    else:
        shutil.rmtree(output_dir)
        os.mkdir(output_dir)


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


def draw_final_result(experiment_range, first_s_result, second_s_result):
    # create x-axis index
    index = np.arange(experiment_range[0], experiment_range[1], experiment_range[2])
    bar_width = 1
    plt.figure(figsize=(10, 5), dpi=300)
    plt.bar(index, first_s_result, width=bar_width, color='blue', label='First Strategy')
    plt.bar(index + bar_width, second_s_result, width=bar_width, color='orange', label='Second Strategy')
    # set x axis label
    plt.xlabel('Initial Infected Count')
    # plt.xticks(index + bar_width / 2, range(1, 11, 2))
    # set y axis label
    plt.ylabel('Results')
    # set title
    plt.title('Comparison of First Strategy and Second Strategy')
    # display the legend by specifying the position
    plt.legend(loc='lower left', bbox_to_anchor=(1, 0.5))
    # adjust the margin of the subplot so that the legend is not cut off
    plt.subplots_adjust(right=0.8)
    plt.gca().margins(x=0)
    plt.show()
