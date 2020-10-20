import requests
from exceptions import StreamerDoesNotExistException
from twitch_data import get_auth_token, get_channel_id, USER_AGENT, get_client_id


# For documentation on Twitch GraphQL API see:
# https://www.apollographql.com/docs/
# https://github.com/mauricew/twitch-graphql-api
# Full list of available methods: https://azr.ivr.fi/schema/query.doc.html (a bit outdated)


def claim_channel_points_bonus(streamer_login, claim_id):
    print(f"Claiming the bonus for {streamer_login}!")
    json_data = {"operationName": "ClaimCommunityPoints",
                 "variables": {"input": {"channelID": get_channel_id(streamer_login), "claimID": claim_id}},
                 "extensions": {"persistedQuery": {"version": 1, "sha256Hash": "46aaeebe02c99afdf4fc97c7c0cba964124bf6b0af229395f1f6d1feed05b3d0"}}}
    post_gql_request(json_data)


# Load the amount of current points for a channel, check if a bonus is available
def load_channel_points_context(streamer_login):
    json_data = {"operationName": "ChannelPointsContext",
                 "variables": {"channelLogin": streamer_login},
                 "extensions": {"persistedQuery": {"version": 1, "sha256Hash": "9988086babc615a918a1e9a722ff41d98847acac822645209ac7379eecb27152"}}}
    response = post_gql_request(json_data)
    if response["data"]["community"] is None:
        raise StreamerDoesNotExistException
    community_points = response["data"]["community"]["channel"]["self"]["communityPoints"]
    initial_balance = community_points["balance"]
    print(f"{initial_balance} channel points for {streamer_login}!")
    available_claim = community_points["availableClaim"]
    if available_claim is not None:
        claim_id = available_claim["id"]
        claim_channel_points_bonus(streamer_login, claim_id)


def post_gql_request(json_data):
    r = requests.post("https://gql.twitch.tv/gql",
                      json=json_data,
                      headers={"Authorization": "OAuth " + get_auth_token(),
                               "Client-Id": get_client_id(),
                               "User-Agent": USER_AGENT})
    return r.json()
