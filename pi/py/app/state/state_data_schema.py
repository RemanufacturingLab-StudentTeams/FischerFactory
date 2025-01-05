from .state_data_sources import MQTTSource, OPCUASource

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
        'state_order': '',
        'monitor': {
            'state_order_ldt_ts': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_Order"."ldt_ts"'),
            'state_order_s_state': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_Order"."s_state"'),
            'state_order_s_type': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_Order"."s_type"'),
            'tracking': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_Track"."track_puck"')
        } | {   
            f'queue_[{n}]_{e}': OPCUASource(f'ns=3;s="Queue"."Queue"[{n}]."{e}"')
            for n in range(7)
            for e in ['ldt_ts', 's_type']
        } | {
            f'queue_[{n}]_wparams_{e}': OPCUASource(f'ns=3;s="Queue"."Queue"[{n}]."Workpiece_Parameters"."{e}"')
            for n in range(7)
            for e in ['DoOven', 'OvenTime', 'DoSaw', 'SawTime']
        },
        'user': {
            's_type': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."s_type"'),
            'order_oven_time': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."OvenTime"'),
            'order_do_oven': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."DoOven"'),
            'order_saw_time': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."SawTime"'),
            'order_do_saw': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."DoSaw"'),
            'order_ldt_ts': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."ldt_ts"'),
        }
    },
    'global': { # every page
        'hydrate': {
        },
        'monitor': {
            f'rack_workpiece_[{x},{y}]_{e}': OPCUASource(f'ns=3;s="gtyp_HBW"."Rack_Workpiece"[{x},{y}]."{e}"')
            for x in range(3) 
            for y in range(3) 
            for e in ['s_id', 's_state', 's_type']
        } | {}
    }
}

