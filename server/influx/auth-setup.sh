#!/bin/bash

# Usage function
usage() {
  echo "Usage: $0 -e [prod|dev] -p <password> -t <token>"
  exit 1
}

# Parse command line arguments
while getopts "e:p:t:" opt; do
  case ${opt} in
    e)
      ENVIRONMENT=$OPTARG
      ;;
    p)
      PASSWORD=$OPTARG
      ;;
    t)
      TOKEN=$OPTARG
      ;;
    *)
      usage
      ;;
  esac
done

# Validate the required arguments
if [[ -z "$ENVIRONMENT" || -z "$PASSWORD" || -z "$TOKEN" ]]; then
  usage
fi

# Set the telegraf configuration file based on the environment
if [ "$ENVIRONMENT" == "dev" ]; then
  TELEGRAF_CONF="telegraf/telegraf.dev.conf"
elif [ "$ENVIRONMENT" == "prod" ]; then
  TELEGRAF_CONF="telegraf/telegraf.prod.conf"
else
  echo "Invalid environment specified. Use 'prod' or 'dev'."
  exit 1
fi

# Write the password to the Docker Compose file
COMPOSE_FILE="compose.yaml"
sed -i "s/DOCKER_INFLUXDB_INIT_PASSWORD: .*/DOCKER_INFLUXDB_INIT_PASSWORD: $PASSWORD/" $COMPOSE_FILE

# Write the token to the telegraf configuration file
sed -i "s/token = .*/token = \"$TOKEN\"/" $TELEGRAF_CONF

# Modify the Docker Compose file to use the correct telegraf configuration file
if [ "$ENVIRONMENT" == "dev" ]; then
  sed -i "s|\./telegraf.prod.conf:/etc/telegraf/telegraf.conf|./telegraf.dev.conf:/etc/telegraf/telegraf.conf|" $COMPOSE_FILE
elif [ "$ENVIRONMENT" == "prod" ]; then
  sed -i "s|\./telegraf.dev.conf:/etc/telegraf/telegraf.conf|./telegraf.prod.conf:/etc/telegraf/telegraf.conf|" $COMPOSE_FILE
fi

echo "Configuration updated successfully."
