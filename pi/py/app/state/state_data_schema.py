from state import state_data_sources as src

_data = {
"""Data that will be fetched per page by the PageStateManager.

    Format:
        {
            '`page-pathname`' : {
                'hydrate': {
                    '`key`': src.OPCUASource | MQTTSource
                },
                'monitor': {
                    '`key`': src.OPCUASource | MQTTSource
                },
                'user': {
                    '`key`': src.OPCUASource | MQTTSource
                }
            }
        }
"""    

    'factory-overview': { # yes, using a hyphen as a delimiter, not an underscore, because it has to correspond with the page URLs. 
        'hydrate': {
            'plc_version': src.OPCUASource('ns=3;s="gtyp_Setup"."r_Version_SPS"')
        },
        'monitor': {
            'turtlebot_current_state': src.MQTTSource('Turtlebot/CurrentState')
        },
        'user': {
            'clean_rack': src.OPCUASource('ns=3;s="gtyp_Setup"."x_Clean_Rack_HBW"')
        }
    },
    'factory-data': {
        'hydrate': {
            
        },
        'monitor': {
            'state_sld': src.MQTTSource('f/i/state/sld')
        },
        'user': {
            
        }
    },
    'dashboard-customer': {
        'hydrate': {
            
        },
        'monitor': {
            f'rack_workpiece_[{x},{y}]_{e}': src.OPCUASource(f'ns=3;s="gtyp_HBW"."Rack_Workpiece"[{x},{y}]."{e}"')
            for x in range(3) 
            for y in range(3) 
            for e in ['s_id', 's_state', 's_type']
        },
        'user': {
            's_type': src.OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."s_type"'),
            'order_oven_time': src.OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."OvenTime"'),
            'order_do_oven': src.OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."DoOven"'),
            'order_saw_time': src.OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."SawTime"'),
            'order_do_saw': src.OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."DoSaw"'),
            'order_ldt_ts': src.OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."ldt_ts"'),
        }
    }
}