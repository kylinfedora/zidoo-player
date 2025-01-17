"""
Zidoo Remote Control API
By Wizmo
References
    oem v1: https://www.zidoo.tv/Support/developer/
    oem v2: http://apidoc.zidoo.tv/s/98365225
"""
import logging
import json
import socket
import struct
import requests
from datetime import datetime
from time import sleep
import urllib.parse

_LOGGER = logging.getLogger(__name__)

VERSION = "0.2.4"
TIMEOUT = 5  # default timeout
RETRIES = 3  # default retries
CONF_PORT = 9529  # default api port
DEFAULT_COUNT = 250  # default list limit
ZCMD_STATUS = "getPlayStatus"

"""Remote Control Button keys"""
ZKEY_BACK = "Key.Back"
ZKEY_CANCEL = "Key.Cancel"
ZKEY_HOME = "Key.Home"
ZKEY_UP = "Key.Up"
ZKEY_DOWN = "Key.Down"
ZKEY_LEFT = "Key.Left"
ZKEY_RIGHT = "Key.Right"
ZKEY_OK = "Key.Ok"
ZKEY_SELECT = "Key.Select"
ZKEY_STAR = "Key.Star"
ZKEY_POUND = "Key.Pound"
ZKEY_DASH = "Key.Dash"
ZKEY_MENU = "Key.Menu"
ZKEY_MEDIA_PLAY = "Key.MediaPlay"
ZKEY_MEDIA_STOP = "Key.MediaStop"
ZKEY_MEDIA_PAUSE = "Key.MediaPause"
ZKEY_MEDIA_NEXT = "Key.MediaNext"
ZKEY_MEDIA_PREVIOUS = "Key.MediaPrev"
ZKEY_NUM_0 = "Key.Number_0"
ZKEY_NUM_1 = "Key.Number_1"
ZKEY_NUM_2 = "Key.Number_2"
ZKEY_NUM_3 = "Key.Number_3"
ZKEY_NUM_4 = "Key.Number_4"
ZKEY_NUM_5 = "Key.Number_5"
ZKEY_NUM_6 = "Key.Number_6"
ZKEY_NUM_7 = "Key.Number_7"
ZKEY_NUM_8 = "Key.Number_8"
ZKEY_NUM_9 = "Key.Number_9"
ZKEY_USER_A = "Key.UserDefine_A"
ZKEY_USER_B = "Key.UserDefine_B"
ZKEY_USER_C = "Key.UserDefine_C"
ZKEY_USER_D = "Key.UserDefine_D"
ZKEY_MUTE = "Key.Mute"
ZKEY_VOLUME_UP = "Key.VolumeUp"
ZKEY_VOLUME_DOWN = "Key.VolumeDown"
ZKEY_POWER_ON = "Key.PowerOn"
ZKEY_MEDIA_BACKWARDS = "Key.MediaBackward"
ZKEY_MEDIA_FORWARDS = "Key.MediaForward"
ZKEY_INFO = "Key.Info"
ZKEY_RECORD = "Key.Record"
ZKEY_PAGE_UP = "Key.PageUP"
ZKEY_PAGE_DOWN = "Key.PageDown"
ZKEY_SUBTITLE = "Key.Subtitle"
ZKEY_AUDIO = "Key.Audio"
ZKEY_REPEAT = "Key.Repeat"
ZKEY_MOUSE = "Key.Mouse"
ZKEY_POPUP_MENU = "Key.PopMenu"
ZKEY_APP_MOVIE = "Key.movie"
ZKEY_APP_MUSIC = "Key.music"
ZKEY_APP_PHOTO = "Key.photo"
ZKEY_APP_FILE = "Key.file"
ZKEY_LIGHT = "Key.light"
ZKEY_RESOLUTION = "Key.Resolution"
ZKEY_POWER_REBOOT = "Key.PowerOn.Reboot"
ZKEY_POWER_OFF = "Key.PowerOn.Poweroff"
ZKEY_POWER_STANDBY = "Key.PowerOn.Standby"
ZKEY_PICTURE_IN_PICTURE = "Key.Pip"
ZKEY_SCREENSHOT = "Key.Screenshot"
ZKEY_APP_SWITCH = "Key.APP.Switch"
ZKEYS = [
    ZKEY_BACK,
    ZKEY_CANCEL,
    ZKEY_HOME,
    ZKEY_UP,
    ZKEY_DOWN,
    ZKEY_LEFT,
    ZKEY_RIGHT,
    ZKEY_OK,
    ZKEY_SELECT,
    ZKEY_STAR,
    ZKEY_POUND,
    ZKEY_DASH,
    ZKEY_MENU,
    ZKEY_MEDIA_PLAY,
    ZKEY_MEDIA_STOP,
    ZKEY_MEDIA_PAUSE,
    ZKEY_MEDIA_NEXT,
    ZKEY_MEDIA_PREVIOUS,
    ZKEY_NUM_0,
    ZKEY_NUM_1,
    ZKEY_NUM_2,
    ZKEY_NUM_3,
    ZKEY_NUM_4,
    ZKEY_NUM_5,
    ZKEY_NUM_6,
    ZKEY_NUM_7,
    ZKEY_NUM_8,
    ZKEY_NUM_9,
    ZKEY_USER_A,
    ZKEY_USER_B,
    ZKEY_USER_C,
    ZKEY_USER_D,
    ZKEY_MUTE,
    ZKEY_VOLUME_UP,
    ZKEY_VOLUME_DOWN,
    ZKEY_POWER_ON,
    ZKEY_MEDIA_BACKWARDS,
    ZKEY_MEDIA_FORWARDS,
    ZKEY_INFO,
    ZKEY_RECORD,
    ZKEY_PAGE_UP,
    ZKEY_PAGE_DOWN,
    ZKEY_SUBTITLE,
    ZKEY_AUDIO,
    ZKEY_REPEAT,
    ZKEY_MOUSE,
    ZKEY_POPUP_MENU,
    ZKEY_APP_MOVIE,
    ZKEY_APP_MUSIC,
    ZKEY_APP_PHOTO,
    ZKEY_APP_FILE,
    ZKEY_LIGHT,
    ZKEY_RESOLUTION,
    ZKEY_POWER_REBOOT,
    ZKEY_POWER_OFF,
    ZKEY_POWER_STANDBY,
    ZKEY_PICTURE_IN_PICTURE,
    ZKEY_SCREENSHOT,
    ZKEY_APP_SWITCH
]

"""Movie Player entry types"""
ZTYPE_VIDEO = 0
ZTYPE_MOVIE = 1
ZTYPE_COLLECTION = 2
ZTYPE_TV_SHOW = 3
ZTYPE_TV_SEASON = 4
ZTYPE_TV_EPISODE = 5
ZTYPE_OTHER = 6
ZTYPE_NAMES = {
    ZTYPE_VIDEO: "video",
    ZTYPE_MOVIE: "movie",
    ZTYPE_COLLECTION: "collection",
    ZTYPE_TV_SHOW: "tvshow",
    ZTYPE_TV_SEASON: "tvseason",
    ZTYPE_TV_EPISODE: "tvepisode",
    ZTYPE_OTHER: "other",
}

ZCONTENT_VIDEO = "Video Player"
ZCONTENT_MUSIC = "Music Player"
ZCONTENT_NONE = None

"""Movie Player search keys"""
ZVIDEO_FILTER_TYPES = {
    "all": 0,
    "favorite": 1,
    "watching": 2,
    "movie": 3,
    "tvshow": 4,
    "sd": 5,
    "bluray": 6,
    "4k": 7,
    "3d": 8,
    "children": 9,
    "recent": 10,
    "unwatched": 11,
    "other": 12,
    # ?"dolby": 13
}

ZVIDEO_SEARCH_TYPES = {
    # "all": -1,    # combined results
    "video": 0,  # all movies tvshows and collections
    "movie": 1,
    "tvshow": 2,
    "collection": 3,
}

ZMUSIC_SEARCH_TYPES = {
    "music": 0,
    "album": 1,
    "artist": 2,
    "playlist": 3
}

"""File System devicce type names"""
ZDEVICE_FOLDER = 1000
ZDEVICE_NAMES = {
    1000: "hhd",
    1001: "usb",
    1002: "usb",
    1003: "tf",
    1004: "nfs",
    1005: "smb",
}

ZFILETYPE_NAMES = {
    0: "folder",
    1: "music",
    2: "movie",
    3: "Image",
    4: "txt",
    5: "apk",
    6: "pdf",
    7: "doc",
    8: "xls",
    9: "ppt",
    10: "web",
    11: "zip",
    # default: "other",
}

ZTYPE_MIMETYPE = {
    "image": 3,
    "video": 2,
    "audio": 2, # 1 is Music Player but upnp needs dms server
    "other": 0,
    "default": 4,
    "application": 4,
}
ZUPNP_SERVERNAME = "zidoo-rc"

ZMEDIA_TYPE_ARTIST = "artist"
ZMEDIA_TYPE_ALBUM = "album"
ZMEDIA_TYPE_PLAYLIST = "playlist"

ZMUSIC_IMAGETYPE = {0: 0, 1: 1, 2: 0, 3: 0, 4: 1}
ZMUSIC_IMAGETARGET = {0: 16, 1: 16, 2: 32, 3: 16, 4: 32}
ZMUSIC_PLAYLISTTYPE = {
    ZMEDIA_TYPE_ARTIST: 3,
    ZMEDIA_TYPE_ALBUM: 4,
    ZMEDIA_TYPE_PLAYLIST: 5,
}


class ZidooRC(object):
    """Zidoo Media Player Remote Control"""
    def __init__(self, host, psk=None, mac=None):
        """Initialize the Zidoo class.
        Parameters
            mac:
                address is optional and can be used to manually assign the WOL address.
            psk:
                authorization passwortd key.  If not assigned, standard basic auth is used.
        """

        self._host = "{}:{}".format(host, CONF_PORT)
        self._mac = mac
        self._psk = psk
        self._cookies = None
        self._commands = []
        self._content_mapping = []
        self._current_source = None
        self._app_list = {}
        self._power_status = False
        self._video_id = -1
        self._music_id = -1
        self._music_type = -1
        self._last_video_path = None
        self._movie_info = {}
        self._current_subtitle = 0
        self._current_audio = 0

    def _jdata_build(self, method, params=None):
        if params:
            ret = json.dumps(
                {"method": method, "params": [params], "id": 1, "version": "1.0"}
            )
        else:
            ret = json.dumps(
                {"method": method, "params": [], "id": 1, "version": "1.0"}
            )
        return ret

    def connect(self, clientid="guest", nickname="Client"):
        """Connect to player and get authentication cookie.
        Parameters
            clientid: str
                id assigned to connection.
            nickname: str
                name assigned to connection.
        Returns
            json
                raw api response if sucessful.
        """
        authorization = json.dumps(
            {
                "method": "actRegister",
                "params": [
                    {"clientid": clientid, "nickname": nickname, "level": "private"},
                    [{"value": "yes", "function": "WOL"}],
                ],
                "id": 1,
                "version": "1.0",
            }
        ).encode("utf-8")

        headers = {"Connection": "keep-alive"}

        auth = None

        # if pin:
        #    auth = ('', pin)

        url = "http://{}/ZidooControlCenter/getModel".format(self._host)
        try:
            response = requests.post(
                url, data=authorization, headers=headers, timeout=TIMEOUT, auth=auth
            )
            response.raise_for_status()

        except requests.exceptions.Timeout as exception_instance:
            _LOGGER.info("[I] Timeout occurred: %s", str(exception_instance))
            self._cookies = None
            return None

        except requests.exceptions.HTTPError as exception_instance:
            _LOGGER.warning("[W] HTTPError: %s", str(exception_instance))
            return None

        except Exception as exception_instance:  # pylint: disable=broad-except
            _LOGGER.error("[W] Exception: %s", str(exception_instance))
            return None

        else:
            resp = response.json()
            _LOGGER.debug("connected: %s", resp)
            if resp is not None or resp.get("status") == 200:
                self._cookies = response.cookies
                if self._mac is None:
                    self._mac = resp.get("net_mac")
                self._power_status = True
                return resp

    def _recreate_auth_cookie(self):
        cookies = requests.cookies.RequestsCookieJar()
        cookies.set("auth", self._cookies.get("auth"))
        return cookies

    def is_connected(self):
        """Basic check for connection status.
        Returns
            bool
                True if connected.
        """
        if self._cookies is None:
            return False
        else:
            return True

    def _wakeonlan(self):
        """Sends WOL command to known mac addresses."""
        if self._mac is not None:
            addr_byte = self._mac.split(":")
            hw_addr = struct.pack(
                "BBBBBB",
                int(addr_byte[0], 16),
                int(addr_byte[1], 16),
                int(addr_byte[2], 16),
                int(addr_byte[3], 16),
                int(addr_byte[4], 16),
                int(addr_byte[5], 16),
            )
            msg = b"\xff" * 6 + hw_addr * 16
            socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_instance.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            socket_instance.sendto(msg, ("<broadcast>", 9))
            socket_instance.close()

    def _send_key(self, key, log_error=False):
        """Sends Remote Control button command to device.
        Parameters
            key: str
                remote control key command (see ZKEY list)
            log_error: bool
                suppesses error logging if False
        Returns
            True if sucessful
        """
        url = "ZidooControlCenter/RemoteControl/sendkey"
        params = {"key": key}

        response = self._req_json(url, params, log_error)

        if response and response.get("status") == 200:
            return True
        return False

    def _req_json(self, url, params={}, log_errors=True, timeout=TIMEOUT, max_retries=RETRIES):
        """Send request command via HTTP json to player.
        Parameters
            url: str
                api call.
            params: str
                api parameters.
            log_error: bool
                suppesses error logging if False
            max_retries
                reties on response errors
        Returns
            json
                raw API response
        """
        headers = {}
        if self._psk is not None:
            headers["X-Auth-PSK"] = self._psk

        url = "http://{}/{}".format(self._host, url)

        while max_retries > 0:
            try:
                # self._cookies = self._recreate_auth_cookie()
                response = requests.get(
                    url, params, cookies=self._cookies, timeout=timeout, headers=headers
                )

            except requests.exceptions.Timeout as exception_instance:
                if log_errors and self._power_status:
                    _LOGGER.info("[I] Timeout occurred: %s", str(exception_instance))

            except requests.exceptions.ConnectionError as exception_instance:
                if log_errors and self._power_status:
                    _LOGGER.info("[I] Connect occurred: %s", str(exception_instance))

            except requests.exceptions.HTTPError as exception_instance:
                if log_errors:
                    _LOGGER.warning("HTTPError: %s", str(exception_instance))

            except Exception as exception_instance:  # pylint: disable=broad-except
                if log_errors:
                    _LOGGER.error("Exception: %s", str(exception_instance))

            else:
                result = json.loads(response.content.decode("utf-8"))
                if result:
                    if ZCMD_STATUS not in url or result.get("status") != 804: # player can report 804 when switching media. force retry
                        return result
                _LOGGER.debug("URL Error for %s: %s", str(url), str(result))
                sleep(timeout)
            max_retries -= 1

        self._cookies = None  # forces reconnect on next update

    def get_source(self):
        """Returns last known app"""
        return self._current_source

    def load_source_list(self):
        """Returns app list."""
        return self.get_app_list()

    def select_source(self, source):
        """Set the input source. Not currently used."""
        if len(self._content_mapping) == 0:
            self._content_mapping = self.load_source_list()

        if source in self._content_mapping:
            uri = self._content_mapping[source]

    def get_playing_info(self):
        """Gets playing information of active app.
        Returns
            json (if successful)
                source: music = music player, video = vodeo player
                status: True if playing
                uri: path to current file
                title: title (filename)
                duration: length in ms
                position: position in ms
                artist: artist name(music only)
                track: track title (music only)
                type: ??
                movie_name: movie title (movie only)
                tag: tag line (movie only)
                date: release date (movie only)
                episode: episode number (tv only)
                episode_name: episode title (tv only)
                season: season number (tv only)
                season_name: season title (tv only)
                series_name: series title (tv only)
        """
        return_value = {}

        response = self._get_video_playing_info()
        if response is not None:
            return_value = response
            return_value["source"] = "video"
            if return_value.get("status") is True:
                self._current_source = ZCONTENT_VIDEO
                return {**return_value, **self._movie_info}

        response = self._get_music_playing_info()
        if response is not None:
            return_value = response
            return_value["source"] = "music"
            if return_value["status"] is True:
                self._current_source = ZCONTENT_MUSIC
                return return_value

        if not return_value:
            self._current_source = ZCONTENT_NONE

        return return_value

    def _get_video_playing_info(self):
        """Get information from built in video player."""
        return_value = {}
        response = self._req_json("ZidooVideoPlay/" + ZCMD_STATUS)

        if response is not None and response.get("status") == 200:
            if response.get("subtitle"):
                self._current_subtitle = response["subtitle"].get("index")
            if response.get("audio"):
                self._current_audio = response["audio"].get("index")
            if response.get("video"):
                result = response.get("video")
                return_value["status"] = result.get("status") == 1
                return_value["title"] = result.get("title")
                return_value["uri"] = result.get("path")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("currentPosition")
                return_value["width"] = result.get("width")
                return_value["height"] = result.get("height")
                return_value["fps"] = result.get("fps")
                return_value["bitrate"] = result.get("bitrate")
                return_value["audio"] = result.get("audioInfo")
                return_value["video"] = result.get("output")
                if (
                    return_value["status"] is True
                    and return_value["uri"]
                    and return_value["uri"] != self._last_video_path
                ):
                    self._last_video_path = return_value["uri"]
                    self._video_id = self._get_id_from_uri(self._last_video_path)
                result = response.get("zoom")
                return_value["zoom"] = result.get("information")
                return return_value
        # _LOGGER.debug("video play info: %s", str(response))

    def _get_id_from_uri(self, uri):
        """returns the movie id from the path"""
        movie_id = 0
        movie_info = {}

        response = self._req_json(
            "ZidooPoster/v2/getAggregationOfFile?path={}".format(
                urllib.parse.quote(uri)
            )
        )

        if response:
            movie_info["type"] = response.get("type")
            result = response.get("movie")
            if result is not None:
                movie_id = result.get("id")
                movie_info["movie_name"] = result.get("name")
                movie_info["tag"] = result["aggregation"].get("tagLine")
                release = result["aggregation"].get("releaseDate")
                if release:
                    movie_info["date"] = datetime.strptime(release, "%Y-%m-%d")
            result = response.get("episode")
            if result is not None:
                movie_id = result.get("id")
                movie_info["episode"] = result["aggregation"].get("episodeNumber")
                movie_info["episode_name"] = result["aggregation"].get("name")
            result = response.get("season")
            if result is not None:
                movie_info["season"] = result["aggregation"].get("seasonNumber")
                movie_info["season_name"] = result["aggregation"].get("name")
                movie_info["series_name"] = result["aggregation"].get("tvName")
            if not movie_id:
                result = response.get("video")
                if result is not None:
                    movie_id = result.get("parentId")

            self._movie_info = movie_info

        _LOGGER.debug("new media detected (%s): %s", str(movie_id), str(movie_info))
        return movie_id

    def _get_music_playing_info(self):
        """Get information from built in Music Player"""
        return_value = {}
        response = self._req_json("ZidooMusicControl/" + ZCMD_STATUS)

        if response is not None and response.get("status") == 200:
            return_value["status"] = response.get("isPlay")
            result = response.get("music")
            if result is not None:
                return_value["title"] = result.get("title")
                return_value["artist"] = result.get("artist")
                return_value["track"] = result.get("number")
                return_value["date"] = result.get("date")
                return_value["uri"] = result.get("uri")
                return_value["bitrate"] = result.get("bitrate")
                return_value["audio"] = "{}: {} channels {} bits {} Hz".format(
                    result.get("extension"),
                    result.get("channels"),
                    result.get("bits"),
                    result.get("SampleRate"),
                )
                self._music_id = result.get("id")
                self._music_type = result.get("type")

                result = response.get("state")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("position")

                result = response.get("state")
                if result is not None:
                    # update with satte - playing for newer firmware
                    return_value["status"] = result.get("playing")

                return return_value
        # _LOGGER.debug("music play info %s", str(response))

    def _get_movie_playing_info(self):
        """Get information from built in Movie Player."""
        return_value = {}

        response = self._req_json("ZidooControlCenter/" + ZCMD_STATUS)

        if response is not None and response.get("status") == 200:
            if response.get("file"):
                result = response.get("file")
                return_value["status"] = result.get("status") == 1
                return_value["title"] = result.get("title")
                return_value["uri"] = result.get("path")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("currentPosition")
                return return_value
        # _LOGGER.debug("movie play info {}".format(response))

    def get_play_modes(self):
        """Get the playmode list
        Returns
            json
                raw api response when successful
        """
        response = self._req_json("ZidooVideoPlay/getPlayModeList")

        if response is not None and response.get("status") == 200:
            return response

    def _next_data(self, data, index):
        """Toggle list"""
        temp = iter(data)
        for key in temp:
            if key == index:
                index = next(temp, 0)
                return index
        return 0

    def get_subtitle_list(self, log_errors=True):
        """Get the subtitle list
        Returns
            dictionary list
        """
        return_values = {}
        response = self._req_json(
            "ZidooVideoPlay/getSubtitleList", log_errors=log_errors
        )

        if response is not None and response.get("status") == 200:
            for result in response["subtitles"]:
                index = result.get("index")
                return_values[index] = result.get("title")

        return return_values

    def set_subtitle(self, index=None):
        """Start an subtitle
        Parameters
            index: int
                subtitle list reference
        Return
            True if sucessful
        """
        if index is None:
            index = self._next_data(self.get_subtitle_list(), self._current_subtitle)

        response = self._req_json(
            "ZidooVideoPlay/setSubtitle?index={}".format(index), log_errors=False
        )

        if response is not None and response.get("status") == 200:
            self._current_subtitle = index
            return True
        return False

    def get_audio_list(self):
        """Get the audio track list
        Returns
            dictionary
                list of audio tracks
        """
        return_values = {}
        response = self._req_json("ZidooVideoPlay/getAudioList")

        if response is not None and response.get("status") == 200:
            for result in response["subtitles"]:
                index = result.get("index")
                return_values[index] = result.get("title")

        return return_values

    def set_audio(self, index=None):
        """Select the audio track
        Parameters
            index: int
                audio track list reference
        Return
            True if sucessful
        """
        if index is None:
            index = self._next_data(self.get_audio_list(), self._current_audio)

        response = self._req_json(
            "ZidooVideoPlay/setAudio?index={}".format(index), log_errors=False
        )

        if response is not None and response.get("status") == 200:
            self._current_audio = index
            return True
        return False

    def get_system_info(self):
        """Get system information
        Returns
            json is successful
                'status': 200
                'model': model name
                'ip': ip address
                'net_mac': wired mac address
                'wif_mac': wifi mac address
                'language': system language
                'firmware': firmwate version
                'androidversion': os version
                'flash': flash/emmc memory size
                'ram':' ram memory size
                'ableRemoteSleep': network sleep compatible (buggy on Z9S)
                'ableRemoteReboot': network reboot compatible
                'ableRemoteShutdown': network shut down compatible
                'ableRemoteBoot': network boot compatible (wol)
                'pyapiversion': python api version
        """
        response = self._req_json("ZidooControlCenter/getModel")

        if response is not None and response.get("status") == 200:
            response["pyapiversion"] = VERSION
            return response

    def get_power_status(self):
        """Get power status
        Returns
            "on" when player is on
            "off" when player is not availblessful
        """
        self._power_status = False
        try:
            response = self.get_system_info()

            if response is not None:
                self._power_status = True

        except:  # pylint: disable=broad-except
            pass

        if self._power_status is True:
            return "on"
        return "off"

    def get_volume_info(self):
        """Get volume info. Not currently supported."""
        return None

    def set_volume_level(self, volume):
        """Set volume level. Not currently supported."""
        # api_volume = str(int(round(volume * 100)))
        return 0

    def get_app_list(self, log_errors=True):
        """Get the list of installed apps
        Results
            list of openable apps
                <app name>: <app_id>
        """
        return_values = {}

        response = self._req_json(
            "ZidooControlCenter/Apps/getApps", log_errors=log_errors
        )

        if response is not None and response.get("status") == 200:
            for result in response["apps"]:
                if result.get("isCanOpen"):
                    name = result.get("label")
                    return_values[name] = result.get("packageName")

        return return_values

    def start_app(self, app_name, log_errors=True):
        """Start an app by name
        Parameters
            app_name: str
                app list reference
        Return
            True if sucessful
        """
        if len(self._app_list) == 0:
            self._app_list = self.get_app_list(log_errors)
        if app_name in self._app_list:
            return self._start_app(self._app_list[app_name], log_errors=log_errors)
        return False

    def _start_app(self, app_id, log_errors=True):
        """Start an app by package name"""
        response = self._req_json(
            "ZidooControlCenter/Apps/openApp?packageName={}".format(app_id)
        )

        if response is not None and response.get("status") == 200:
            return True
        return False

    def get_device_list(self):
        """Return list of root file system devices.
        Returns
            json device list if sucessful
                'name': device name
                'path': device path
                'type': device type (see ZDEVICE_TYPE)
        """
        response = self._req_json("ZidooFileControl/getDevices")

        if response is not None and response.get("status") == 200:
            return response["devices"]

    def get_movie_list(self, filter_type=-1, max_count=DEFAULT_COUNT):
        """Return list of movies
        Parameters
            max_count: int
                maxumum number of list items
            filter_type: int or str
                see ZVIDEO_FILTER_TYPE
        Returns
            json
                raw API response if successful
        """

        def byId(e):
            return e["id"]

        if filter_type in ZVIDEO_FILTER_TYPES:
            filter_type = ZVIDEO_FILTER_TYPES[filter_type]

        # v2 http://{{host}}/Poster/v2/getAggregations?type=0&start=0&count=40
        response = self._req_json(
            "ZidooPoster/getVideoList?page=1&pagesize={}&type={}".format(
                max_count, filter_type
            )
        )

        if response is not None and response.get("status") == 200:
            if filter_type in {10, 11}:
                response["data"].sort(key=byId, reverse=True)
            return response

    def get_collection_list(self, movie_id):
        """Return video collection details
        Parameters
            movie_id: int
                database movie_id
        Returns
            json
                raw API response if successful
        """
        response = self._req_json("ZidooPoster/getCollection?id={}".format(movie_id))

        if response is not None and response.get("status") == 200:
            return response

    def get_movie_details(self, movie_id):
        """Return video details
        Parameters
            movie_id: int
                database movie_id
        Returns
            json
                raw API response (no status)
        """
        # v1 response = self._req_json("ZidooPoster/getDetail?id={}".format(movie_id))
        response = self._req_json("Poster/v2/getDetail?id={}".format(movie_id))

        if response is not None:  # and response.get("status") == 200:
            return response

    def get_episode_list(self, season_id):
        """Returns list video list sorted by episodes
        Parameters
            movie_id: int
                database movie_id
        Returns
            json:
                raw API episode list if successful
        """

        def byEpisode(e):
            return e["aggregation"]["episodeNumber"]

        response = self.get_movie_details(season_id)

        if response is not None:
            episodes = response.get("aggregations")
            if episodes is None:
                # try alternative location
                result = response.get("aggregation")
                if result is not None:
                    episodes = result.get("aggregations")

            if episodes is not None:
                episodes.sort(key=byEpisode)
                return episodes

    def _collection_video_id(self, movie_id):
        response = self.get_collection_list(movie_id)

        if response is not None:
            for result in response["data"]:
                if result["type"] == 0:
                    return result["aggregationId"]
        return movie_id

    def get_music_list(self, music_type=0, music_id=None, max_count=DEFAULT_COUNT):
        """Return list of movies
        Parameters
            max_count: int
                maxumum number of list items
            filter_type: int or str
                see ZVIDEO_FILTER_TYPE
        Returns
            json
                raw API response if successful
        """
        if music_type == ZMEDIA_TYPE_ARTIST:
            return self._get_artist_list(music_id, max_count)
        elif music_type == ZMEDIA_TYPE_ALBUM:
            return self._get_album_list(music_id, max_count)
        elif music_type == ZMEDIA_TYPE_PLAYLIST:
            return self._get_playlist_list(music_id, max_count)
        return self._get_song_list(max_count)

    def _get_song_list(self, max_count=DEFAULT_COUNT):
        """Return list of albums or album music
        Parameters
            max_count: int
                maxumum number of list items
        Returns
            json
                raw API response if successful
        """
        response = self._req_json(
            "MusicControl/v2/getSingleMusics?start=0&count={}".format(max_count)
        )

        if response is not None:
            return response

    def _get_album_list(self, album_id=None, max_count=DEFAULT_COUNT):
        """Return list of albums or album music
        Parameters
            album_id: int or str
                see ZVIDEO_FILTER_TYPE
            max_count: int
                maxumum number of list items
        Returns
            json
                raw API response if successful
        """
        if album_id:
            response = self._req_json(
                "MusicControl/v2/getAlbumMusics?id={}&start=0&count={}".format(
                    album_id, max_count
                )
            )
        else:
            response = self._req_json(
                "MusicControl/v2/getAlbums?start=0&count={}".format(max_count)
            )

        if response is not None:
            return response

    def _get_artist_list(self, artist_id=None, max_count=DEFAULT_COUNT):
        """Return list of artists or artist music
        Parameters
            max_count: int
                maxumum number of list items
            filter_type: int or str
                see ZVIDEO_FILTER_TYPE
        Returns
            json
                raw API response if successful
        """
        if artist_id:
            response = self._req_json(
                "MusicControl/v2/getArtistMusics?id={}&start=0&count={}".format(
                    artist_id, max_count
                )
            )
        else:
            response = self._req_json(
                "MusicControl/v2/getArtists?start=0&count={}".format(max_count)
            )

        if response is not None:  # and response.get("status") == 200:
            return response

    def _get_playlist_list(self, playlist_id=None, max_count=DEFAULT_COUNT):
        """Return list of playlists
        Parameters
            max_count: int
                maxumum number of list items
            filter_type: int or str
                see ZVIDEO_FILTER_TYPE
        Returns
            json
                raw API response if successful
        """
        if playlist_id:
            if playlist_id == "playing":
                response = self._req_json(
                    "MusicControl/v2/getPlayQueue?start=0&count={}".format(max_count)
                )
            else:
                response = self._req_json(
                    "MusicControl/v2/getSongListMusics?id={}&start=0&count={}".format(
                        playlist_id, max_count
                    )
                )
        else:
            response = self._req_json(
                # "MusicControl/v2/getSongList?start=0&count={}".format(max_count)
                "MusicControl/v2/getSongLists"
            )

        if response is not None:
            return response

    def search_movies(self, query, search_type=0, max_count=DEFAULT_COUNT):
        """Return video details
        Parameters
            movie_id: int
                database movie_id
            search_type: int ot str
                see ZVIDEO_SEARCH_TYPES
        Returns
            json
                raw API response (no status)
        """
        if search_type in ZVIDEO_SEARCH_TYPES:
            search_type = ZVIDEO_SEARCH_TYPES[search_type]

        # v1 "ZidooPoster/search?q={}&type={}&page=1&pagesize={}".format(query, filter_type, max_count)
        response = self._req_json(
            "Poster/v2/searchAggregation?q={}&type={}&start=0&count={}".format(
                query, search_type, max_count
            )
        )

        if response is not None and response.get("status") == 200:
            return response

    def search_music(self, query, search_type=0, max_count=DEFAULT_COUNT):
        """search music
        Parameters
            query: str
                text to search
            search_type: int or str
                see ZMUSIC_SEARCH_TYPES
            max_count: int
                max number of songs returned
        Returns
            json
                raw API response (no status)
        """
        if search_type in ZMUSIC_SEARCH_TYPES:
            search_type = ZMUSIC_SEARCH_TYPES[search_type]

        if search_type == 1:
            return self._search_album(query, max_count)
        elif search_type == 2:
            return self._search_artist(query, max_count)
        return self._search_song(query, max_count)

    def _search_song(self, query, max_count=DEFAULT_COUNT):
        """get search list on song title
        Parameters
            query: str
                text to search
        Returns
            json
                raw API response (no status)
        """
        response = self._req_json(
            "MusicControl/v2/searchMusic?key={}&start=0&count={}".format(
                query, max_count
            )
        )

        if response is not None:  # and response.get("status") == 200:
            return response

    def _search_album(self, query, max_count=DEFAULT_COUNT):
        """get search list on album name
        Parameters
            query: str
                text to search
        Returns
            json
                raw API response (no status)
        """
        response = self._req_json(
            "MusicControl/v2/searchAlbum?key={}&start=0&count={}".format(
                query, max_count
            ),
            timeout=10,
        )

        if response is not None:  # and response.get("status") == 200:
            return response

    def _search_artist(self, query, max_count=DEFAULT_COUNT):
        """get serach list on artist name
        Parameters
            query: str
                text to search
        Returns
            json
                raw API response (no status)
        """
        response = self._req_json(
            "MusicControl/v2/searchArtist?key={}&start=0&count={}".format(
                query, max_count
            )
        )

        if response is not None:  # and response.get("status") == 200:
            return response

    def play_file(self, uri):
        """Play content by URI.
        Parameters
            uri: str
                path of file to play.
        Returns
            True if sucessful
        """
        url = "ZidooFileControl/openFile?path={}&videoplaymode={}".format(uri, 0) # has issues with parsing for local files

        response = self._req_json(url)

        if response and response.get("status") == 200:
            return True
        return False

    def play_stream(self, uri, media_type):
        """Play url by type
        Uses undocumented v2 upnp FileOpen calls using 'res' and 'type'
            res: str = quoted url
            type : int = app launch
            other information parameters can be used
                name: str (title?)
                date: datetime
                resolution: <width>x<height>
                bitrate: int (audio?)
                size: int (duration?)
                channels: int (audio?)
                bitRates: int (audio?)
                way: {0,1,2,3} (play mode?)
                album: str
                number: int (audio)
                sampleRates: int (audio)
                albumArt: url (audio)
        Parmeters:
            uri: str
                uri link to stream
            media_type: int
                See ZTYPE_MIMETYPE
        Returns
            True if sucessful
        """
        # the res uri needs to be double quoted to protect keys etc.
        # use safe='' in quote to force "/" quoting
        uri = urllib.parse.quote(uri, safe="")

        upnp = "upnp://{}/{}?type={}&res={}".format(
            ZUPNP_SERVERNAME, VERSION, media_type, uri
        )
        url = "ZidooFileControl/v2/openFile?url={}".format(
            urllib.parse.quote(upnp, safe="")
        )
        _LOGGER.debug("Stream command %s", str(url))

        response = self._req_json(url)

        if response and response.get("code") == 0:
            return True
        return False

    def play_movie(self, movie_id, video_type=-1):
        """Play video content by Movie id.
        Parameters
            movie_id
                database id
        Returns
            True if sucessfuL
        """
        # uses the agreggateid to find the first video to play
        if video_type != 0:
            movie_id = self._collection_video_id(movie_id)
        # print("Video id : {}".format(video_id))

        # v2 http://{}/VideoPlay/playVideo?index=0
        response = self._req_json(
            "ZidooPoster/PlayVideo?id={}&type={}".format(movie_id, video_type)
        )

        if response and response.get("status") == 200:
            return True
        return False

    def play_music(self, media_id, media_type="music", music_id=None):
        """Play video content by id.
        Parameters
            media_id
                database id for media type (or ids for music type)
            media_type
                see ZMUSIC_SEARCH_TYPE
            music_id
                database id for track to play (use None or -1 for first)
        Returns
            True if sucessfuL
        """
        if media_type in ZMUSIC_PLAYLISTTYPE:
            response = self._req_json(
                "MusicControl/v2/playMusic?type={}&id={}&musicId={}&music_type=0&trackIndex=1&sort=0".format(
                    ZMUSIC_PLAYLISTTYPE[media_type], media_id, music_id
                )
            )
        else:  # music
            response = self._req_json(
                "MusicControl/v2/playMusics?ids={}&musicId={}&trackIndex=-1".format(
                    media_id, music_id
                )
            )

        if response and response.get("status") == 200:
            return True
        return False

    def get_video_playlist(self):
        """get the current video playlist
        Returns
            json if successful
                'status': 200
                'size': count
                'playList' : array
                    'title': video name (file name)
                    'index': int
        """
        response = self._req_json("VideoPlay/getPlaylist")

        if response and response.get("status") == 200:
            return response

    def get_music_playlist(self, max_count=DEFAULT_COUNT):
        """Gets the current music player playlist
        Parameters
            max_count: int
                list size limit
        Returns
            raw api response if sucessful
        """
        response = self._req_json(
            "MusicControl/v2/getPlayQueue?start=0&count={}".format(max_count)
        )

        if response is not None and response.get("status") == 200:
            return response

    def get_file_list(self, uri, file_type=0):
        """get file list in hass format
        Returns
            json if sucessful
                'status':200
                'isExists':True
                'perentPath':'/storage/356d9775-8a40-4d4e-8ef9-9eea931fc5ae'
                'filelist': list
                    'name': file name
                    'type': file type
                    'path': full file path
                    'isBDMV': True if ?high definition
                    'isBluray': True if blue ray resolution
                    'length': length in ms
                    'modifyDate': linux date code
        """
        response = self._req_json(
            "ZidooFileControl/getFileList?path={}&type={}".format(uri, file_type)
        )

        if response is not None and response.get("status") == 200:
            return response

    def get_host_list(self, uri, host_type=1005):
        """get host list of saved network shares
        Returns
            json if sucessful
                'status':200
                'filelist': list
                    'name': host/share name
                    'type': file type
                    'path': full file path
                    'isBDMV': True if ?high definition
                    'isBluray': True if blue ray resolution
                    'length': length in ms
                    'modifyDate': linux date code
        """
        response = self._req_json(
            "ZidooFileControl/getHost?path={}&type={}".format(uri, host_type)
        )
        _LOGGER.debug("zidoo host list: %s", str(response))

        return_value = {}
        share_list = []
        if response is not None and response.get("status") == 200:
            return_value["status"] = 200
            hosts = response["hosts"]
            for item in hosts:
                response = self.get_file_list(item.get("ip"), item.get("type"))
                hostname = item.get("name").split("/")[-1]
                if response is not None and response.get("status") == 200:
                    for share in response["filelist"]:
                        share["name"] = hostname + "/" + share.get("name")
                        share_list.append(share)
        return_value["filelist"] = share_list
        return return_value

    def generate_image_url(self, media_id, media_type, width=400, height=None):
        """Get link to thumbnail"""
        if media_type in ZVIDEO_SEARCH_TYPES:
            if height is None:
                height = width * 3 / 2
            return self._generate_movie_image_url(media_id, width, height)
        if media_type in ZMUSIC_SEARCH_TYPES:
            if height is None:
                height = width
            return self._generate_music_image_url(
                media_id, ZMUSIC_SEARCH_TYPES[media_type], width, height
            )

    def _generate_movie_image_url(self, movie_id, width=400, height=600):
        """Get link to thumbnail
        Parameters
            movie_id: int
                dtanabase id
            width: int
                image width in pixels
            height: int
                image height in pixels
        Returns
            url for image
        """
        # http://{}/Poster/v2/getPoster?id=66&w=60&h=30
        url = "http://{}/ZidooPoster/getFile/getPoster?id={}&w={}&h={}".format(
            self._host, movie_id, width, height
        )

        return url

    def _generate_music_image_url(self, music_id, music_type=0, width=200, height=200):
        """Get link to thumbnail
        Parameters
            music_id: int
                dtanabase id
            width: int
                image width in pixels
            height: int
                image height in pixels
        Returns
            url for image
        """
        url = "http://{}/ZidooMusicControl/v2/getImage?id={}&music_type={}&type={}&target={}".format(
            self._host,
            music_id,
            ZMUSIC_IMAGETYPE[music_type],
            music_type,
            ZMUSIC_IMAGETARGET[music_type],
        )

        return url

    def generate_current_image_url(self, width=1080, height=720):
        """Gets link to artwork
        Parameters
            movie_id: int
                dtanabase id
            width: int
                image width in pixels
            height: int
                image height in pixels
        Returns
            url for image
        """
        url = None

        if self._current_source == ZCONTENT_VIDEO and self._video_id > 0:
            url = "http://{}/ZidooPoster/getFile/getBackdrop?id={}&w={}&h={}".format(
                self._host, self._video_id, width, height
            )

        if self._current_source == ZCONTENT_MUSIC and self._music_id > 0:
            url = "http://{}/ZidooMusicControl/v2/getImage?id={}&music_type={}&type=4&target=16".format(
                self._host, self._music_id, self._music_type
            )

        # _LOGGER.debug("zidoo getting current image: url-{}".format(url))
        return url

    def turn_on(self):
        """Turn the media player on."""
        # Try using the power on command incase the WOL doesn't work
        self._send_key(ZKEY_POWER_ON, False)
        self._wakeonlan()

    def turn_off(self, standby=False):
        """Turn off media player."""
        key = ZKEY_POWER_OFF
        if standby:
            key = ZKEY_POWER_STANDBY
        self._send_key(key)

    def volume_up(self):
        """Volume up the media player."""
        self._send_key(ZKEY_VOLUME_UP)

    def volume_down(self):
        """Volume down media player."""
        self._send_key(ZKEY_VOLUME_DOWN)

    def mute_volume(self):
        """Send mute command."""
        self._send_key(ZKEY_MUTE)

    def media_play(self):
        """Send play command."""
        # self._send_key(ZKEY_OK)
        if self._current_source == ZCONTENT_NONE and self._last_video_path:
            self.play_file(self._last_video_path)
        elif (self._current_source == ZCONTENT_MUSIC):
            self._req_json("MusicControl/v2/playOrPause")
        else:
            self._send_key(ZKEY_MEDIA_PLAY)

    def media_pause(self):
        """Send media pause command to media player."""
        if (self._current_source == ZCONTENT_MUSIC):
            self._req_json("MusicControl/v2/playOrPause")
        else:
            self._send_key(ZKEY_MEDIA_PAUSE)

    def media_stop(self):
        """Send media pause command to media player."""
        self._send_key(ZKEY_MEDIA_STOP)

    def media_next_track(self):
        """Send next track command."""
        if (self._current_source == ZCONTENT_MUSIC):
            self._req_json("MusicControl/v2/playNext")
        else:
            self._send_key(ZKEY_MEDIA_NEXT)

    def media_previous_track(self):
        """Send the previous track command."""
        if (self._current_source == ZCONTENT_MUSIC):
            self._req_json("MusicControl/v2/playLast")
        else:
            self._send_key(ZKEY_MEDIA_PREVIOUS)

    def set_media_position(self, position, durationsec=1):
        """Set the current playing position.
        Parameters
            position
                position in ms
        Return
            True if sucessful
        """
        if self._current_source == ZCONTENT_VIDEO:
            response = self._set_movie_position(position)
        elif self._current_source == ZCONTENT_MUSIC:
            response = self._set_audio_position(position)

        if response is not None:
            return True
        return False

    def _set_movie_position(self, position):
        """Set current posotion for video player"""
        response = self._req_json(
            "ZidooVideoPlay/seekTo?positon={}".format(int(position))
        )

        if response is not None and response.get("status") == 200:
            return response

    def _set_audio_position(self, position):
        """Set current position for music player"""
        response = self._req_json(
            "ZidooMusicControl/seekTo?time={}".format(int(position))
        )

        if response is not None and response.get("status") == 200:
            return response
