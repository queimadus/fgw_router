# fgw_router
Home Assistant device_tracker implementation for Altice Fiber Gateway GR241AG

![router](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQbkuz3EpT-XWHLZlPKgxVSAcrZgd8pn8j7yg&usqp=CAU)

### Installation
It's recommended to install this via [HACS](https://github.com/custom-components/hacs).
This repository is part of the defaults and can be found by searching for `fgw_router`.

### Configuration

#### Add the following to the `configuration.yaml`:

```
device_tracker:
  - platform: fgw_router
    host: 192.168.1.254
    port: 23
    username: !secret fgw_router_username
    password: !secret fgw_router_password
    interval_seconds: 60
    new_device_defaults:
      track_new_devices: false
```

#### Update your `secrets.yaml`:

If you haven't changed the default credentials, these are the default ones

```
fgw_router_username: meo
fgw_router_password: meo
```

#### Edit `known_devices.yaml`:

This file gets populated over time, as devices are tracked by the router. 
Change the devices you're interested in tracking to `track: true`.

```
ea_60_b2_1b_cd_23:
  name: ea_60_b2_1b_cd_23
  mac: EA:60:B2:1B:CD:23
  icon:
  picture:
  track: true
```

#### Restart Home assistant

Restart so the changes can take place.
