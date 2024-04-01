use serde::{Deserialize, Serialize};
use serde_json::Value;
use tokio::task;
use std::fs::File;
use std::io::{self, BufReader};
use rumqttc::{AsyncClient, MqttOptions, QoS};
use tokio::runtime::Runtime;

// Define the structure for each test case
#[derive(Debug, Serialize, Deserialize, Clone)]
struct TestCase {
    topic: String,
    payload: Value,
}

fn read_json() -> Result<Vec<TestCase>, io::Error> {
    // Open and read the test values file
    let file = File::open("resources/test_values.json")?;
    let reader = BufReader::new(file);

    // Deserialize the JSON into a vector of test cases
    Ok(serde_json::from_reader(reader)?)
}

fn main() -> io::Result<()> {

    let test_cases = read_json()?;
    let rt = Runtime::new().unwrap();

    let mqtt_options = MqttOptions::new("mqtt_testing_tool", "localhost", 1883);
    let (client, mut event_loop) = AsyncClient::new(mqtt_options, 10);

    rt.spawn(async move {
        loop {
            let notification = event_loop.poll().await.unwrap();
            println!("  Received: {:?}", notification);
        }
    });

    rt.block_on(async {
        loop {
            println!("Enter a topic:");
            let mut input = String::new();
            if let Err(e) = io::stdin().read_line(&mut input) {
                eprint!("Could not read test cases file, {:?}", e);
            }
            let input = input.trim();

            if let Some(test_case) = test_cases.iter().find(|&tc| tc.topic == input) {
                println!("Test value found:");
                println!("Topic: {}", &test_case.topic);
                println!("Test payload: {:#?}", test_case.payload);

                println!("[ENTER] to send, or enter custom payload:");
                let mut confirm_input = String::new();
                io::stdin().read_line(&mut confirm_input).expect("Failed to read line");
                let confirm_input = confirm_input.trim();

                if confirm_input.is_empty() {
                    client.publish(&test_case.topic, QoS::AtLeastOnce, false, test_case.payload.to_string()).await.unwrap();
                    println!("Message sent to topic: {}", test_case.topic);
                } else {
                    let custom_payload = confirm_input;
                    client.publish(&test_case.topic, QoS::AtLeastOnce, false, custom_payload.to_string()).await.unwrap();
                    println!("Custom message sent to topic: {}", test_case.topic);
                }
            } else {
                eprintln!("No test value found for topic '{}'. Try again.", input);
            }
        }
    });

    Ok(())
}