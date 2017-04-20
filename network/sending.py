import socket


__all__ = [
    "send_islands",
    "send_route",
    "send_paths",
    "send_metric",
    "send_pt",
]


def send_metric(s1, metric, s2):
    send("Metric", "{},{},{}".format(s1, metric, s2))


def send_islands(islands):
    send("Islands", islands)


def send_route(route):
    send("Path", repr(route))


def send_paths(route):
    send("Paths", repr(route))


def send_pt(pt):
    send("PT", str(pt))


def send(command_head, command_body):
    sender = socket.socket()
    try:
        sender.connect(('127.0.0.1', 6111))
        sender.send(command_head + ":" + command_body)
    except socket.error as e:
        print('Caught exception socket.error: {0}'.format(e))
    finally:
        sender.close()
