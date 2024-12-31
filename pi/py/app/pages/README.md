# Dash Pages Architecture

This directory contains the UI elements that the user interacts with. The data on the pages dynamically get updated from external calls (MQTT/OPC UA) based on three different inputs:
-  Hydration. This is data that should be displayed ASAP on a page load, which does not change (often). For instance, displaying PLC version information needs an external OPC UA call to `ns=3;s=\"gtyp_Setup\".\"r_Version_SPS\"`. When this data is retrieved, it is stored and displayed and not expected to change anymore.
- Monitored data. This is data that constantly changes without direct user input, requiring regular updates to the UI. An example would be the status of the SLD in the factory (the sorting line), which requires a call to `f/i/state/sld`. 
- User interaction. This data is a direct response or feedback on something the user does. This data only updates very sporadically and only needs one positive poll [^1] (like the hydration data). An example would be an acknowledgement of a customer order.

## Asyncio with Dash

Both backend clients (MQTT and OPCUA) are asynchronous (and should be, because the time it will take to respond to a call is unpredictable and should not block rendering); however, Dash does not support asynchronous programming. Specifically, Dash callbacks (the ones that update the UI) cannot be async. To work around that, I have implemented a `RuntimeManager` and a polling mechanism. 

The `RuntimeManager` is relatively simple. It is a singleton[^2] that keeps an event loop to schedule async tasks in alive for the duration of the program, so that each Dash page can schedule async functions from a synchronous context without having to each have a separate event loop.

Making sure that the result of asynchronous functions gets back to the Dash callbacks is frankly absurdly difficult for something that on the surface should not be so hard. To do this, I have devised a polling mechanism[^3] that takes up the majority of the boilerplate code on each page. In short, the async call result gets stored sever-side in a globally accessible state variable, managed by the [PageStateManager](../page_state_manager.py). Then, the pages periodically poll this variable. 

1. Have one separate callback for hydration, which polls the state and has multiple `Output`s, one for each element that should be hydrated. This callback should quickly only raise `PreventUpdate` after a positive call. 
2. Have each user-incited call have a separate callback for polling the response. It should have some dirty bit mechanism that tells it to raise a `PreventUpdate`. Having separate callbacks simplifies the code (and also makes it longer unfortunately) and allows for for custom feedback UI/logic.
3. Have one callback that handles all monitoring data. It should never raise `PreventUpdate`, but it should return `no_update` for `Output`s that have no new data. It should also use a dirty-bit mechanism, but this time per-component.

The [PageStateManager](../page_state_manager.py) is the one that receives the results of the async callbacks and makes them accessible. It also handles dirty bit logic. Lastly, it polls hydration data and subscribes to MQTT topics so that hydration data is accessible even before the page loads, and monitoring data is also accessible the moment the Publish message is in.

I know this solution looks ridiculous, but I really have found no better solution. If you, dear reader, know something better, please let me know.

### Performance Motivation

The main overhead / congestion sources are the HTTP requests Dash needs to send out and receive to communicate between the Dash backend and the client-side (HTML/CSS/JS). In this application, using `dcc.Interval` causes a HTTP request each time the interval fires, and each update to the DOM also causes a request. Because Dash callbacks can only be triggered by the clientside, using `dcc.Interval` is, as far as I know, the only way to implement polling. 

What it comes down to is that the less `Interval` elements, the better. That is why each page gets its input from the singular `Interval` element in [app/app.py](../app.py). 

Furthermore, the less DOM updates the better. If multiple DOM mutations can be bundled into one callback `Output`, then it should be done. That is the reason for the wildly complicated lists `Output`s in some callbacks (like hydration callbacks).

*Note: I chose not to use `dcc.Store` because it is client-side storage, which means it would mean even more HTTP traffic between the client and the server.*
*At some point in the future, it would be preferable to use SocketIO to push data to the client-side, and receive this with JavaScript client-side scripts, that writes this pushed data to a `dcc.Store`, which the callbacks can take as input. This would allow for realtime-updates, and it would allow for the admittedly hideously complicated polling logic to be removed.*

[^1]: A positive poll is a data poll that does not return `None`. I.d., either a successful poll or an error response poll. 
[^2]: See `common/singleton_decorator.py`.
[^3]: I have tried a lot of other solutions as well, from trying to call Dash callbacks like regular functions in the `RuntimeManager`, to using flask's `SocketIO` Websockets (because callbacks can take Websocket inputs, unfortunately only the ones that are implemented as Dash elements)
