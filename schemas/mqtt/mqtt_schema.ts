type schema = {
    f: { // Fischer Factory

        tracking: { //topic(s) used for tracking feature
            topic: "f/tracking"
            payload: "Warehouse" | "BeforeCrane" | "OnCrane" | "OutsiteOven" | "InsideOven" | "OnBelt" | "OnSaw" | "OnSortBelt" | "Behindcolorsens" | "OnRed" | "OnBlue" | "OnWhite" | "AtEnd"

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
                    topic: 'f/i/state/dsi',
                    payload: {
                        ts: Date,
                        station: "dsi",
                        code: number,
                        description: string
                    }
                },
                // DSO state is sent over MQTT after 'gtyp_Interface_Dashboard"."Subscribe"."State_DSO' nodes are polled
                dso: {
                    topic: 'f/i/state/dso',
                    payload: {
                        ts: Date,
                        station: "dso",
                        code: number,
                        description: string
                    }
                },

                mpo: {
                    topic: "f/i/state/mpo",
                    payload: {
                        ts: Date,
                        station: "mpo",
                        code: number,
                        description: string,
                        active: 1,
                        error: number,
                        errorMessage: string,
                        target: "mpo",
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
                        code: number,
                        description: string,
                        active: 1,
                        error: number,
                        errorMessage: string,
                        target: "sld",
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
                        code: number,
                        description: string,
                        active: 1,
                        target: "vgr"
                    }

                },

                hbw: {
                    // VGR state is sent over MQTT after 'gtyp_Interface_Dashboard"."Subscribe"."State_VGR' nodes are polled
                    topic: 'f/i/state/hbw',
                    payload: {
                        ts: Date,
                        station: "hbw",
                        code: number,
                        description: string,
                        active: 1,
                        target: "hbw",
                        err: false,
                        errorMessage: string
                    }

                },
            },

            stock: {
                topic: 'f/i/stock',
                payload: {
                    stockItems: FixedLengthArray<{
                        workpiece: {
                            id: string,
                            state: string,
                            type: 'RED' | 'WHITE' | 'BLUE'
                        }, location: string
                    }, 9>
                    ts: Date,
                }
            }
        },
        o: { // topics that the Dashboard publishes to
            state: {
                // Dashboard Ack. Button from MQTT
                ack: {
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
                degree: 10 // for all the "relmove" commands
                | 1, // for everything else
                ts: Date
            }
        }
    },

    fl: {
        i: {
            // NFC reader - deliver read values from MQTT to OPC UA
            nfc: {
                ds: {
                    topic: 'fl/i/nfc/ds'
                }
            }
        },
        o: {
            nfc: {
                ds: {
                    topic: 'fl/o/nfc/ds'
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
    // Note: the payloads might not be comprehensive, as the publishing client was too opaque at the time of writing. 
    i: {
        ldr: {
            topic: 'i/ldr',
            payload: {
                br: number // brightness
                ts: Date
            }
        },

        ptu: {
            topic: 'i/ptu'
            payload: {
                ts: Date
            }
        },

        bme680: {
            topic: 'i/bme680'
            payload: {
                ts: Date
                t: number // temperature
                p: number // pressure
                iaq: number // air quality index
                aq: number // air quality score
                h: number // humidity
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
                on: "true",
                fps: "2",
                ts: Date
            }
        }
        ldr: {
            topic: 'c/ldr'
            payload: {
                period: 3,
                ts: Date
            }
        }
        bme680: {
            topic: 'c/bme680'
            payload: {
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

type FixedLengthArray<T, L extends number> = L extends 0 ? never[] : [T, ...Array<T>];
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
