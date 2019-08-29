'''
    Live matplotlib graphs for better visualisation
'''

import sys

# max_length_to_graph = 100
# update_interval = 3000  # millisecond to update graph

max_length_to_graph, update_interval, total_or_speeds, DB, COLLECTION = \
                                                                sys.argv[1:]
max_length_to_graph, update_interval = \
                int(max_length_to_graph), int(update_interval)

from matplotlib import pyplot as plt
# from pprint import pprint as pp
import random
# import pandas as pd
# from itertools import count
from matplotlib.animation import FuncAnimation

# plt.style.use("fivethirtyeight")
plt.style.use("dark_background")


start_index = 0
end_index = start_index + 20

# countries = all_countries[start_index: end_index]
countries = ["registrers"]



def get_total_for(country):
    '''
    get number of total results for country
    '''

    import pymongo
    client = pymongo.MongoClient("localhost")

    # we use soopage_ here to refer to second database

    # db = client["registrers"]
    # col = db["Denmark"]

    db = client[DB]
    col = db[COLLECTION]

    # breakpoint()
    total_num = col.estimated_document_count()
    return total_num


# print(get_total_for("United Kingdom"))
# exit()

# x_vals = list(range(6))
# y_vals = list(range(6))


# x_vals, y_vals = [0], []
# speeds = [0]
# totals = [get_total_for(country)]

# create dict to use as we have multiple dynamic lists
# inner_info = {"x_vals": [], "speeds": [], "totals": []}

live_data = {
    country: {"x_vals": [], "speeds": [], "totals": []}
    for country in countries
}


# index = count()
index = 0

###########################################################################
# coloring
# countries = [country_1, country_2]
#####################################
# from matplotlib import colors as mcolors
# colors = {i for i in mcolors.CSS4_COLORS.keys()}
colors = ["red", "blue",  "yellow", "lime", "cyan", "magenta", "orange"]

#####################################
colors = [
      # 'blue',
      # 'brown',
      # 'cyan',
      # 'fuchsia',
      # 'indigo',
      'lime',
      'orangered',
      # 'sienna',
      # 'pink',
      'red',
      # 'purple',
      'yellow',
      'orange',
      # 'midnightblue',
      'magenta',
      # 'lightslategray',
      # 'lightgrey',
      # 'floralwhite',
      # 'coral'
]
# colors = ["lime"]
#####################################
# colors.remove("black")
colors = list(colors)
random.shuffle(colors)


# exit()
###########################################################################


def animate(i):
    global index, colors

    plt.cla()


    for index_, country in enumerate(countries):
        live_data[country]['x_vals'].append(index)

        # calculate difference
        live_data[country]['totals'].append(get_total_for(country))

        if len(live_data[country]['totals']) == 1:
            curr_speed = 0
        else:
            curr_speed = live_data[country]['totals'][i + 1] - \
                         live_data[country]['totals'][i]

        live_data[country]['speeds'].append(curr_speed)

        # # y_vals.append(random.randint(0, 5))
        # curr_speed = sum(speeds[i: i +1])
        # speeds.append(curr_speed)

        # plt.title(f'Showing speed for {country}')
        # plt.title(f'Speed In Live(downloads in {update_interval // 1000} second)')
        plt.title(f'Live Chart(Update time: {update_interval // 1000} second)')
        plt.grid()
        plt.plot(
            live_data[country]['x_vals'][-max_length_to_graph:],
            live_data[country][total_or_speeds][-max_length_to_graph:],
            color=colors[index_],
            linewidth=1,
            label=DB + " - " + COLLECTION.upper(),
            # label="Python is cool",
            # label="Python " + str(countries.index(country)),
            )

        plt.xlabel("Time")
        plt.ylabel("Speed")

    index += 1
    plt.legend(loc="lower left")
    # print(index)


ani = FuncAnimation(plt.gcf(), animate, interval=update_interval)


# plt.plot(x_vals, speeds)
# plt.title(f'Showing speed for {country}')
# plt.grid()
# plt.tight_layout()
plt.show()
