use std::env;
use std::io;

use rumqttc::Packet;
use rumqttc::{AsyncClient, MqttOptions, QoS};
use tokio::runtime::Runtime;

enum Puck {
    RED,
    WHITE,
    BLUE,
}

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
