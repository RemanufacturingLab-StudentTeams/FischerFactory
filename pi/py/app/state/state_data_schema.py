from .state_data_sources import MQTTSource, OPCUASource

_data: dict[str, dict[str, dict[str, MQTTSource | OPCUASource]]] = {
# """Data that will be fetched per page by the PageStateManager.

#     Format:
#         {
#             '`page-pathname`' : {
#                 'hydrate': {
#                     '`key`': OPCUASource | MQTTSource
#                 },
#                 'monitor': {
#                     '`key`': OPCUASource | MQTTSource
#                 },
#                 'user': {
#                     '`key`': OPCUASource | MQTTSource
#                 }
#             }
#         }
# """    

    'factory-overview': { # yes, using a hyphen as a delimiter, not an underscore, because it has to correspond with the page URLs. 
        'hydrate': {
            'plc_version': OPCUASource('ns=3;s="gtyp_Setup"."r_Version_SPS"')
        },
        'monitor': {
            f'rack_workpiece_[{x},{y}]_{e}': OPCUASource(f'ns=3;s="gtyp_HBW"."Rack_Workpiece"[{x},{y}]."{e}"')
            for x in range(3) 
            for y in range(3) 
            for e in ['s_id', 's_state', 's_type']
        } | {
            'turtlebot_current_state': MQTTSource('Turtlebot/CurrentState')
        },
        'user': {
            'clean_rack': OPCUASource('ns=3;s="gtyp_Setup"."x_Clean_Rack_HBW"')
        }
    },
    'factory-data': {
        'hydrate': {
            
        },
        'monitor': {
        'state_sld': MQTTSource('f/i/state/sld')
        },
        'user': {
            
        }
    },
    'dashboard-customer': {
        'hydrate': {
            
        },
        'monitor': {
            f'rack_workpiece_[{x},{y}]_{e}': OPCUASource(f'ns=3;s="gtyp_HBW"."Rack_Workpiece"[{x},{y}]."{e}"')
            for x in range(3) 
            for y in range(3) 
            for e in ['s_id', 's_state', 's_type']
        } | {
            'queue_full': OPCUASource('ns=3;s="Queue"."x_Queue_Full"'),
            'queue_index': OPCUASource('ns=3;s="Queue"."i_Queue_Index"')
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
    }
}

