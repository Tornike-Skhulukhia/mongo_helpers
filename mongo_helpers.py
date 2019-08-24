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


def get_data_from_collection(db, col, sel,
                             projection={"_id": 0},
                             as_list=True,
                             host="localhost"):
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
    '''
    client, database = connect(db, host=host)
    collection = database[col]

    # get results
    cursor_obj = collection.find(sel, projection)

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
                                    ])
    distincts = [i['_id'] for i in distincts_ if i['_id']]  # remove Nones

    #####################################

    return list(distincts)


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

# a = get_data_from_collection(
#                             db="hello_db",
#                             col="data",
#                             sel={},
#                             projection=None,
#                             as_list=True)
# pp(a)
# print(len(a))
