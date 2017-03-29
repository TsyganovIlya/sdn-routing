def launch():
    from log.level import launch
    launch(DEBUG=True)

    from samples.pretty_log import launch
    launch()

    from openflow.keepalive import launch
    launch(interval=15)

    from openflow.discovery import launch
    launch()

    from sdnrouting.yen_routing import launch
    launch(l3_matching=False)
