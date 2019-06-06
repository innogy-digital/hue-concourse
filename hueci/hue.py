import json

import requests

HUE_COLOR_RED = 0
HUE_COLOR_GREEN = 21845
HUE_COLOR_BLUE = 43690
HUE_COLOR_YELLOW = 10833


class Hue:
    def __init__(self, url, username):
        self.__url = url
        self.__username = username
        self.__lights = []

    def update_lights(self):
        self.__lights = self.__get_lights()

    def set_success(self, lightId):
        self.__set_light_state(lightId, HUE_COLOR_GREEN)

    def set_failed(self, lightId):
        self.__set_light_state(lightId, HUE_COLOR_RED, 'lselect')

    def set_started(self, lightId):
        self.__set_light_state(lightId, HUE_COLOR_YELLOW, 'lselect')

    def __light_id_from_id_or_name(self, lightIdOrName):
        if type(lightIdOrName) is str:
            nameToId = self.__map_light_names_to_ids()
            return nameToId[lightIdOrName]
        else:
            return lightIdOrName

    def __get_lights(self):
        response = requests.get(self.__url + "/api/" + self.__username + "/lights")
        return json.loads(response.content)

    def __map_light_names_to_ids(self):
        names = {}
        for i in self.__lights:
            name = self.__lights[i].get("name")
            names[name] = i
        return names

    def __set_light_state(self, lightIdsOrNames, color, alert='select'):
        if not type(lightIdsOrNames) is list:
            lightIdsOrNames = [lightIdsOrNames]

        for lightIdOrName in lightIdsOrNames:
            lightId = self.__light_id_from_id_or_name(lightIdOrName)

            state = self.__lights[lightId]["state"]
            if not state \
                or not state["on"] \
                or state["hue"] != color \
                or state["alert"] != alert:
                requests.put(self.__url + "/api/" + self.__username + "/lights/" + str(lightId) + "/state",
                             json={"on": True,
                                   "hue": color,
                                   "sat": 254,  # Saturation
                                   "bri": 254,  # Brightness
                                   "alert": alert
                                   },
                             headers={'Content-type': 'application/json'})
