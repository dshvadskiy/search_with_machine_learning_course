#
# The main search hooks for the Search Flask application.
#
import json
from typing import Union, List, Optional

from flask import (
    Blueprint, redirect, render_template, request, url_for,
)
from flask_cors import CORS

from week1 import executor
from week1.opensearch import get_opensearch

bp = Blueprint('search', __name__, url_prefix='/search')

CORS(bp)


# Process the filters requested by the user and return a tuple that is appropriate for use in: the query, URLs displaying the filter and the display of the applied filters
# filters -- convert the URL GET structure into an OpenSearch filter query
# display_filters -- return an array of filters that are applied that is appropriate for display
# applied_filters -- return a String that is appropriate for inclusion in a URL as part of a query string.  This is basically the same as the input query string
def process_filters(filters_input):
    # Filters look like: &filter.name=regularPrice&regularPrice.key={{ agg.key }}&regularPrice.from={{ agg.from }}&regularPrice.to={{ agg.to }}
    filters = []
    display_filters = []  # Also create the text we will use to display the filters that are applied
    applied_filters = ""
    for filter in filters_input:
        type = request.args.get(filter + ".type")
        display_name = request.args.get(filter + ".displayName", filter)

        #
        # We need to capture and return what filters are already applied so they can be automatically added to any existing links we display in aggregations.jinja2
        applied_filters += "&filter.name={}&{}.type={}&{}.displayName={}".format(filter, filter, type, filter,
                                                                                 display_name)
        # TODO: IMPLEMENT AND SET filters, display_filters and applied_filters.
        # filters get used in create_query below.  display_filters gets used by display_filters.jinja2 and applied_filters gets used by aggregations.jinja2 (and any other links that would execute a search.)
        if type == "range":
            filter_exp = {
                "range": {
                    filter: {
                        "gte": request.args.get(filter + ".from")
                    }
                }
            }
            if request.args.get(filter + ".to"):
                filter_exp['range'][filter]["lte"] = request.args.get(filter + ".to")
            filters.append(filter_exp)
            applied_filters += f"&{filter}.from={request.args.get(filter + '.from')}&{filter}.to={request.args.get(filter + '.to')}"
            display_filters.append(
                f'{display_name}:  {request.args.get(filter + ".from")} TO {request.args.get(filter + ".to")}')
        elif type == "terms":
            # filters.append({})
            filters.append({"term": {filter + ".keyword": request.args.get(filter + ".key")}})
            applied_filters += f"&{filter}.key={request.args.get(filter + '.key')}"
            display_filters.append(f'{display_name}: {request.args.get(filter + ".key")}')
    print("Filters: {}".format(filters))

    return filters, display_filters, applied_filters


# Our main query route.  Accepts POST (via the Search box) and GETs via the clicks on aggregations/facets
@bp.route('/query', methods=['GET', 'POST'])
def query():
    opensearch = get_opensearch()  # Load up our OpenSearch client from the opensearch.py file.
    # Put in your code to query opensearch.  Set error as appropriate.
    error = None
    user_query = None
    query_obj = None
    display_filters = None
    applied_filters = ""
    filters = None
    sort = "_score"
    sortDir = "desc"
    if request.method == 'POST':  # a query has been submitted
        user_query = request.form['query']
        if not user_query:
            user_query = "*"
        sort = request.form["sort"]
        if not sort:
            sort = "_score"
        sortDir = request.form["sortDir"]
        if not sortDir:
            sortDir = "desc"
        query_obj = create_query(user_query, [], sort, sortDir)
    elif request.method == 'GET':  # Handle the case where there is no query or just loading the page
        user_query = request.args.get("query", "*")
        filters_input = request.args.getlist("filter.name")
        sort = request.args.get("sort", sort)
        sortDir = request.args.get("sortDir", sortDir)
        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)

        query_obj = create_query(user_query, filters, sort, sortDir)
    else:
        query_obj = create_query("*", [], sort, sortDir)

    print(json.dumps(query_obj))
    response = opensearch.search(
        body=query_obj,
        index='bbuy_products'
    )
    if len(response['hits']['hits']) == 0:
        query_obj = {"suggest": {
            "text": user_query,
            "simple_phrase": {
                "phrase": {
                    "field": "name.trigram",
                    "size": 3,
                    "gram_size": 3,
                    "direct_generator": [{
                        "field": "name.trigram",
                        "suggest_mode": "always"
                    }]

                }
            }
        }
        }
        response = opensearch.search(
            body=query_obj,
            index='bbuy_products'
        )

        print(response['suggest']['simple_phrase'][0]['options'])
    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir)
    else:
        redirect(url_for("index"))


def create_query(user_query, filters, sort="_score", sortDir="desc"):
    print("Query: {} Filters: {} Sort: {}".format(user_query, filters, sort))
    query_obj = {
        'size': 10,
        "sort": [
            {
                sort: {
                    "order": sortDir
                }
            }
        ],
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": {
                            "query_string": {
                                "query": user_query,
                                "fields": [
                                    "name.unique^20",
                                    "name^50",

                                    "shortDescription^20",
                                    "longDescription^10",
                                    "department"
                                ]
                            }
                        },
                        # "should": [
                        #     {
                        #         "multi_match": {
                        #             "query": "#$query##",
                        #             "fields": [
                        #                 "name.unique",
                        #                 "name"
                        #             ],
                        #             "type": "phrase",
                        #             "boost": 50
                        #         }
                        #     }],
                        "filter": filters
                    }
                },
                "boost_mode": "multiply",
                "score_mode": "avg",
                "functions": [
                    {
                        "field_value_factor": {
                            "field": "salesRankShortTerm",
                            "modifier": "reciprocal",
                            "missing": 1000000000
                        }
                    },
                    {
                        "field_value_factor": {
                            "field": "salesRankLongTerm",
                            "modifier": "reciprocal",
                            "missing": 1000000000
                        }
                    },
                    {
                        "field_value_factor": {
                            "field": "salesRankMediumTerm",
                            "modifier": "reciprocal",
                            "missing": 1000000000
                        }
                    }
                ]
            }
        },

        "aggs": {
            "regularPrice": {
                "range": {
                    "field": "regularPrice",
                    # "keyed": True,
                    "ranges": [
                        {
                            "key": "$",
                            "from": 0,
                            "to": 10
                        },
                        {
                            "key": "$$",
                            "from": 10,
                            "to": 50
                        },
                        {
                            "key": "$$$",
                            "from": 50,
                            "to": 300
                        },
                        {
                            "key": "$$$$",
                            "from": 300
                        }
                    ]
                }
            },
            "department": {
                "terms": {
                    "field": "department.keyword",
                    "size": 10,
                    "missing": "N/A",
                    "min_doc_count": 0
                }
            },
            "missing_images": {
                "missing": {
                    "field": "image.keyword"
                }
            }
            # "missing_images": {
            #     "filter": {
            #         "script": {
            #             "script": {
            #                 "lang": "painless",
            #                 "source":
            #                     """if (doc['image.keyword'].empty) return true; else return false; """}
            #         }
            #     }
            # }
        },
        "highlight": {
            "number_of_fragments": 1,
            "fragment_size": -1,
            "pre_tags": ['<span style="color:blue">'],
            "post_tags": ["</span>"],
            "fields": {
                "name": {},
                "shortDescription": {},
                "longDescription": {},
                "department": {}
            }
        }
    }
    # if filters:
    #     for fltr in filters:
    #         query_obj['query']['bool']['filter'].append(fltr)
    return query_obj


@bp.route('/quepid', methods=['POST'])
def search_proxy() -> dict:
    index_name = "bbuy_products"
    body = request.get_json(force=True)

    result = executor.search(
        index_name,
        body['from'],
        body['size'],
        body['explain'],
        body['_source'],
        {"query": body['query']} if body['query'] else None,
        None,
    )
    return result
