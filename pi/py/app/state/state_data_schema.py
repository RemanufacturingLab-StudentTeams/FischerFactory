_data: dict[str, dict[str, str]] = {
# """Data that will be fetched per page by the PageStateManager. The data will be made available for polling (or, in the future, pushing with WebSockets) using the given key.

#     Format:
#         {
#             '`page-pathname`' : {
#                 '`key`': `topic/name`
#             }
#         }
# """    

    'factory-overview': { # yes, using a hyphen as a delimiter, not an underscore, because it has to correspond with the page URLs. 
        'plc_version': 'f/setup/versionSPS',
        'turtlebot_current_state': 'Turtlebot/CurrentState'
    },
    'factory-data': {
        'state_sld': 'f/i/state/sld'
    },
    'dashboard-customer': {
        'queue': 'f/queue/',
        'state_order': 'f/i/order',
        'tracking': 'f/i/track',
        'place_order': 'f/o/order',
        'queue': 'f/queue'
    },
    'global': { # every page
        'stock' : 'f/i/stock'
    }
}

