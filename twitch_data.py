import time
import requests
from cookies import get_cookie_value
from exceptions import StreamerIsOfflineException, StreamerDoesNotExistException


TWITCH_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"

streamer_logins = []  # the list is sorted by priorities: more important streamers go first
online_streamers = []  # ditto
last_offline_time = {}  # the time when each streamer went offline (if they did)


# specify the streamers we'll be watching
def set_streamer_logins(streamer_logins_):
    global streamer_logins
    streamer_logins = streamer_logins_
    for streamer_login in streamer_logins:
        check_online(streamer_login, print_offline_message=True)


def get_streamer_logins():
    return streamer_logins


def do_for_each_streamer(function, args=None):
    if args is None:
        args = []
    for streamer_login in get_streamer_logins():
        function(streamer_login, *args)


def check_online(streamer_login, print_offline_message=False):
    # Twitch API has a delay for querying channels. If a query is made right after the streamer went offline,
    # it will cause a false "streamer is live" event.
    if time.time() < last_offline_time.get(streamer_login, 0) + 60:
        return

    if not is_online(streamer_login):
        # maintain the priorities of streamers
        online_streamers.append(streamer_login)
        online_streamers.sort(key=lambda streamer: streamer_logins.index(streamer))

        try:
            from watch_minute import update_minute_watched_event_request  # circular dependencies
            update_minute_watched_event_request(streamer_login)
        except StreamerIsOfflineException:
            set_offline(streamer_login, print_offline_message)
        else:
            print(f"{streamer_login} is live!")


def set_offline(streamer_login, print_offline_message=True):
    if is_online(streamer_login):
        online_streamers.remove(streamer_login)
        last_offline_time[streamer_login] = time.time()

        if print_offline_message:
            print(f"{streamer_login} is offline currently.")


def is_online(streamer_login):
    return streamer_login in online_streamers


def get_user_id():
    return int(get_cookie_value("persistent").split("%")[0])


channel_id_by_login = {}
login_by_channel_id = {}


def get_channel_id(streamer_login):
    if streamer_login not in channel_id_by_login:
        r = requests.get(f"https://api.twitch.tv/helix/users?login={streamer_login}",
                         headers={"Authorization": "Bearer " + get_auth_token(),
                                  "Client-Id": get_client_id()})
        data = r.json()["data"]
        if len(data) >= 1:
            channel_id = data[0]["id"]
            channel_id_by_login[streamer_login] = channel_id
            login_by_channel_id[channel_id] = streamer_login
        else:
            raise StreamerDoesNotExistException
    return channel_id_by_login[streamer_login]


def get_streamer_ids():
    return login_by_channel_id.keys()


def get_login_by_channel_id(channel_id):
    return login_by_channel_id[channel_id]


def get_broadcast_id(streamer_login):
    from claim_bonus import post_gql_request  # circular imports
    json_data = {"operationName": "WithIsStreamLiveQuery",
                 "variables": {"id": get_channel_id(streamer_login)},
                 "extensions": {"persistedQuery": {"version": 1,
                                                   "sha256Hash": "04e46329a6786ff3a81c01c50bfa5d725902507a0deb83b0edbf7abe7a3716ea"}}}
    response = post_gql_request(json_data)
    stream = response["data"]["user"]["stream"]
    if stream is not None:
        return stream["id"]
    else:
        raise StreamerIsOfflineException


def get_streamer_url(streamer_login):
    return f"https://www.twitch.tv/{streamer_login}"


def get_auth_token():
    return get_cookie_value("auth-token")


def get_client_id():
    return TWITCH_CLIENT_ID