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
        'setup': 'relay/f/setup',
        'turtlebot_current_state': 'Turtlebot/CurrentState'
    },
    'factory-data': {
        'state_sld': 'relay/f/i/state/sld'
    },
    'dashboard-customer': {
        'queue': 'relay/f/queue',
        'state_order': 'relay/f/i/order',
        'tracking': 'relay/f/i/track',
        'place_order': 'relay/f/o/order',
    },
    'global': { # every page
        'stock' : 'relay/f/i/stock'
    }
}

