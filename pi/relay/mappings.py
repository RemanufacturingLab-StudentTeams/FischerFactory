from .types import Mapping, SpecialRuleOPCUA

"""Mappings for the Relay. It will relay the FROM node/topic to the TO node/topic.
    - If the node has descendants (direct or indirect children), it will relay the descendants as well, keeping the same nested structure. For example, `FROM="gtyp_Interface_Dashboard"."Subscribe"` will also relay `"gtyp_Interface_Dashboard"."Subscribe"."State_HBW"."x_sensor_oven"`.
    - If it is a MQTT->OPCUA mapping, it will NOT apply recursive subscribe. The reason for that is because MQTT does not implement a way to browse child topics from a topic. What that means is that for an MQTT->OPCUA mapping, the target node must be a single leaf node.
    - It automatically converts MQTT format names (e.g.: `errorMessage`) to OPCUA format names (`s_ErrorMessage`)
    - There are nodes and topic names that don't follow convention, in which case there are SpecialRuleOPCUA types. It will internally interpret and process these nodes based on their `MEANS` argument.
    - The default OPCUA namespace is 3. This can be given as an argument for different namespaces.
    
    *This file can be edited, and the program should work all the same. To see changes take effect, rerun the relay program.*
    *Note: the nodeID and topic in the FROM parameter should exist. *
"""

mappings = [
    # PLC -> Dashboard
    Mapping(FROM='"gtyp_Interface_Dashboard"."Subscribe"', TO='f/i'),
    Mapping(FROM='"gtyp_Setup"', TO='f/setup'),
    Mapping(FROM='"gtyp_HBW"', TO='f/setup'),
    Mapping(FROM='"Queue"', TO='f/queue'),
    # Dashboard -> PLC
    Mapping(FROM='f/o/state/ack', TO='"gtyp_Interface_Dashboard"."Publish"."ldt_AcknowledgeButton"'),
    Mapping(FROM='f/o/order', TO='"gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"'),
    # Camera -> PLC
    Mapping(FROM='o/ptu', TO='"gtyp_Interface_Dashboard"."Publish"."PosPanTiltUnit"'),
    # Dashboard -> PLC (Dashboard sends NFC commands to the PLC)
    Mapping(FROM='f/o/nfc/ds', TO='"gtyp_Interface_Dashboard"."Publish"."ActionButtonNFCModule"'),
    # PLC -> NFC Reader (PLC then sends the commands to the NFC reader)
    Mapping(FROM='"gtyp_Interface_TXT_Controler"."Publish"."ActionButtonNFCModule"', TO='fl/o/nfc/ds'),
    # NFC Reader -> PLC (NFC reader responds to PLC with read value)
    Mapping(FROM='fl/i/nfc/ds', TO='"gtyp_Interface_Dashboard"."Publish"."ActionButtonNFCModule"'),
    # Sensors -> PLC (presumably, the reason it says "Subscribe" even though it is PLC *ingress*, is because it is considered Dashboard input?)
    Mapping(FROM='i/cam', TO='"gtyp_Interface_Dashboard"."Subscribe"."CameraPicture"'),
    Mapping(FROM='i/bme680', TO='"gtyp_Interface_Dashboard"."Subscribe"."EnvironmentSensor"'),
    Mapping(FROM='i/ldr', TO='"gtyp_Interface_Dashboard"."Subscribe"."BrightnessSensor"'),    
]

special_rules = [
    SpecialRuleOPCUA(ORIGINAL='track_puck', MEANS='s_trackPuck'),
    SpecialRuleOPCUA(ORIGINAL='DoOven', MEANS='s_doOven'),
    SpecialRuleOPCUA(ORIGINAL='OvenTime', MEANS='s_ovenTime'),
    SpecialRuleOPCUA(ORIGINAL='DoSaw', MEANS='s_doSaw'),
    SpecialRuleOPCUA(ORIGINAL='SawTime', MEANS='s_doOven'),
    SpecialRuleOPCUA(ORIGINAL='AlertMessage', MEANS='"Alert"'),
    SpecialRuleOPCUA(ORIGINAL='PosPanTiltUnit', MEANS='"Ptu"'),
    SpecialRuleOPCUA(ORIGINAL='State_HBW', MEANS='"State"."Hbw"'),
    SpecialRuleOPCUA(ORIGINAL='State_VGR', MEANS='"State"."Vgr"'),
    SpecialRuleOPCUA(ORIGINAL='State_MPO', MEANS='"State"."Mpo"'),
    SpecialRuleOPCUA(ORIGINAL='State_SLD', MEANS='"State"."Sld"'),
    SpecialRuleOPCUA(ORIGINAL='State_DSI', MEANS='"State"."Dsi"'),
    SpecialRuleOPCUA(ORIGINAL='State_DSO', MEANS='"State"."Dso"'),
    SpecialRuleOPCUA(ORIGINAL='State_Track', MEANS='"Track"'),
    SpecialRuleOPCUA(ORIGINAL='State_Order', MEANS='"Order"'),
    SpecialRuleOPCUA(ORIGINAL='State_NFC_Device', MEANS='"Nfc"'),
    SpecialRuleOPCUA(ORIGINAL='Stock_HBW', MEANS='"Stock"'),
]
