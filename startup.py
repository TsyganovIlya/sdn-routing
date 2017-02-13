from datetime import datetime

def launch (postfix=datetime.now().strftime("%Y%m%d%H%M%S")):
        from log.level import launch
        launch(DEBUG=True)

        from samples.pretty_log import launch
        launch()

        from openflow.keepalive import launch
        launch(interval=15)  # 15 seconds

        from openflow.discovery import launch
        launch()

        from sdnrouting.forwarding import launch
        launch(l3_matching=False)

