# HTTP/REST

HTTP is used to query data from InfluxDB, GraphDB and the AAS server.

## InfluxDB

InfluxDB OSS exposes its data with a REST API out-of-the-box. [You can read the official documentation here](https://docs.influxdata.com/influxdb/v2/api/). 

For local development, you need to make sure InfluxDB is running at localhost:8086 with `$ influxd` first, with the correct authorization (see the [documentation for setting up InfluxDB in the ReMan lab](/server/influx/README.md)).

After that, you can query the database like so:

- `URL`: http://localhost:8086/api/v2/query?orgID=80627e52d150f118
- `Headers`:

Key | Value
-|-
Authorization | Token ****
Content-type | application/json
- `Body`:
```
{
    "query": "from(bucket: \"FischerFactory\") |> range(start: -30d) |> filter(fn: (r) => r[\"_field\"] == \"inOven\")"
}
```

Replace **** with your actual auth token. The Flux query in the body is also just an example query - in this case it filters on datapoints that have an "inOven" field.

*Note: During production, the URL is obviously not going to be `localhost:8086`. However, the central server has not been purchased as of yet, so the IP address during production is not yet known.*

### Measurements
The measurements in InfluxDB mirror the exact [structure of the MQTT messages](/schemas/mqtt/README.md) they are generated from. The following measurements are stored in the InfluxDB database:
- `dsi` - from `f/i/state/dsi`
- `dso` - from `f/i/state/dso`
- `mpo` - from `f/i/state/mpo`
- `sld` - from `f/i/state/sld`
- `vgr` - from `f/i/state/vgr`
- `hbw` - from `f/i/state/hbw`

The measurements also have a `topic` tag with the full path of the MQTT topic they were generated from. This can be used for filtering.

## GraphDB

## AAS Basyx
