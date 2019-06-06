#!/usr/bin/env python

import json
import time

import BaseHTTPServer
import requests
from urlparse import parse_qs

HUE_USERNAME = "XXX"
HUE_IP = "192.168.2.100"

HUE_COLOR_RED = 0
HUE_COLOR_GREEN = 21845
HUE_COLOR_BLUE = 43690
HUE_COLOR_YELLOW = 11845

CI_TOKEN = None  # set via raw_input / http callback

LAB = {
    "hydrodata4all": "dlab 2.1",
    "BeMa": "dlab 2.2",  # 2.4
    # 'TICM': 2,
    'aspekt': "dlab 2.3"
}


# TODO
# - ein team -> mehrere lampen
# - mehrere projekte -> mehrere lampen
# - check state before change

def __hueGetLights():
    response = requests.get("http://" + HUE_IP + "/api/" + HUE_USERNAME + "/lights")
    return json.loads(response.content)


def __hueLightNameToId():
    lights = __hueGetLights()
    names = {}
    for i in lights:
        name = lights[i].get("name")
        names[name] = i
    return names


def __hueSetState(lightId, color, alert='none'):
    response = requests.put("http://" + HUE_IP + "/api/" + HUE_USERNAME + "/lights/" + str(lightId) + "/state",
                            json={"on": True,
                                  "hue": color,
                                  "sat": 254,  # Saturation
                                  "bri": 254,  # Brightness
                                  "alert": alert
                                  },
                            headers={'Content-type': 'application/json'})


def hueSetSuccess(lightId):
    print(lightId, ' -> green')
    __hueSetState(lightId, HUE_COLOR_GREEN)


def hueSetFailed(lightId):
    print(lightId, ' -> red')
    __hueSetState(lightId, HUE_COLOR_RED, 'select')


def hueSetStarted(lightId):
    print(lightId, ' -> blink')
    __hueSetState(lightId, HUE_COLOR_YELLOW, 'lselect')


# started > failed > succeeded
def __newStatus(newStatus, oldStatus=None):
    if not oldStatus:
        return newStatus
    elif oldStatus == 'started' or newStatus == 'started':
        return 'started'
    elif oldStatus == 'failed' or newStatus == 'failed':
        return 'failed'
    elif oldStatus == 'errored' or newStatus == 'errored':
        return 'failed'
    else:
        return newStatus


def groupCiStatusByTeam():
    response = requests.get('https://ci.lab.innogize.io/api/v1/jobs', headers={'Authorization': CI_TOKEN})
    jobs = json.loads(response.content)
    status = {}

    for job in jobs:
        if job['next_build'] and job['next_build']['status']:
            status[job['team_name']] = __newStatus(job['next_build']['status'], status.get(job['team_name'], None))
        if job['finished_build'] and job['finished_build']['status']:
            status[job['team_name']] = __newStatus(job['finished_build']['status'], status.get(job['team_name'], None))

    return status


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(s):
        global CI_TOKEN

        s.send_response(200)
        s.send_header("Content-type", "text/text")
        s.end_headers()

        if s.path.startswith("/auth/callback?"):
            query_str = s.path[s.path.index("?") + 1:]
            params = parse_qs(query_str)
            if params.get('token'):
                CI_TOKEN = params.get('token')[0]
                print
                "received token."
                s.wfile.write("Ok, received token. You can close this window now.")
            else:
                print
                "wrong callback parameter"
                s.wfile.write("Call it like '/auth/callback?token=XXX'.")
        else:
            print
            "wrong callback parameter"
            s.wfile.write("Call it like '/auth/callback?token=XXX'.")


if __name__ == '__main__':
    print("Login to concourse")
    print
    print("https://ci.lab.innogize.io/sky/login?redirect_uri=http://127.0.0.1:64354/auth/callback")
    print
    httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 64354), MyHandler)
    try:
        httpd.handle_request()
    except KeyboardInterrupt:
        pass

    if not CI_TOKEN:
        print
        "No token from callback. Exit"
        # CI_TOKEN = raw_input("Enter token: ")

    if CI_TOKEN:
        lightsNameToId = __hueLightNameToId()

        while True:
            states = groupCiStatusByTeam()
            # print(states)
            for team in LAB:
                lightId = lightsNameToId[LAB[team]]
                if not states.get(team):
                    print('no team with name "' + team + '"')
                elif states[team] == 'succeeded':
                    hueSetSuccess(lightId)
                elif states[team] == 'failed':
                    hueSetFailed(lightId)
                elif states[team] == 'started':
                    hueSetStarted(lightId)
            time.sleep(5)
