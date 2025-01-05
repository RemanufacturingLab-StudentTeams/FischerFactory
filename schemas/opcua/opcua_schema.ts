/**
 * This file contains a non-comprehensive, human-readable documentation of the OPC UA schema used for communication between
 * the PLC and the Raspberry Pi. It is written in TypeScript for convenience, and is not supposed to be
 * compiled to JavaScript.
 */

/**
 * OPC UA primary types. Note that these are not the same (but they are analogous) as the datatypes on the PLC.
 */
enum DataType {
    Boolean,
    Int16,
    Int32,
    Float,
    DateTime,
    String,
    Word // Is a bit string of 16 bits: W#16#0 to W#16#FFFF.
}

import { FixedLengthArray } from "../mqtt/mqtt_schema"

/**
 * Nodes that the PLC publishes to, and that the Raspberry Pi consumes.
 */ 
type gtyp_Interface_Dashboard = {
    Subscribe: {
        EnvironmentSensor: // For these nodes, the BME680 publishes its data over MQTT, which the relay publishes to OPC UA. Presumably, there are in gtyp_Interface_Subscribe_Dashboard because the Dashboard can subscribe to these. However, the Dashboard can also just subscribe to the original MQTT datasource directly, so this is, as far as I understand it, not necessary.
        {
            test: DataType.Boolean
            ldt_ts: DataType.DateTime
            r_t: DataType.Float // e.g., 19.8
            r_rt: DataType.Float // e.g., 22.95
            r_h: DataType.Float // e.g., 51.9
            r_rh: DataType.Float // e.g., 42.64
            r_p: DataType.Float // e.g., 1018.1
            i_iaq: DataType.Int16 // e.g., 59
            i_aq: DataType.Int16 // e.g., 3
            di_gr: DataType.Int32 // e.g., 919245
        }
        BrightnessSensor: // For these nodes, the Photoresistor publishes its data over MQTT, which the relay publishes to OPC UA. Presumably, there are in gtyp_Interface_Subscribe_Dashboard because the Dashboard can subscribe to these. However, the Dashboard can also just subscribe to the original MQTT datasource directly, so this is, as far as I understand it, not necessary.
        {
            ldt_ts: DataType.DateTime
            r_br: DataType.Float // e.g., 88.0
            i_ldr: DataType.Int16 // e.g., 1804
        }
        CameraPicture: // For these nodes, the Camera publishes its data over MQTT, which the relay publishes to OPC UA. Presumably, there are in gtyp_Interface_Subscribe_Dashboard because the Dashboard can subscribe to these. However, the Dashboard can also just subscribe to the original MQTT datasource directly, so this is, as far as I understand it, not necessary.
        {
            ldt_ts: DataType.DateTime
            s_data: DataType.String
        }
        PosPanTiltUnit:
        {
            ldt_ts: DataType.DateTime
            r_pan: DataType.Float
            r_tilt: DataType.Float
        }
        AlertMessage:
        {
            ldt_ts: DataType.DateTime
            s_id: DataType.String
            s_data: DataType.String
            i_code: DataType.Int16
        }
        Broadcast:
        {
            ldt_ts: DataType.DateTime
            di_hardwareId: DataType.Int32
            di_hardwareModel: DataType.Int32
            s_softwareName: DataType.String
            di_softwareVersion: DataType.Int32
            s_message: DataType.String
        }

        State_HBW: typ_State_Client,
        State_VGR: typ_State_Client,
        State_MPO: typ_State_Client,
        State_SLD: typ_State_Client,
        State_DSI: typ_State_Client,
        State_DSO: typ_State_Client,

        State_Track:{ //node(s) used for tracking feature
            track_puck: DataType.String
        }

        State_Order:
        {
            ldt_ts: DataType.DateTime
            s_state: DataType.String // 'WAITING_FOR_ORDER' | 'ORDERED' | 'SHIPPED' | 'IN_PROCESS'
            s_type: DataType.String // 'RED' | 'BLUE' | 'WHITE'
        }
        State_NFC_Device:
        {
            ldt_ts: DataType.DateTime
            Workpiece: typ_Workpiece
            History:
            {
                ldt_ts: DataType.DateTime
                i_code: DataType.Int16
            }
        }

        Stock_HBW:
        {
            ldt_ts: DataType.DateTime
            StockItem: typ_StockItem,
            s_location: DataType.String
        }
    },

    // Nodes that the Raspberry Pi publishes on.
    Publish: {
        ldt_AcknowledgeButton: DataType.DateTime
        ConfigRateEnvironmentSensor:
        {
            ldt_ts: DataType.DateTime
            di_period: DataType.Int32
        }
        ConfigRateBrightnessSensor:
        {
            ldt_ts: DataType.DateTime
            x_on: DataType.Boolean
            i_fps: DataType.Int16
        }
        ConfigRateCameraPicture:
        {
            ldt_ts: DataType.DateTime
            di_period: DataType.Int32
        }
        PosPanTiltUnit:
        {
            ldt_ts: DataType.DateTime
            s_cmd: DataType.String
            i_degree: DataType.Int16
        }
        OrderWorkpieceButton:
        {
            ldt_ts: DataType.DateTime
            s_type: DataType.String
            Workpiece_Parameters:
            {
                DoOven: DataType.Boolean
                OvenTime: DataType.Int32
                DoSaw: DataType.Boolean
                SawTime: DataType.Int32
            }
        }
        ActionButtonNFCModule:
        {
            ldt_ts: DataType.DateTime
            s_cmd: DataType.String
        }
    }
}

type gtyp_VGR = {
    x_Start_Park_Position: DataType.Boolean
    x_Park_Position_Reached: DataType.Boolean
    x_NFC_Start_First: DataType.Boolean
    x_NFC_Start: DataType.Boolean
    x_NFC_Completed: DataType.Boolean
    x_HBW_Storage: DataType.Boolean
    x_HBW_Outsource: DataType.Boolean
    s_HBW_Outsource_Typ: DataType.String
    x_HBW_Discards: DataType.Boolean
    x_HBW_PickedUp: DataType.Boolean
    x_MPO_Req_Discard: DataType.Boolean
    x_MPO_Discards: DataType.Boolean
    x_Ready_For_Outsource: DataType.Boolean
    x_State_Process: DataType.Boolean
    x_Workpiece_NiO: DataType.Boolean
    horizontal_Axis: typ_Axis
    vertical_Axis: typ_Axis
    rotate_Axis: typ_Axis
    Workpiece: typ_Workpiece
    Worpiece_Parameters: typ_Workpiece_Parameters
    History: FixedLengthArray<typ_History, 20>
    di_Pos_DSI_horizontal: DataType.Int32
    di_Pos_DSI_Collect_vertical: DataType.Int32
    di_Pos_DSI_Discard_vertical: DataType.Int32
    di_Offset_Pos_DSI_NFC_vertical: DataType.Int32
    di_Pos_DSI_rotate: DataType.Int32
    di_Pos_DSO_horizontal: DataType.Int32
    di_Pos_DSO_Collect_vertical: DataType.Int32
    di_Pos_DSO_Discard_vertical: DataType.Int32
    di_Offset_Pos_DSO_vertical: DataType.Int32
    di_Pos_DSO_rotate: DataType.Int32
    di_Pos_Color_horizontal: DataType.Int32
    di_Pos_Color_vertical: DataType.Int32
    di_Pos_Color_rotate: DataType.Int32
    di_Pos_NFC_horizontal: DataType.Int32
    di_Pos_NFC_vertical: DataType.Int32
    di_Pos_NFC_rotate: DataType.Int32
    di_Pos_MPO_horizontal: DataType.Int32
    di_Pos_MPO_vertical: DataType.Int32
    di_Offset_Pos_MPO_vertical: DataType.Int32
    di_Pos_MPO_rotate: DataType.Int32
    di_Pos_Free_MPO_Min_rotate: DataType.Int32
    di_Pos_Free_MPO_Max_rotate: DataType.Int32
    di_Pos_Free_MPO_horizontal: DataType.Int32
    di_Pos_HBW_horizontal: DataType.Int32
    di_Offset_Pos_HBW_horizontal: DataType.Int32
    di_Pos_HBW_Collect_vertical: DataType.Int32
    di_Pos_HBW_Discard_vertical: DataType.Int32
    di_Offset_Pos_HBW_vertical: DataType.Int32
    di_Pos_HBW_rotate: DataType.Int32
    di_Pos_NiO_horizontal: DataType.Int32
    di_Pos_NiO_vertical: DataType.Int32
    di_Pos_NiO_rotate: DataType.Int32
    di_Pos_SLD_Blue_horizontal: DataType.Int32
    di_Pos_SLD_Blue_vertical: DataType.Int32
    di_Pos_SLD_Blue_rotate: DataType.Int32
    di_Pos_SLD_Red_horizontal: DataType.Int32
    di_Pos_SLD_Red_vertical: DataType.Int32
    di_Pos_SLD_Red_rotate: DataType.Int32
    di_Pos_SLD_White_horizontal: DataType.Int32
    di_Pos_SLD_White_vertical: DataType.Int32
    di_Pos_SLD_White_rotate: DataType.Int32
    di_Pos_Park_horizontal: DataType.Int32
    di_Pos_Park_vertical: DataType.Int32
    di_Pos_Park_rotate: DataType.Int32
    x_Ready_For_Order: DataType.Boolean
}

type gtyp_MPO = {
    x_Start_Park_Position: DataType.Boolean
    x_Park_Position_Reached: DataType.Boolean
    x_Discard_Ready: DataType.Boolean
    x_MPO_Discards_Accepted: DataType.Boolean
    x_Error: DataType.Boolean
    s_ErrorMessage: DataType.String
    i_PWM_TurnTable: DataType.Int16
    i_PWM_Vacuum: DataType.Int16
    Workpiece: typ_Workpiece
    Workpiece_Parameters: typ_Workpiece_Parameters
    History: FixedLengthArray<typ_History, 20>
}

type gtyp_SSC = {
    x_Start_Park_Position: DataType.Boolean
    x_Park_Position_Reached: DataType.Boolean
    x_Error: DataType.Boolean
    di_Pos_Centre_Horizontal: DataType.Int32
    di_Pos_Centre_Vertical: DataType.Int32
    di_Pos_HBW_Horizontal: DataType.Int32
    di_Pos_HBW_Vertical: DataType.Int32
    di_Pos_Park_Horizontal: DataType.Int32
    di_Pos_Park_Vertical: DataType.Int32
    w_Threshold_White_Red: DataType.Word
    w_Threshold_Red_Blue: DataType.Word
    Horizontal_Axis: typ_Axis
    Vertical_Axis: typ_Axis
    Workpiece: typ_Workpiece
    History: FixedLengthArray<typ_History, 20>
}

type gtyp_HBW = {
    x_Start_Park_Position: DataType.Boolean
    x_Park_Position_Reached: DataType.Boolean
    x_HBW_PickedUp_Accepted: DataType.Boolean
    x_HBW_Discards_Accepted: DataType.Boolean
    x_HBW_PickUp_Ready: DataType.Boolean
    x_HBW_Container_Available: DataType.Boolean
    x_Error: DataType.Boolean
    s_ErrorMessage: DataType.String
    di_PosBelt_Horizontal: DataType.Int32
    di_PosBelt_Vertical: DataType.Int32
    di_Offset_Pos_Belt_Vertical: DataType.Int32
    di_PosRack_A1_Horizontal: DataType.Int32
    di_PosRack_A1_Vertical: DataType.Int32
    di_PosRack_B2_Horizontal: DataType.Int32
    di_PosRack_B2_Vertical: DataType.Int32
    di_PosRack_C3_Horizontal: DataType.Int32
    di_PosRack_C3_Vertical: DataType.Int32
    di_Offset_Pos_Rack_Vertical: DataType.Int32
    di_Pos_Park_Horizontal: DataType.Int32
    di_Pos_Park_Vertical: DataType.Int32
    i_PWM_ConveyorBelt: DataType.Int16
    i_PWM_Cantilever: DataType.Int16
    Workpiece: typ_Workpiece
    History: FixedLengthArray<typ_History, 20> // [1..20]
    Rack_Pos: {
        di_PosRack_Horizontal: DataType.Int32
        di_PosRack_Vertical: DataType.Int32
    }[][] // [1..3, 1..3]
    Rack_Workpiece: typ_Workpiece[][] // [1..3, 1..3]
    Rack_History: typ_Rack_History[][] // [1..3, 1..3]
    Horizontal_Axis: typ_Axis
    Vertical_Axis: typ_Axis
    i_Red_Available: DataType.Int16
    i_Blue_Available: DataType.Int16
    i_White_Available: DataType.Int16
    di_Offset_Actual_Pickup: DataType.Int32
}

type gtyp_SLD = {
    x_Error: DataType.Boolean
    s_ErrorMessage: DataType.String
    i_CounterValue_Blue: DataType.Int16
    i_CounterValue_White: DataType.Int16
    i_CounterValue_Red: DataType.Int16
    i_Counter_Actual: DataType.Int16
    w_Threshold_White_Red: DataType.Word
    w_Threshold_Red_Blue: DataType.Word
    Workpiece: typ_Workpiece
    History: FixedLengthArray<typ_History[], 20> // [1..20]
}

type gtyp_Interface_TXT_Controler = {
    Subscribe: {
        State_NFC_Device: {
            ldt_ts: DataType.DateTime,
            Workpiece: typ_Workpiece,
            History: FixedLengthArray<typ_History[], 20> // [1..20]
        }
    },

    Publish: {
        ActionButtonNFCModule: {
            ldt_ts: DataType.DateTime,
            s_cmd: DataType.String,
            Workpiece: typ_Workpiece,
            History: FixedLengthArray<typ_History[], 20> // [1..20]
        }
    }
}

type Queue = {
    x_Queue_Full: DataType.Boolean
    i_Queue_Index: DataType.Int16 // index where the next element will be written (so 0 if the queue is empty)
    Queue: FixedLengthArray<{
        ldt_ts: DataType.DateTime
        s_type: 'RED' | 'WHITE' | 'BLUE'
        Workpiece_Parameters: typ_Workpiece_Parameters
    }, 7>
}

type typ_State_Client = {
    ldt_ts: DataType.DateTime
    x_sensor_oven: DataType.Boolean
    s_station: DataType.String
    i_code: DataType.Int16
    s_description: DataType.String
    x_active: DataType.Boolean
    s_target: DataType.String
    x_error: DataType.Boolean
    s_errorMessage: DataType.String
    Workpiece: typ_Workpiece
}

type typ_StockItem = typ_Workpiece[][] // [1..3, 1..3]

type gtyp_Setup = {

    r_Version_SPS: {
        // PLC Version
        datatype: DataType.Float
    },

    x_Fill_Rack_HBW: {
        datatype: DataType.Boolean
    },

    x_Start_TON_Fill_HBW: {
        datatype: DataType.Boolean
    },

    x_Clean_Rack_HBW: {
        datatype: DataType.Boolean
    },

    x_AcknowledgeButton: {
        // Acknowledge Errors
        datatype: DataType.Boolean
    },

    x_Park_Position: {
        // Move to park position 
        datatype: DataType.Boolean
    }
}

type typ_Workpiece = {

    // Unique id of Workpiece
    s_id: DataType.String, // e.g., '04f8a942ef6c80' or '0425a942ef6c80'

    // Type of workpiece ("RED"/"WHITE"/"BLUE")
    s_type: DataType.String,

    // State of workpiece ("RAW"/"PROCESSED"). Not really relevant since addind Workpiece_States
    s_state: DataType.String

    // Possible states of workpiece and timestamps
    Workpiece_States: typ_Workpiece_States,
    Workpiece_Parameters: typ_Workpiece_Parameters,
}

type typ_Workpiece_Parameters = {
    DoOven: DataType.Boolean
    OvenTime: DataType.DateTime
    DoSaw: DataType.Boolean
    SawTime: DataType.DateTime
}

type typ_Workpiece_States = {
    x_inOven: DataType.Boolean,
    ldt_Oven: DataType.DateTime,
    x_ColorObserved: DataType.Boolean,
    s_ObservedColor: DataType.String,
    w_ObservedColorValue: DataType.Word,
    ldt_Color: DataType.DateTime,
    x_atSaw: DataType.DateTime,
    ldt_Saw: DataType.DateTime,
    x_onTransportBelt: DataType.Boolean,
    ldt_TransportBelt: DataType.DateTime
}

type typ_Axis = {
    x_Start_Positioning: DataType.Boolean
    x_Reference: DataType.Boolean
    x_Referenced: DataType.Boolean
    x_Position_Reached: DataType.Boolean
    di_Target_Position: DataType.Int32
    di_Increment: DataType.Int32
    di_Actual_Position: DataType.Int32
    i_PWM: DataType.Int16
    Config: typ_Axis_Data
}

type typ_Axis_Data = {
    di_Pos_Soft_Switch: DataType.Int32
    di_Neg_Soft_Switch: DataType.Int32
    di_Ref_Pos: DataType.Int32
    di_Loop_Value: DataType.Int32
    di_Pos_Window: DataType.Int32
}

type typ_History = {
    ldt_ts: DataType.DateTime
    i_code: DataType.Int16
}

type typ_Rack_History = FixedLengthArray<typ_History[], 20> // Max size 20