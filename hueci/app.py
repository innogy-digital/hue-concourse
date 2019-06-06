import time
from datetime import datetime

from .concourse import Concourse
from .hue import Hue

UPDATE_INTERVAL_SEC = 5

CI_URL = "https://ci.lab.innogize.io"

HUE_USERNAME = "XXX"
HUE_URL = "http://192.168.2.100"

LAB = {
    "hydrodata4all,tnb-portal": "dlab 2.1",
    "wth,BeMa": ["dlab 2.2"],
    "BeMa,KiWi": "dlab 2.4",
    'aspekt': "dlab 2.3"
}


def run():
    hue = Hue(HUE_URL, HUE_USERNAME)
    ci = Concourse(CI_URL)

    ci.wait_for_token()

    while True:
        hue.update_lights()

        for team in LAB:
            state = ci.status_from_team(team.split(","))
            print("[" + str(datetime.now()) + "] " + team + " -> " + state)
            if not state:
                print('no status for team "' + team + '"')
            elif state == 'succeeded':
                hue.set_success(LAB[team])
            elif state == 'failed':
                hue.set_failed(LAB[team])
            elif state == 'started':
                hue.set_started(LAB[team])
            else:
                print('unkown status "' + state + '" for team "' + team + '"')

        time.sleep(UPDATE_INTERVAL_SEC)
