const schema = {
    gtyp_Setup: {
        // Check if Fill is allowed
        x_Start_TON_Fill_HBW:
        {
            nodeId: 'ns=3;s="gtyp_Setup"."x_Start_TON_Fill_HBW"',
            datatypeName: 'Boolean'
        },

        // Check PLC Version
        r_Version_SPS:
        {
            name: "",
            nodeId: 'ns=3;s="gtyp_Setup"."r_Version_SPS"',
            datatypeName: 'Float'
        },

        x_Clean_Rack_HBW:
        {
            nodeId: 'ns=3;s="gtyp_Setup"."x_Clean_Rack_HBW"',
            datatypeName: 'Boolean'
        },
        x_Fill_Rack_HBW:
        {
            nodeId: 'ns=3;s="gtyp_Setup"."x_Fill_Rack_HBW"',
            datatypeName: 'Boolean'
        },
        x_AcknowledgeButton:
        // Acknowledge Errors
        {
            nodeId: 'ns=3;s="gtyp_Setup"."x_AcknowledgeButton"',
            datatypeName: 'Boolean'
        },

        x_Park_Position:
        // Move to park position 
        {
            nodeId: 'ns=3;s="gtyp_Setup"."x_Park_Position"',
            datatypeName: 'Boolean'
        }
    },

    gtyp_Interface_Dashboard: {
        subscribe: {
            // Alert Message - from OPC UA to MQTT
            // Server listens to this node
            alertMessage: {
                ldt_ts:
                {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."AlertMessage"."ldt_ts"',
                    datatypeName: 'DateTime'
                },

                // The following nodes are polled when a timestamp is published to 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."AlertMessage"."ldt_ts"'. 
                // The data is then sent over MQTT on 'f/i/alert'. 
                i_code:
                {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."AlertMessage"."i_code"',
                    datatypeName: 'Int16'
                },
                s_data:
                {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."AlertMessage"."s_data"',
                    datatypeName: 'String'
                },
                s_id:
                {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."AlertMessage"."s_id"',
                    datatypeName: 'String'
                }
            },

            State_Track:{ //Nodes for tracking pucks feature
                track_puck: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_Track"."track_puck"',
                    datatypeName: 'String'
                }
            },


            // These nodes are used to poll the state of the DSI from the PLC. The data is then sent over MQTT to the broker.
            state_DSI: {
                // This node is subscribed to to get the State of the DSI. When the server starts, it also publishes on this node to trigger the polling process.
                ldt_ts: {
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_DSI"."ldt_ts"',
                    datatypeName: 'DateTime'
                },

                // When data is published to ldt_ts, these nodes (and ldt_ts as well) are polled. Then the data is published to 'f/i/state/dsi'.
                i_code: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_DSI"."i_code"',
                    datatypeName: 'Int16'
                },

                s_description: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_DSI"."s_description"',
                    datatypeName: 'String'
                },

                s_station: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_DSI"."s_station"',
                    datatypeName: 'String'
                },

                s_target: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_DSI"."s_target"',
                    datatypeName: 'String'
                },

                x_active: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_DSI"."x_active"',
                    datatypeName: 'Bool'
                }
            },

            state_DSO: {
                // This node is subscribed to to get the State of the DSO. When the server starts, it also publishes on this node to trigger the polling process.
                ldt_ts: {
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_DSO"."ldt_ts"',
                    datatypeName: 'DateTime'
                },

                // When data is published to ldt_ts, these nodes (and ldt_ts as well) are polled. Then the data is published to 'f/i/state/dso'.
                i_code: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_DSO"."i_code"',
                    datatypeName: 'Int16'
                },

                s_description: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_DSO"."s_description"',
                    datatypeName: 'String'
                },

                s_station: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_DSO"."s_station"',
                    datatypeName: 'String'
                },

                s_target: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_DSO"."s_target"',
                    datatypeName: 'String'
                },

                x_active: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_DSO"."x_active"',
                    datatypeName: 'Bool'
                }
            },

            state_MPO: {
                i_code: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."i_code"',
                    datatypeName: 'Int16'
                },
                ldt_ts: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."ldt_ts"',
                    datatypeName: 'DateTime'
                },
                s_description: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."s_description"',
                    datatypeName: 'String'
                },
                s_station: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."s_station"',
                    datatypeName: 'String'
                },
                s_target: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."s_target"',
                    datatypeName: 'String'
                },
                x_active: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."x_active"',
                    datatypeName: 'Bool'
                },

                workpiece: {
                    workpiece_states: {
                        //WORKPIECE STATES
                        x_inOven:
                        //In Oven
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."Workpiece"."Workpiece_States"."x_inOven"',
                            datatypeName: 'Bool'
                        },
                        ldt_Oven:
                        //Oven timestamp
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."Workpiece"."Workpiece_States"."ldt_Oven"',
                            datatypeName: 'DateTime'
                        },
                        x_atSaw:
                        //At saw
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."Workpiece"."Workpiece_States"."x_atSaw"',
                            datatypeName: 'Bool'
                        },
                        ldt_Saw:
                        //Saw timestamp
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."Workpiece"."Workpiece_States"."ldt_Saw"',
                            datatypeName: 'DateTime'
                        },
                        s_id:
                        //Workpiece
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."Workpiece"."s_id"',
                            datatypeName: 'String'
                        },
                        s_type:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."Workpiece"."s_type"',
                            datatypeName: 'String'
                        },
                        //parameters
                        workpiece_parameters: {
                            ovenTime:
                            {
                                name: "",
                                nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."Workpiece"."Workpiece_Parameters"."OvenTime"',
                                datatypeName: 'DateTime'
                            },
                            sawTime: {
                                name: "",
                                nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."Workpiece"."Workpiece_Parameters"."SawTime"',
                                datatypeName: 'DateTime'
                            }
                        }
                    }
                }
            },

            state_HBW: {
                i_code: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_HBW"."i_code"',
                    datatypeName: 'Int16'
                },
                ldt_ts: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_HBW"."ldt_ts"',
                    datatypeName: 'DateTime'
                },
                s_description: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_HBW"."s_description"',
                    datatypeName: 'String'
                },
                s_station: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_HBW"."s_station"',
                    datatypeName: 'String'
                },
                s_target: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_HBW"."s_target"',
                    datatypeName: 'String'
                },
                x_active: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_HBW"."x_active"',
                    datatypeName: 'Bool'
                },
                x_error: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_HBW"."x_error"',
                    datatypeName: 'Bool'
                },
                s_errorMessage: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_HBW"."s_errorMessage"',
                    datatypeName: 'String'
                }
            },

            state_VGR: {
                // This node is subscribed to to get the State of the VGR. When the server starts, it also publishes on this node to trigger the polling process.
                ldt_ts: {
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_VGR"."ldt_ts"',
                    datatypeName: 'DateTime'
                },

                // When data is published to ldt_ts, these nodes (and ldt_ts as well) are polled. Then the data is published to 'f/i/state/vgr'.
                i_code: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_VGR"."i_code"',
                    datatypeName: 'Int16'
                },

                s_description: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_VGR"."s_description"',
                    datatypeName: 'String'
                },

                s_station: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_VGR"."s_station"',
                    datatypeName: 'String'
                },

                s_target: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_VGR"."s_target"',
                    datatypeName: 'String'
                },

                x_active: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_VGR"."x_active"',
                    datatypeName: 'Bool'
                }
            },

            state_SLD: {
                ldt_ts: {
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_SLD"."ldt_ts"',
                    datatypeName: 'DateTime'
                },

                // When data is published to ldt_ts, these nodes (and ldt_ts as well) are polled. Then the data is published to 'f/i/state/sld'.
                i_code: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_SLD"."i_code"',
                    datatypeName: 'Int16'
                },

                s_description: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_SLD"."s_description"',
                    datatypeName: 'String'
                },

                s_station: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_SLD"."s_station"',
                    datatypeName: 'String'
                },

                s_target: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_SLD"."s_target"',
                    datatypeName: 'String'
                },

                x_active: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_SLD"."x_active"',
                    datatypeName: 'Bool'
                }
            },

            postPanTiltUnit: {
                ldt_ts: {
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."PosPanTiltUnit"."ldt_ts"',
                    datatypeName: 'DateTime'
                }
            }
        },

        publish: {
            // When the Ack. button on the Dashboard is pressed, the timestamp is sent to the PLC
            ldt_AcknowledgeButton: {
                name: '',
                nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Publish"."ldt_AcknowledgeButton"',
                datatypeName: 'DateTime'
            },

            postPanTiltUnit: {
                s_cmd: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Publish"."PosPanTiltUnit"."s_cmd"',
                    datatypeName: 'String',
                },
                i_degree: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Publish"."PosPanTiltUnit"."i_degree"',
                    datatypeName: 'Int16'
                },
                ldt_ts: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Publish"."PosPanTiltUnit"."ldt_ts"',
                    datatypeName: 'DateTime'
                }
            },

            actionButtonNFCModule: {
                s_cmd:
                {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Publish"."ActionButtonNFCModule"."s_cmd"',
                    datatypeName: 'String'
                },
                ldt_ts:
                {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Publish"."ActionButtonNFCModule"."ldt_ts"',
                    datatypeName: 'DateTime'
                },
                workpiece: {
                    s_id: {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Publish"."ActionButtonNFCModule"."Workpiece"."s_id"',
                        datatypeName: 'String'
                    },
                    s_state: {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Publish"."ActionButtonNFCModule"."Workpiece"."s_state"',
                        datatypeName: 'String'
                    },
                    s_stype: {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Publish"."ActionButtonNFCModule"."Workpiece"."s_type"',
                        datatypeName: 'String'
                    },
                    history: [
                        {
                            i_code:
                            {
                                name: "",
                                nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Publish"."ActionButtonNFCModule"."History"[0]."i_code"',
                                datatypeName: 'Int16'
                            },
                            ldt_ts: {
                                name: "",
                                nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Publish"."ActionButtonNFCModule"."History"[0]."ldt_ts"',
                                datatypeName: 'DateTime'
                            }
                        }
                    ]
                }
            },

            // Data is published to these nodes when the queue is not full, and a new workpiece is ordered.
            orderWorkpieceButton: {
                s_type:
                {
                    name: "Name0",
                    nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."s_type"',
                    datatypeName: 'String'
                },
                workpiece_parameters: {
                    ovenTime: {
                        name: "Name1",
                        nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."OvenTime"',
                        datatypeName: 'Int32'
                    },
                    doOven: {
                        name: "Name2",
                        nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."DoOven"',
                        datatypeName: 'Boolean'
                    },
                    sawTime: {
                        name: "Name3",
                        nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."SawTime"',
                        datatypeName: 'Int32'
                    },
                    doSaw: {
                        name: "Name4",
                        nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."DoSaw"',
                        datatypeName: 'Boolean'
                    },
                    ldt_ts: {
                        name: "Name5",
                        nodeId: 'ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."ldt_ts"',
                        datatypeName: 'DateTime'
                    }
                }
            }
        }
    },

    gtyp_HBW: {
        rack_workpiece:
            // HBW view
            // These nodes are polled when the PLC publishes to ns=3;s="gtyp_HBW"."Rack_Workpiece". They represent cells in the HBW.
            [
                [
                    //ROW A
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[0,0]."s_id"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[0,0]."s_state"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[0,0]."s_type"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[0,1]."s_id"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[0,1]."s_state"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[0,1]."s_type"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[0,2]."s_id"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[0,2]."s_state"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[0,2]."s_type"',
                        datatypeName: 'STRING'
                    }
                ],
                [
                    //ROW B
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[1,0]."s_id"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[1,0]."s_state"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[1,0]."s_type"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[1,1]."s_id"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[1,1]."s_state"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[1,1]."s_type"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[1,2]."s_id"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[1,2]."s_state"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[1,2]."s_type"',
                        datatypeName: 'STRING'
                    }
                ],
                [
                    //ROW C
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[2,0]."s_id"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[2,0]."s_state"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[2,0]."s_type"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[2,1]."s_id"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[2,1]."s_state"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[2,1]."s_type"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[2,2]."s_id"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[2,2]."s_state"',
                        datatypeName: 'STRING'
                    },
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_HBW"."Rack_Workpiece"[2,2]."s_type"',
                        datatypeName: 'STRING'
                    }
                ]
            ]

    },

    gtyp_Interface_TXT_Controler: {
        subscribe: {
            state_NFC_device: {
                ldt_ts: {
                    name: "",
                    nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."ldt_ts"',
                    datatypeName: 'DateTime'
                },
                workpiece: {
                    s_id:
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."Workpiece"."s_id"',
                        datatypeName: 'String'
                    },
                    s_state:
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."Workpiece"."s_state"',
                        datatypeName: 'String'
                    },
                    s_type:
                    {
                        name: "",
                        nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."Workpiece"."s_type"',
                        datatypeName: 'String'
                    },
                },
                history: [
                    {
                        i_code:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[0]."i_code"',
                            datatypeName: 'Int16'
                        },
                        ldt_ts:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[0]."ldt_ts"',
                            datatypeName: 'DateTime'
                        },
                    },
                    {
                        i_code:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[1]."i_code"',
                            datatypeName: 'Int16'
                        },
                        ldt_ts:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[1]."ldt_ts"',
                            datatypeName: 'DateTime'
                        },
                    },
                    {
                        i_code:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[2]."i_code"',
                            datatypeName: 'Int16'
                        },
                        ldt_ts:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[2]."ldt_ts"',
                            datatypeName: 'DateTime'
                        },
                    },
                    {
                        i_code:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[3]."i_code"',
                            datatypeName: 'Int16'
                        },
                        ldt_ts:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[3]."ldt_ts"',
                            datatypeName: 'DateTime'
                        },
                    },
                    {
                        i_code:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[4]."i_code"',
                            datatypeName: 'Int16'
                        },
                        ldt_ts:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[4]."ldt_ts"',
                            datatypeName: 'DateTime'
                        },
                    },
                    {
                        i_code:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[5]."i_code"',
                            datatypeName: 'Int16'
                        },
                        ldt_ts:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[5]."ldt_ts"',
                            datatypeName: 'DateTime'
                        },
                    },
                    {
                        i_code:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[6]."i_code"',
                            datatypeName: 'Int16'
                        },
                        ldt_ts:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[6]."ldt_ts"',
                            datatypeName: 'DateTime'
                        },
                    },
                    {
                        i_code:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[7]."i_code"',
                            datatypeName: 'Int16'
                        },
                        ldt_ts:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[7]."ldt_ts"',
                            datatypeName: 'DateTime'
                        },
                    },
                    {
                        i_code:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[8]."i_code"',
                            datatypeName: 'Int16'
                        },
                        ldt_ts:
                        {
                            name: "",
                            nodeId: 'ns=3;s="gtyp_Interface_TXT_Controler"."Subscribe"."State_NFC_Device"."History"[8]."ldt_ts"',
                            datatypeName: 'DateTime'
                        },
                    },
                ]
            }
        }
    },

    queue: {
        x_queue_full: {
            nodeId: 'ns=3;s="Queue"."x_Queue_Full"',
            datatypeName: 'Bool'
        }
    }
}