import json


def parse(options=None):
        with open('workspace.json') as json_file:
            json_string = json_file.read()
            if options:
                json_string = json_string % options
            return json.loads(json_string)
