import requests
import json
import time
import sys
import dbus
import dbus.mainloop.glib
import gobject

USER_TOKEN = "Token YOUR_TOKEN"
url = 'https://api.listenbrainz.org/1/submit-listens'
prev = ''

def get_dict(track_name, artist_name):
    data = {"listen_type": "single", "payload": []}
    track_metadata = {"track_name": track_name, "artist_name": artist_name}
    data["payload"].append({"track_metadata": track_metadata})
    data["payload"][0]["listened_at"] = int(time.time())
    return data

def send(payload):
    r = requests.post(url, headers = {"Authorization": USER_TOKEN}, data = json.dumps(payload))
    if r.status_code != 200:
        print("error")
        print(r.text)

def changed(nxt):
    global prev
    return nxt != prev

def get_track_info():
    global iface
    return (iface.GetMetadata()["artist"], iface.GetMetadata()["title"])

def show_status(dummy):
    global iface
    status = iface.GetStatus()[0]
    if status == 2:
        msg = "stopped"
    else:
        track_data = get_track_info()
        if status == 0:
            msg = "playing {} - {}".format(track_data[0], track_data[1])
        elif status == 1:
            msg = "paused {} - {}".format(track_data[0], track_data[1])
    if changed(msg):
        if status == 0:
            print msg
            send(get_dict(track_data[1], track_data[0]))
        global prev
        prev = msg

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
session_bus = dbus.SessionBus()

player = session_bus.get_object('org.mpris.clementine', '/Player')
iface = dbus.Interface(player, dbus_interface='org.freedesktop.MediaPlayer')
iface.connect_to_signal("TrackChange", show_status)
iface.connect_to_signal("StatusChange", show_status)

mainloop = gobject.MainLoop()
try:
    mainloop.run()
except KeyboardInterrupt:
    sys.exit(0)
