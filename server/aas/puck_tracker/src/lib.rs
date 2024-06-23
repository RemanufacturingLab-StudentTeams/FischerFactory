use rumqttc::ClientError;
use serde::{Serialize, Deserialize};
use serde_json;

#[derive(Clone, Copy, PartialEq)]
pub enum PuckColour {
    RED,
    WHITE,
    BLUE,
}

pub struct Puck {
    pub colour: PuckColour,
}

pub struct Component {
    pub tracking_label: &'static str, // the string payload published on f/tracking corresponding to this component. E.g., "InsideOven" for MPO.
    // Note that this is not the same as the IdShort of the Submodel in the AAS.
    pub red_pucks_topic: &'static str,
    pub white_pucks_topic: &'static str,
    pub blue_pucks_topic: &'static str,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Order {
    pub r#type: String, // 'type' is a reserved word in Rust so I am using r# to escape it
}

pub const COMPONENTS: [Component; 4] = [
    Component {
        tracking_label: "OnCrane",
        red_pucks_topic: "aas/vgr/numRedPucks",
        white_pucks_topic: "aas/vgr/numWhitePucks",
        blue_pucks_topic: "aas/vgr/numBluePucks",
    },
    Component {
        tracking_label: "OnSortBelt",
        red_pucks_topic: "aas/sld/numRedPucks",
        white_pucks_topic: "aas/sld/numWhitePucks",
        blue_pucks_topic: "aas/sld/numBluePucks",
    },
    Component {
        tracking_label: "AtEnd",
        red_pucks_topic: "aas/dso/numRedPucks",
        white_pucks_topic: "aas/dso/numWhitePucks",
        blue_pucks_topic: "aas/dso/numBluePucks",
    },
    Component {
        tracking_label: "InsideOven",
        red_pucks_topic: "aas/mpo/numRedPucks",
        white_pucks_topic: "aas/mpo/numWhitePucks",
        blue_pucks_topic: "aas/mpo/numBluePucks",
    },
    // The DSI has no puck tracking sensor, so this component is commented out. It could be used later if necessary.
    // Component {
    //     tracking_label: "",
    //     red_pucks_topic: "aas/dsi/numRedPucks",
    //     white_pucks_topic: "aas/dsi/numWhitePucks",
    //     blue_pucks_topic: "aas/dsi/numBluePucks",
    // },
];

#[derive(Debug)]
pub enum UpdateError {
    SerdeError(serde_json::Error),
    UnrecognizedPuckColour(String),
    UnrecognizedTrackingPayload(String), // thrown when a payload is published to "f/tracking" that the program does not recognise.
    ClientError(ClientError),
}

impl From<serde_json::Error> for UpdateError {
    fn from(err: serde_json::Error) -> UpdateError {
        UpdateError::SerdeError(err)
    }
}