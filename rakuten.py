# system imports
# import pprint
from collections import namedtuple
from typing import List

# 3rd parties imports
import requests


# Channel definition
CHANNEL_FIELDS = [
    "id",
    "numerical_id",
    "title",
    "type",
    "channel_number",
    "category",
    "language_ids",
]

Channel = namedtuple("Channel", CHANNEL_FIELDS)


class Api:
    api_scheme = "https"
    api_domain = "gizmo.rakuten.tv"
    api_base_path = "/v3"
    api_base_url = "{}://{}{}".format(
        api_scheme,
        api_domain,
        api_base_path
    )

    origin = "https://rakuten.tv"
    referer = "https://rakuten.tv/"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0"

    language = "es"


    @classmethod
    def get_live_channels(cls):
        path = "/live_channels"
        headers = {
            "Origin": cls.origin,
            "Referer": cls.referer,
            "User_Agent": cls.user_agent,
        }
        query = {
            "classification_id": 36,
            "device_identifier": "web",
            "locale": cls.language,
            "market_code": cls.language,
            "page": 1,
            "per_page": 100,
        }

        response = requests.get(
            cls.api_base_url + path,
            headers=headers,
            params=query,
        )

        return response.json()


    @classmethod
    def get_live_channel_categories(cls):
        path = "/live_channel_categories"
        headers = {
            "Origin": cls.origin,
            "Referer": cls.referer,
            "User_Agent": cls.user_agent,
        }
        query = {
            "classification_id": 36,
            "device_identifier": "web",
            "locale": cls.language,
            "market_code": cls.language
        }

        response = requests.get(
            cls.api_base_url + path,
            headers=headers,
            params=query,
        )

        return response.json()

    
    @classmethod
    def get_live_streaming(cls, channel: Channel, session: requests.Session = None):
        path = "/avod/streamings"
        headers = {
            "Origin": cls.origin,
            "Referer": cls.referer,
            "User_Agent": cls.user_agent,
        }
        query = {
            "classification_id": 36,
            "device_identifier": "web",
            "device_stream_audio_quality": "2.0",
            "device_stream_hdr_type": "NONE",
            "device_stream_video_quality": "FHD",
            "disable_dash_legacy_packages": False,
            "locale": cls.language,
            "market_code": cls.language
        }

        data = {
            "audio_language": channel.language_ids[0],
            "audio_quality": "2.0",
            "classification_id": "36",
            "content_id": channel.id,
            "content_type": "live_channels",
            "device_serial": "not implemented",
            "player": "web:HLS-NONE:NONE",
            "strict_video_quality": False,
            "subtitle_language": "MIS",
            "video_type": "stream"
        }

        if session:
            caller = session
        else:
            caller = requests
        
        response = caller.post(
            cls.api_base_url + path,
            headers=headers,
            params=query,
            json=data,
        )

        return response.json()


# methods
def map_channels_categories(api_response):
    categories = api_response.get("data", [])
    
    channels_categories_map = {}
    for category in categories:
        name = category.get("name", "no_category")
        channels = category.get("live_channels", [])

        for channel in channels:
            channels_categories_map[channel] = name
    
    return channels_categories_map


def map_channels_streams(channels: List[Channel]):
    session = requests.Session()

    ch_stream_map = {}

    for channel in channels:
        stream_url = Api.get_live_streaming(channel, session)\
            .get("data", {})\
            .get("stream_infos", [None])[0]\
            .get("url", "# no_url")

        ch_stream_map[channel.id] = stream_url
    
    return ch_stream_map


def get_channels():
    live_channels_raw = Api.get_live_channels()
    categories_raw = Api.get_live_channel_categories()

    # pprint.pprint(live_channels)
    # print("\n\n\n\n")
    # pprint.pprint(categories)
    
    # make channels/category lookup map
    cc_map = map_channels_categories(categories_raw)
    
    # list of all live channels
    ch_list: List(Channels) = []

    channels = live_channels_raw.get("data", [])
    for channel in channels:
        
        ch_id = channel.get("id", "no_id")

        ch_languages = channel.get("labels", {}).get("languages", [])
        langs = []

        for lang in ch_languages:
            langs.append(lang.get("id"))
        
        ch = Channel(
            id = ch_id,
            numerical_id = int(channel.get("numerical_id", -1)),
            title = channel.get("title", "no_title"),
            type = channel.get("type", "no_type"),
            channel_number = int(channel.get("channel_number", -1)),
            category = cc_map.get(ch_id, "no_category"),
            language_ids = langs,
        )

        ch_list.append(ch)

    # pprint.pprint(ch_list)
    return ch_list
