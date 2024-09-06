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
use rumqttc::ClientError;
use serde_json;

use rumqttc::Packet;
use rumqttc::{AsyncClient, MqttOptions, QoS};
use tokio::runtime::Runtime;
use tokio::time::{sleep, Duration};

use puck_tracker::*;

fn main() -> io::Result<()> {
    println!("===== Tracker started =====");

    let rt = Runtime::new().unwrap();

    let mut pucks: Vec<Puck> = vec![];

    // Connect to the broker
    let production_mode = env::args().any(|s| s.eq("prod")); // default in dev
    if !production_mode { println!("Running in dev mode. Use \"-- prod\" to run in production mode."); }
    let server = if production_mode { "192.168.0.10" } else { "localhost" };
    let port = 1883;

    let mut mqtt_options = MqttOptions::new(
        "puck_tracker",
        server,
        port,
    );
    mqtt_options.set_credentials("puck_tracker", "test123");

    println!("Connecting to {}:{}...", server, port);
    let (client, mut event_loop) = AsyncClient::new(mqtt_options, 10);

    rt.block_on(async move {
        client.subscribe("f/o/order", QoS::AtMostOnce).await.expect("Could not subscribe!");
        client.subscribe("f/tracking", QoS::AtMostOnce).await.expect("Could not subscribe!");

        loop {
            let notif = event_loop.poll().await;

            match notif {
                Err(e) => {
                    eprintln!("Error in event loop: {}, retrying in 5 seconds...", e);
                    sleep(Duration::from_secs(5)).await; 
                },
                Ok(event) => {
                    match event {
                        rumqttc::Event::Incoming(Packet::Publish(p)) => {
                            let payload = std::str::from_utf8(&p.payload).expect("Valid UTF-8 string");
                            println!("Received: {} on topic {}", payload, p.topic);

                            match update(&p.topic, payload, &mut pucks, &client).await {
                                Ok(_) => {},
                                Err(UpdateError::ClientError(e)) => panic!("MQTT client error: {:#?}", e),
                                Err(UpdateError::UnrecognizedPuckColour(e)) => eprint!("Unrecognised puck colour: {}", e),
                                Err(UpdateError::UnrecognizedTrackingPayload(e)) => eprint!("Unrecognised tracking payload: {}", e),
                                Err(UpdateError::SerdeError(e)) => eprint!("Could not deserialize JSON: {:#?}", e),
                            }
                        }
                        _ => { println!("{:?}", event)}
                    }
                }
            }
        }
    });

    Ok(())
}

async fn update(topic: &str, payload: &str, pucks: &mut Vec<Puck>, client: &AsyncClient) -> Result<(), UpdateError>{
    if topic == "f/o/order" {
        let puck_colour_msg: Order = serde_json::from_str(payload)?;

        let colour = match puck_colour_msg.r#type.as_str() { // only accessing the 0-th element here because of the one active puck assumption
            "RED" => PuckColour::RED,
            "WHITE" => PuckColour::WHITE,
            "BLUE" => PuckColour::BLUE,
            other => return Err(UpdateError::UnrecognizedPuckColour(other.to_string())),
        }; 

        if let Some(p) = pucks.get_mut(0) { p.colour = colour } else {
            pucks.push(Puck { colour });
        }
    } else { // we got a tracking message
        let futures = COMPONENTS.iter().map(|c| {
            let client = client.clone();
            let tracking_label = c.tracking_label.clone();
            let payload = payload.to_owned();
            let colour = pucks[0].colour;

            tokio::task::spawn(async move {
                if tracking_label == payload {
                    if let Err(e) = relay(c, colour, &client).await {
                        return Err(UpdateError::ClientError(e));
                    }
                } else {
                    if let Err(e) = reset(c, &client).await {
                        return Err(UpdateError::ClientError(e));
                    };
                }
                Ok(())
            })
        });

        for f in futures { f.await.expect("Relay call could not be joined")?; }
    }

    Ok(())
}

/**
 * Relays the information from the tracking topic to the aas topics, such as aas/mpo/state.
 */
async fn relay(component: &Component, p: PuckColour, client: &AsyncClient) -> Result<(), ClientError> {
    println!("Sending relay to {}", &component.tracking_label);
    client.publish(component.red_pucks_topic, QoS::AtLeastOnce, false, 
        if p == PuckColour::RED {"{\"value\": 1}"} else {"{\"value\": 0}"}).await?;
    client.publish(component.blue_pucks_topic, QoS::AtLeastOnce, false, 
        if p == PuckColour::BLUE {"{\"value\": 1}"} else {"{\"value\": 0}"}).await?;
    client.publish(component.white_pucks_topic, QoS::AtLeastOnce, false, 
        if p == PuckColour::WHITE {"{\"value\": 1}"} else {"{\"value\": 0}"}).await?;

    Ok(())
}

/**
 * Set the amount of pucks on a Submodel to 0 by publishing to, e.g., aas/mpo/(numRedPucks, numBluePucks, numWhitePucks). 
 */
async fn reset(component: &Component, client: &AsyncClient) -> Result<(), ClientError> {
    println!("Sending reset to {}", &component.tracking_label);
    client.publish(component.red_pucks_topic, QoS::AtLeastOnce, false, "{\"value\": 0}").await?;
    client.publish(component.white_pucks_topic, QoS::AtLeastOnce, false, "{\"value\": 0}").await?;
    client.publish(component.blue_pucks_topic, QoS::AtLeastOnce, false, "{\"value\": 0}").await?;

    Ok(())
}
