def plot_download_speeds(
                    db_name,
                    col,
                    selectors,
                    max_length_to_graph=100,
                    update_interval=3,
                    custom_colors=True,
                    legend_side="lower left",
                    host="localhost"):
    '''
    function to visually track download speeds in mongodb-s
    specific collection, based on specific documents total number changes
    in given time.

    Creates dynamically updating line chart with one or more lines.

    arguments:
        1. db_name - database of data storage

        2. col - collection of data storage

        3. selectors - what fields to track in database
            (list of dictionary selectors like in mongodb)

        4. max_length_to_graph - number of maximum
              visible horizontal axis change to plot(default=100)

        5. update_interval - interval to update graph(in seconds)(default=3)

        6. custom_colors - set to False to use normal matplotlib colors
               (default=True, so 7 custom colors are used for first 7 lines)

        7. legend_side - string, denoting position of legend.
                    If set to False, no legend will be shown.
                    Other available options are:
                        . "best"
                        . "upper right"
                        . "upper left"
                        . "lower left" (default)
                        . "lower right"
                        . "right"
                        . "center left"
                        . "center right"
                        . "lower center"
                        . "upper center"
                        . "center"
        8. host - host(default="localhost")
    '''

    from mongo_helpers import connect
    # from time import sleep
    import matplotlib
    import matplotlib.pyplot as plt
    import random

    from matplotlib.animation import FuncAnimation

    # plt.style.use("fivethirtyeight")
    plt.style.use("dark_background")

    matplotlib.rcParams.update({"font.size": 9})
    matplotlib.rcParams.update({"font.weight": 400})

    # if more colors are needed, system ones will be used
    colors = ["red", "blue", "yellow", "lime", "cyan", "magenta", "orange"]
    random.shuffle(colors)

    # from pprint import pprint as pp

    ###############################################################
    # define helper functions
    ###############################################################
    def _get_documents_number(database_obj, collection_name, selector):
        '''
        return number of elements with given query in database

        arguments:
            1. database_obj - pymongo connection to database
            2. collection_name - name of collection
            3. selector - selector to count document based on.
                if is empty ({}, or other Falsy value), speed is much faster,
                than when filtering.
        '''
        collection = database[collection_name]

        # full data case
        if not selector:
            ans = collection.estimated_document_count()
        else:
            # specific data selection case
            ans = collection.count_documents(selector)
        return ans

    def _get_working_key_name(db_name, col, selector):
        '''
        generate working key name to display
        on live graph and also work with as string.

        arguments:
            1.database name
            2.col - colletion name
            3.selector - selector that we are using(dict)
        '''
        answer = f'{db_name} - {col} | '

        if selector:
            answer += (f'{list(selector.keys())[0]} : '
                       f'{list(selector.values())[0]}')
        return answer

    ###########################################################
    # connect to database
    client, database = connect(db_name)

    # create dictionary that stores totals after each
    # time_interval passes as list.
    # as keys, use formatted text returned
    # from function _get_working_key_name

    totals_data = {}

    # initialize first counts
    for selector in selectors:
        key = _get_working_key_name(db_name, col, selector)
        value = _get_documents_number(database, col, selector)

        # list of (totals number, speed)
        # (save speed to not calculate every time)
        totals_data[key] = [[value, 0]]

    def animate(i):
        '''
        updates and plots data
        '''
        # clear
        plt.cla()

        # update data
        for selector in selectors:
            key = _get_working_key_name(db_name, col, selector)

            current_total = _get_documents_number(database, col, selector)
            previous_total = totals_data[key][-1][0]

            # calculate current speed
            current_speed = current_total - previous_total
            totals_data[key].append((current_total, current_speed))

            if isinstance(totals_data[key][0], list):
                totals_data[key].pop(0)  # delete it
                # return  # continue

        # plot data
        for index_, selector in enumerate(selectors):  # optimize later
            # label
            key = _get_working_key_name(db_name, col, selector)

            # y values to plot(generate x-s automatically)
            data_list = totals_data[key][-max_length_to_graph:]
            y_values = [i[1] for i in data_list]
            # generate x values based on time intervals
            x_values = [
                index * update_interval for index, i in enumerate(data_list)]

            color = None  # in this case, system default is used
            if index_ < len(colors):
                color = colors[index_]

            plt.plot(x_values,
                     y_values,
                     linewidth=1,
                     label=key.split("-")[-1],
                     color=color)
        # change few things
        plt.grid()
        plt.title(f'Live Chart(Update time: {update_interval} second)')
        plt.xlabel("Time")
        plt.ylabel("Speed")

        if legend_side:
            plt.legend(loc=legend_side)

        # breakpoint()

    anim = FuncAnimation(
                    plt.gcf(),
                    animate,
                    interval=update_interval * 1000)
    plt.show()


########################
# test
########################
db_name = "usa_states"
col = "CA"
host = "localhost"

selectors = [
            # {"Status": "ACTIVE"},
            # {},
            # {"Status": "CANCELED"},
            {"Status": i} for i in ['FORFEITED', 'SUSPENDED', 'SURRENDER', 'FTB FORFEITED', 'SOS CANCELED', 'DISSOLVED', 'SOS FORFEITED', 'CONVERTED-OUT', 'CANCELED', 'BANK CONVERSION', 'FTB SUSPENDED', 'TERM EXPIRED', 'INACTIVE', 'SOS/FTB SUSPENDED', 'ACTIVE', 'SOS/FTB FORFEITED', 'MERGED OUT', 'SOS SUSPENDED'][:]
        ] + [{}]

max_length_to_graph = 100
update_interval = 20  # seconds


plot_download_speeds(
                    db_name,
                    col,
                    selectors,
                    max_length_to_graph,
                    update_interval)