'''
    helper functions to work with mongodb
'''


def connect(db, host="localhost"):
    '''
    connect to database
    and get client and connection object.
    client - useful to close connection later.

    arguments:
        1. db - database name
        2. host - host(default="localhost")
    '''
    from pymongo import MongoClient

    client = MongoClient(host)
    return (client, client[db])


def get_collection_names(db, host="localhost"):
    '''
    get all collection names as list

        arguments:
        1. db - database name
        2. host - host(default="localhost")
    '''
    client, database = connect(db)
    return database.list_collection_names()


def get_documents_number(db, col, selector):
    '''
    return number of elements with given query in database

    arguments:
        1. db - database name
        2. col - name of collection
        3. selector - selector to count document based on.
            if is empty ({}, or other Falsy value), speed is much faster,
            than when filtering.
    '''
    client, database = connect(db)
    collection = database[col]

    # full data case
    if not selector:
        ans = collection.estimated_document_count()
    else:
        # specific data selection case
        ans = collection.count_documents(selector)
    return ans



def remove_from_collection(db, col, selector, host="localhost"):
    '''
    delete documents from collection, matching given selector.

    arguments:
        1. db - database name
        2. col - collection to insert data into
        3. selector - selector to match documents we want to delete
        4. host - host(default="localhost")
    '''
    client, database = connect(db, host=host)
    collection = database[col]

    collection.remove(selector)


def insert_in_collection(db, col, data, host="localhost"):
    '''
    save one/multiple records in collection

    arguments:
        1. db - database name
        2. col - collection to insert data into
        3. data - document/documents to insert,
                  if it is the instance of dict, it
                  will be directly saved(insertOne),
                  otherwise all list/tuple/generator
                  items individually(insertMany)
        4. host - host(default="localhost")
    '''
    client, database = connect(db, host=host)
    collection = database[col]

    if isinstance(data, dict):
        collection.insert_one(data)
    else:  # do not do additional checks here
        collection.insert_many(data)

    client.close()


def update_in_collection(db,
                         col,
                         selector,
                         replacement,
                         upsert=True,
                         host="localhost",
                         update_all=False):
    '''
    update collection record

    arguments:
        1. db - database name
        2. col - collection name
        3. selector - selector to select record/records
                which we want to update
        4. replacement - what to update in record/records
        5. upsert - set to True, to create new document
                    if no document found(default=True)
        6. host - host(default="localhost")
        7. update_all - set to False to update only first match(default=False)
    '''
    client, database = connect(db, host=host)
    collection = database[col]

    method = [collection.update_one, 
              collection.update_many][int(update_all)]

    method(selector, replacement, upsert=upsert)


def get_from_collection(db, col, sel,
                             projection={"_id": 0},
                             as_list=True,
                             host="localhost",
                             sort_by=[],
                             limit=None):
    '''
    get data from collection using find method

    arguments:
        1. db - database name
        2. col - collection name
        3. sel - selector to select data
        4. projection - which fields do we want to get
                        from matched documents.
                        if set to other value(default="_id": 0}),
                        this other value will be used, otherwise
                        results will have all available fields
                        except _id.
                        To get everything including _id-s,
                        set projection to None
        5. as_list - if set to True(defatult), result will be list,
                    otherwise, cursor object with results
        6. host - host(default="localhost")
        7. sort_by - sort to use(list of tuples)
        8. limit - number of records to limit output,
                    default - None - no limit.
    '''
    client, database = connect(db, host=host)
    collection = database[col]

    # get results
    cursor_obj = collection.find(sel, projection, sort=sort_by)

    # add limit if necessary
    if isinstance(limit, int): cursor_obj = cursor_obj.limit(limit)

    client.close()
    return cursor_obj if not as_list else list(cursor_obj)


def get_distinct_values(db, col, field, filter_sel={}, host="localhost"):
    '''
    get list of distinct values for specific field,
    even if its size is more than 16mb

    arguments:
        1. db - database name
        2. col - collection
        3. field - field for which we want distinct values for
        4. filter_sel - selector to filter documents(default={})
        5. host - host(default="localhost")
    '''
    client, database = connect(db, host=host)

    #####################################
    # use mongos aggregation
    #####################################
    distincts_ = database[col].aggregate([
                                    {"$match": filter_sel},
                                    {"$group": {"_id": f"${field}"}},
                                    ],
                                    allowDiskUse=True)

    distincts = [i['_id'] for i in distincts_ if i['_id']]  # remove Nones

    #####################################

    return list(distincts)


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

            For example, if
            ---------------------------------------------
            selectors = [
                    {"site":"facebook.com"},
                    {"site":""twitter.com}]
            ---------------------------------------------
            graph will show how documents number containing "site" fields
            facebook.com and twitter.com changes over time in given collection.

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
        collection = database_obj[collection_name]

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

        # breakpoint()

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

            # y values to plot
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

# #############################################################
# # # test
# from pprint import pprint as pp

# print(len(a))

# pp(a,  width=100)

# # insert_in_collection(
#                     db="hello_db",db 
#                     col="data",
#                     data=[{"data": "hello new document"}]
#                 )

# a = get_from_collection(
#                             db="hello_db",
#                             col="data",
#                             sel={},
#                             projection=None,
#                             as_list=True)
# pp(a)
# print(len(a))
