/**
 * This program assumes only one puck can be active in the FischerFactory at one time. It was originally created with the intention of 
 * managing multiple pucks, providing the memory required to determine which puck was where based on the emissions from the puck tracking 
 * sensors in the FischerFactory (which does not say which puck was detected, only that it was). 
 * 
 * For just one puck, the logic is much simpler; just remember which puck is currently active and send MQTT messages to the different components
 * based on that.
 */

use std::env;
use std::io;
use std::string;

use rumqttc::Packet;
use rumqttc::{AsyncClient, MqttOptions, QoS};
use tokio::runtime::Runtime;

enum Puck {
    RED,
    WHITE,
    BLUE,
}

struct Component<'a> {
    tracking_label: &'a str, // the string payload published on f/tracking corresponding to this component. E.g., "InsideOven" for MPO.
    red_pucks_topic: &'a str,
    white_pucks_topic: &'a str,
    blue_pucks_topic: &'a str,
}

const COMPONENTS: [Component; 1] = [
    Component {
        tracking_label: "Warehouse",
        red_pucks_topic: "aas/mpo/numRedPucks",
        white_pucks_topic: "aas/mpo/numWhitePucks",
        blue_pucks_topic: "aas/mpo/numBluePucks",
    },
];

fn main() -> io::Result<()> {
    println!("===== Tracker started =====");

    let rt = Runtime::new().unwrap();

    let pucks: Vec<Puck> = vec![];
    let locations: Vec<&str> = vec![
        "Warehouse",
        "BeforeCrane",
        "OnCrane",
        "OutsiteOven",
        "InsideOven",
        "OnBelt",
        "OnSaw",
        "OnSortBelt",
        "BehindcolorSens",
        "OnRed",
        "OnBlue",
        "OnWhite",
        "AtEnd",
    ];

    // Connect to the broker
    let production_mode = env::args().any(|s| s.eq("prod")); // default in dev
    if!production_mode { println!("Running in dev mode. Use \"-- prod\" to run in production mode."); }
    let server = if production_mode { "192.168.0.10" } else { "localhost" };

    let mut mqtt_options = MqttOptions::new(
        "puck_tracker",
        server,
        1883,
    );
    mqtt_options.set_credentials("puck_tracker", "test123");

    println!("Connecting to {}...", server);
    let (client, mut event_loop) = AsyncClient::new(mqtt_options, 10);

    // Subscribe to order and tracking topics
    rt.spawn(async move {
        client
            .subscribe("f/o/order", QoS::AtMostOnce)
            .await
            .unwrap();
        client
            .subscribe("f/tracking", QoS::AtMostOnce)
            .await
            .unwrap();
    });

    rt.block_on(async move {
        loop {
            let notif = event_loop.poll().await;

            match notif {
                Err(e) => eprint!("{}", e),
                Ok(event) => {
                    match event {
                        rumqttc::Event::Incoming(Packet::Publish(p)) => {
                            let payload = std::str::from_utf8(&p.payload).expect("Valid UTF-8 string");
                            println!("Received: {} on topic {}", payload, p.topic);

                        }
                        _ => { println!("{:?}", event)}
                    }
                }
            }
        }
    });

    Ok(())
}

/**
 * Relays the information from the tracking topic to the aas topics, such as aas/mpo/state.
 */
fn relay() {

}

/**
 * Set the amount of pucks on a Submodel to 0 by publishing to, e.g., aas/mpo/(numRedPucks, numBluePucks, numWhitePucks). 
 */
fn reset() {

}
