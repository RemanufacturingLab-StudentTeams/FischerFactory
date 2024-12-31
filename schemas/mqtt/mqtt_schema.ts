/**
 * This file contains a comprehensive, human-readable documentation of the MQTT schema used for communication between
 * the Raspberry Pi and several other components, like the server, bme, Turtlebot, and various extensions. It is written in TypeScript for convenience, and is not supposed to be
 * compiled to JavaScript.
 */

/**
 * Timestamps are in ISO 8601 format. E.g.: "2022-09-27 18:00:00.000".
 */

/**
 * Units and min..max values are in block brackets, e.g. [1..100][Celsius] means min. 1 degree Celsius, max 100 degrees Celsius
 */

type schema = {
    f: { // Fischer Factory

        tracking: { //topic(s) used for tracking feature
            topic: "f/tracking"
            //If the puck is rejected 'AtEnd' will not be published 
            //Only one of the OnBlue,OnRed,OnWhite will be published
            //Incase the oven is used 'OutsiteOven' will be published twice, once when entering and when exiting.
            payload: {
                trackPuck: "Warehouse" | "BeforeCrane" | "OnCrane" | "OutsiteOven" | "InsideOven" | "OnBelt" | "OnSaw" | "OnSortBelt" | "Behindcolorsens" | "OnRed" | "OnBlue" | "OnWhite" | "AtEnd"
            }

        }


        i: { // topics that are published to to translate OPC UA messages from the PLC to MQTT
            alert: {
                // Alert message from OPC UA
                topic: 'f/i/alert',
                payload:
                {
                    code: number,
                    data: string,
                    id: string,
                    ts: Date
                }
            },

            state: {
                // DSI state
                dsi: {
                    topic: 'f/i/state/dsi'
                    payload: {
                        ts: Date
                        station: 'dsi'
                        code: number // 0 available, 1 not available
                        description: string
                        active: 1
                        error: number
                        errorMessage: string
                        target: 'dsi'
                    }
                },
                // DSO state is sent over MQTT after 'gtyp_Interface_Dashboard"."Subscribe"."State_DSO' nodes are polled
                dso: {
                    topic: 'f/i/state/dso'
                    payload: {
                        ts: Date
                        station: "dso"
                        code: number // 0 available, 1 not available
                        description: string
                        active: 1
                        error: number
                        errorMessage: string
                        target: 'dso'
                    }
                },

                mpo: {
                    topic: "f/i/state/mpo",
                    payload: {
                        ts: Date,
                        station: 'mpo',
                        code: number // Bit code for lamps: Red=4 Yellow=2 Green=1
                        description: string,
                        active: 1,
                        error: number,
                        errorMessage: string,
                        target: 'mpo' // target node for process
                        inOven: false,
                        tsOven: Date,
                        atSaw: false,
                        tsSaw: Date,
                        workpieceID: string,
                        workpieceType: string,
                        setOvenTime: number,
                        setSawTime: 0
                    }
                },

                sld: {
                    topic: "f/i/state/sld",
                    payload: {
                        ts: Date,
                        station: "sld",
                        code: number // Bit code for lamps: Red=4 Yellow=2 Green=1
                        description: string,
                        active: 1,
                        error: number,
                        errorMessage: string,
                        target: "sld" // target node for process
                        tsColor: Date,
                        colorObserved: false,
                        observedColor: "String",
                        workpieceID: string,
                        workpieceType: string,
                        onTransportBelt: false,
                        tsTransportBelt: Date

                    }
                },

                vgr: {
                    // VGR state is sent over MQTT after 'gtyp_Interface_Dashboard"."Subscribe"."State_VGR' nodes are polled
                    topic: 'f/i/state/vgr',
                    payload: {
                        ts: Date,
                        station: "vgr",
                        code: number // Bit code for lamps: Red=4 Yellow=2 Green=1
                        description: string,
                        active: number,
                        error: number,
                        errorMessage: string,
                        target: 'vgr' // target node for process
                    }

                },

                hbw: {
                    // VGR state is sent over MQTT after 'gtyp_Interface_Dashboard"."Subscribe"."State_VGR' nodes are polled
                    topic: 'f/i/state/hbw',
                    payload: {
                        ts: Date,
                        station: "hbw",
                        code: number // Bit code for lamps: Red=4 Yellow=2 Green=1
                        description: string,
                        active: 1,
                        error: number,
                        errorMessage: string,
                        target: "hbw",
                    }

                },
            },

            stock: {
                topic: 'f/i/stock',
                payload: {
                    stockItems: FixedLengthArray<{
                        workpiece: {
                            id: string
                            state: 'RAW' | 'PROCESSED'
                            type: 'RED' | 'WHITE' | 'BLUE'
                        }
                        location: 'A1' | 'A2' | 'A3' | 'B1' | 'B2' | 'B3' | 'C1' | 'C2' | 'C3'
                    }, 9>
                    ts: Date,
                }
            }

            order: {
                topic: 'f/i/order'
                payload: {
                    ts: Date
                    state: 'WAITING_FOR_ORDER' | 'ORDERED'| 'IN_PROCESS' | 'SHIPPED'
                    type: 'RED' | 'WHITE' | 'BLUE'
                }
            }

            nfc: {
                ds: {
                    topic: 'f/i/nfc/ds'
                    payload: {
                        ts: Date
                        workpiece: {
                            id: string
                            state: 'RAW' | 'PROCESSED'
                            type: 'RED' | 'WHITE' | 'BLUE'
                        }
                        history: FixedLengthArray<{
                            ts: Date
                            /**
                             * 100 = 'Delivery of raw materials'
                             * 200 = 'Quality control'
                             * 300 = 'Storage'
                             * 400 = 'Removal from storage'
                             * 500 = 'Processing kiln'
                             * 600 = 'Milling processing'
                             * 700 = 'Sorting'
                             * 800 = 'Dispatch of goods'
                             */
                            code: number
                        }, 1000>
                    }
                }
            }
        },
        o: { // topics that the Dashboard publishes to as output
            state: {
                // Dashboard Ack. Button from MQTT
                ack: { // Serves as a trigger to acknowledge the error status so production can continue
                    topic: 'f/o/state/ack',
                    payload: {
                        ts: Date
                    }
                },
            },

            order: {
                topic: 'f/o/order'
                payload: {
                    type: 'RED' | 'WHITE' | 'BLUE'
                    ts: Date
                }
            },

            // NFC reader - control actions from MQTT
            nfc: {
                ds: {
                    topic: "f/o/nfc/ds"
                    payload: {
                        cmd: 'delete' | 'read' | 'read_uid'
                        ts: Date
                    }
                }
            }
        }
    },

    o: { // Node-RED -> Factory components (no PLC)
        ptu: {
            // Post/pan tilt unit - control actions from MQTT
            topic: "o/ptu",
            payload: {
                cmd: "relmove_left" // Dashboard icon: keyboard_arrow_left
                | "relmove_right" // Dashboard icon: keyboard_arrow_right
                | "relmove_down" // Dashboard icon: keyboard_arrow_down
                | "relmove_up" // Dashboard icon: keyboard_arrow_up
                | "stop" // Dashboard icon: fa-stop fa-2x
                | "home" // Dashboard icon: fa-home fa-4x
                | "start_pan" // Dashboard icon: arrow_back
                | "end_pan" // Dashboard icon: arrow_forward
                | "start_tilt" // Dashboard icon: arrow_downward
                | "end_tilt", // Dashboard icon: arrow_upwards
                degree: 10 // for all the "relmove" commands [decimal]
                | 1, // for everything else
                ts: Date
            }
        }

        broadcast: {
            topic: 'o/broadcast'
            payload: {
                ts: Date
                hardwareId: string
                softwareName: string
                softwareVersion: string
                message: string
            }
        }
    },

    fl: {
        i: {
            // NFC reader - deliver read values from MQTT to OPC UA
            nfc: {
                ds: {
                    topic: 'fl/i/nfc/ds'
                    payload: {
                        ts: Date
                        workpiece: {
                            id: string
                            type: string
                            state: string
                        }
                        history: FixedLengthArray<{
                            code: number
                            ts: Date
                        }, 9>
                    }
                }
            }
        },
        o: {
            nfc: { // relay MQTT payload from fl/i/nfc/ds to OPC UA after adding a command (cmd)
                ds: {
                    topic: 'fl/o/nfc/ds',
                    payload: {
                        ts: Date
                        cmd: string
                        workpiece: {
                            id: string
                            type: string
                            state: string
                        },
                        history: FixedLengthArray<{
                            code: number
                            ts: Date
                        }, 9>
                    }
                }
            }
        },

        broadcast: {
            topic: 'fl/broadcast',
            payload: {
                ts: Date
            }
        }

        ssc: { // no clue what this is
            joy: {
                topic: 'fl/ssc/joy',
                payload: {
                    ts: Date
                }
            }
        }

        hbw: {
            ack: {
                topic: 'fl/hbw/ack'
                payload: {
                    ts: Date
                }
            }
        }

        mpo: {
            ack: {
                topic: 'fl/mpo/ack'
                payload: {
                    ts: Date
                }
            }
        }

        sld: {
            ack: {
                topic: 'fl/sld/ack'
                payload: {
                    ts: Date
                }
            }
        }

        vgr: {
            do: {
                topic: 'fl/vgr/do',
                payload: {
                    ts: Date
                }
            }
        }
    },

    // Inputs from MQTT publishers other than the Node-RED program.
    i: {
        ldr: { // Photoresistor
            topic: 'i/ldr',
            payload: {
                br: number // brightness [0..100.0]
                ldr: number // Resistance [0..15000] [Ohm]
                ts: Date
            }
        },

        ptu: {
            topic: 'i/ptu'
            payload: {
                ts: Date
            }
            pos: {
                topic: 'i/ptu/pos'
                payload: {
                    ts: Date
                    pan: number // [-1.000...0.000...1.000]
                    tilt: number // [-1.000...0.000...1.000]
                }
            }
        },

        bme680: {
            topic: 'i/bme680'
            payload: {
                ts: Date
                t: number // temperature, adjusted [Celsius]
                p: number // pressure [hPa]
                iaq: number // air quality index (0-500 (0...50:Good, 51...100:Moderate, 101...150:Unhealthy for Sensitive Groups, 151...200:Unhealthy, 201...300:Very Unhealthy, 301...500:Hazardous))
                aq: number // air quality score  0-3 (0:IAQ invalid, 1:Calibration necessary, 2:Calibration complete, 3:IAQ is calibrated)
                h: number // humidity [%]
            }
        },

        cam: {
            topic: 'i/cam'
            payload: {
                ts: Date
                data: string // URI: data:image/jpeg;base64
            }
        },

        alert: {
            topic: 'i/alert'
            payload: {
                ts: Date
                id: 'bme680/t' | 'bme680/h' | 'bme680/p' | 'bme680/iaq' | 'ldr' | 'cam' // id of the component that triggered the alert
                data: string
                /**
                * Alarm codes:
                100 = 'Alarm: Motion detected!': Motion in the camera image
                200 = 'Alarm: Danger of frost! (%1)': Temperature < 4.0°C
                300 = 'Alarm: High humidity! (%1)': Humidity > 80%
                 */
                code: number
            }
        },

        // Note: not used in the FischerFactory. 
        broadcast: {
            topic: 'i/broadcast'
            payload: {
                ts: Date,
                hardwareId: string
                hardwareModel: string
                softwareName: string
                softwareVersion: string
                message: string
            }
        }
    },

    Turtlebot: {
        // The TurtleBotPosition type only provides the topic suffix. To get the full topic name,
        // prepend it with the type path. For instance:
        // "Turtlebot/Position/Home/X"
        // is a valid topic name.
        Position: {
            Home: TurtleBotPosition
            DockReady: TurtleBotPosition
            PickUpFischer: TurtleBotPosition
            DropOffFischer: TurtleBotPosition
            MagazineIn: TurtleBotPosition
            MagazineOut: TurtleBotPosition
        }
        VersionNumber: {
            topic: 'Turtlebot/VersionNumber'
            payload: string
        }
        State: {
            topic: 'Turtlebot/State'
            payload: 'on_Home'
            | 'on_PickUpFischer'
            | 'on_DropOffFischer'
            | 'on_MagazineIn'
            | 'on_MagazineOut'
            | 'Quit'
        }
        CurrentState: {
            topic: 'Turtlebot/CurrentState'
            payload: string
        }
    },

    esp32: {
        Status: {
            topic: 'esp32/Status'
            payload: 'on' | 'off' // Plaintext payload, not JSON
        }
        Slagboom: {
            topic: 'esp32/Slagboom'
            payload: 'on' | 'off' // Plaintext payload, not JSON
        }
        Speed: {
            topic: 'esp32/Speed'
            payload: number // Plaintext payload, not JSON
        }
    }

    c: { // Configuration / status topics
        cam: { // Camera
            topic: 'c/cam',
            payload: { // If the camera is on
                on: "true"
                fps: "2" // [2..15]
                ts: Date
            }
        }
        ldr: { // photoresistor
            topic: 'c/ldr'
            payload: {
                /**
                 * Sensor values per second
                    2 corresponds to one sensor value every 2 seconds
                    6 corresponds to one sensor value every six seconds
                 */
                period: 3,
                ts: Date
            }
        }
        bme680: {
            topic: 'c/bme680'
            payload: {
                /**
                 * Sensor values per second
                    Minimum 3 or multiple of 3
                    3 corresponds to one sensor value every three seconds
                    6 corresponds to one sensor value every six seconds
                 */
                period: 3,
                ts: Date
            }
        }
    },

    oven: {
        time: {
            // From the MPO, last measured oven time (ms)
            topic: "oven/time",
        }
    },

    saw: {
        time: {
            // From MPO, last measured saw time (ms)
            topic: "saw/time",
        }
    },

    detected: {
        color: {
            // From SLD, detected color
            topic: "detected/color"
        }
    },

    transport: {
        time: {
            // From SLD, last measured transport time (ms)
            topic: "transport/time"
        }
    }

}

export type FixedLengthArray<T, L extends number> = L extends 0 ? never[] : [T, ...Array<T>];
type TurtleBotPosition = {
    X: {
        topicSuffix: '/X'
        payload: number
    }
    Y: {
        topicSuffix: '/Y'
        payload: number
    }
    Z: {
        topicSuffix: '/Z'
        payload: number
    }
    AngleExtension: {
        topicSuffix: '/AngleExtension'
        payload: number
    }
    AngleTurlebot: {
        topicSuffix: '/AngleTurlebot'
        payload: number
    }
    OpenClosed: {
        topicSuffix: '/OpenClosed'
        payload: number
    }
}
