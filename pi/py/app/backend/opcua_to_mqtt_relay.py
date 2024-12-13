from backend import RelayTopic, RelaySubNode, RelayHistoryNode

# helper variables to make the code shorter
_dashboard_sub = 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe".'
_txt_sub = 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe".' # yeah, it's misspelled, blame fischertechnik
_txt_pub = 'ns=3;s="gtyp_Interface_TXT_Controler"."Publish".'
_station_fields = ['i_code', 'ldt_ts', 's_description', 's_station', 's_target', 'x_active', 'x_error', 's_errorMessage'] # OPCUA fields that are common for every station (DSI, DSO, MPO, VGR, HBW, SLD)

class Relay:
    """Translates OPCUA Node information to MQTT topics. This behaviour is necessary for the Influx DB on the server to work, and it is used by the dashboard internally.
    """
    
    
    relay_map: list[RelayTopic] = [
        # A dict with the keys being the MQTT topics that the Relay will publish on, and the values being dicts that represent the payload it will send. 
        # The Relay will follow the structure of the dicts to determine its payload. The keys will become the payload keys, and the node IDs are the nodes it will listen to.
        # Lastly, per topic it can have a key called `relay_interval` which determines how frequently it will relay, in seconds. Default is 1s. 
        
        # *NOTE: the Relay will only relay if the new value is different from the old value. It will also relay all values once when the application is started.* 
        
        # alert message
        RelayTopic({'f/i/alert': _dashboard_sub + '."AlertMessage"'},[
            'i_code', 's_data', 's_id', 'ldt_ts'
        ]),
        
        # stations
        RelayTopic({'f/i/state/dsi': _dashboard_sub + '"State_DSI"'},_station_fields),
        RelayTopic({'f/i/state/dso': _dashboard_sub + '"State_DSO"'},_station_fields),
        RelayTopic({'f/i/state/mpo': _dashboard_sub + '"State_MPO"'},_station_fields + [
            RelaySubNode('"Workpiece"."Workpiece_States"', [
                'x_inOven', 'ldt_Oven', 'x_atSaw', 'ldt_Saw'
            ]),
            RelaySubNode('"Workpiece"."Workpiece_Parameters"', [
                {'setOvenTime': 'OvenTime'}, {'setSawTime': 'SawTime'}
            ]),
            RelaySubNode('"Workpiece"', [
                {'workpieceId': 's_id'}, {'workpieceType': 's_type'}
            ])
        ]),
        RelayTopic({'f/i/state/sld': _dashboard_sub + '"State_SLD"'},_station_fields + [
            RelaySubNode('"Workpiece"."Workpiece_States"',[
                'x_ColorObserved', 'ldt_Color', 's_ObservedColor', 'x_onTransportBelt', 'ldt_TransportBelt'
            ]),
            RelaySubNode('"Workpiece"', [
                {'workpieceId': 's_id'}, {'workpieceType', 's_type'}
            ])
        ]),
        RelayTopic({'f/i/state/vgr': _dashboard_sub + '"State_VGR"'},_station_fields),
        RelayTopic({'f/i/state/hbw': _dashboard_sub + '"State_HBW"'}, _station_fields),
    
        # ptu
        RelayTopic({'i/ptu/pos': _dashboard_sub + '"PosPanTiltUnit"'}, [
            'r_pan', 'r_tilt', 'ldt_ts'
        ]),
        
        # nfc reader
        RelayTopic({'fl/o/nfc/ds': _txt_pub + '"ActionButtonNFCModule"'}, [
            'ldt_ts', 's_cmd',
            RelaySubNode('"Workpiece"', [
                's_id', 's_state', 's_type'
            ]),
            RelayHistoryNode(9)
        ]),
        
        # order
        RelayTopic({'f/i/order', _dashboard_sub + '"State_Order"'}, [
            's_state', 's_type', 'ldt_ts'
        ]),
        
        # stock
        RelayTopic({'f/i/stock', _dashboard_sub + '"Stock_HBW"'}, [
            's_location', 'ldt_ts'
        ]
                   
                   !TODO: figure out how to do RelayArrays)
    ]
    