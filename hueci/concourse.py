import json
from functools import reduce

import BaseHTTPServer
import requests
from urlparse import parse_qs


class Concourse:
    def __init__(self, url, token=None):
        self.__url = url
        self.__token = token
        self.__jobs = []

    # started > failed > succeeded
    def __new_status(self, newStatus, oldStatus=None):
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

    def __get_jobs(self):
        response = requests.get(self.__url + "/api/v1/jobs", headers={'Authorization': self.__token})
        return json.loads(response.content)

    def group_ci_status_by_teams(self):
        jobs = self.__get_jobs()
        status = {}

        for job in jobs:
            if job['next_build'] and job['next_build']['status']:
                status[job['team_name']] = self.__new_status(job['next_build']['status'],
                                                             status.get(job['team_name'], None))
            if job['finished_build'] and job['finished_build']['status']:
                status[job['team_name']] = self.__new_status(job['finished_build']['status'],
                                                             status.get(job['team_name'], None))

        return status

    def status_from_team(self, teamOrTeams):
        states = self.group_ci_status_by_teams()

        if type(teamOrTeams) is str:
            return states[teamOrTeams]
        else:
            teamStats = [states[team] for team in states if team in teamOrTeams]
            state = reduce((lambda x, y: self.__new_status(x, y)), teamStats)
            return state

    def wait_for_token(self):
        global CI_TOKEN

        print("Login to concourse")
        print
        print(self.__url + "/sky/login?redirect_uri=http://127.0.0.1:64354/auth/callback")
        print
        httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 64354), self.__ReadTokenHandler)
        try:
            httpd.handle_request()
        except KeyboardInterrupt:
            pass

        if not CI_TOKEN:
            print("No token from callback. Exit")
        else:
            self.__token = CI_TOKEN
            return self.__token

    def set_token(self, token):
        self.__token = token

    class __ReadTokenHandler(BaseHTTPServer.BaseHTTPRequestHandler):
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
                    print("received token.")
                    s.wfile.write("Ok, received token. You can close this window now.")
                else:
                    print("wrong callback parameter")
                    s.wfile.write("Call it like '/auth/callback?token=XXX'.")
            else:
                print("wrong callback parameter")
                s.wfile.write("Call it like '/auth/callback?token=XXX'.")
