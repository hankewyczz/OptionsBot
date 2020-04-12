import os
import json


class pyson:
    '''Allows for easier manipulatoin of json files.

    It will check if a json file already exists with the given file name and open that, otherwise it will create a new one.

    Default datatype is a DICT, but you can pass what you want to it. EX: example=pyson(file_name,[]) would pass a list to the json.

    The modify the json with using the "data" attribute. EX: example.data.append('test') would add 'test' to the list declared above.'''

    def __init__(self, file_name, data={}):
        if not file_name.endswith('.json'):
            file_name = file_name + '.json'
        if not os.path.isfile(file_name):
            pass
        else:
            try:
                with open(file_name) as f:
                    data = json.load(f)
            except ValueError:
                pass
        self.file_name = file_name
        self.data = data

    def save(self):
        '''Save your json file'''
        if not self.file_name.endswith('.json'):
            self.file_name = self.file_name + '.json'
        with open(self.file_name, "w") as f:
            json.dump(self.data, f, indent=4, sort_keys=True)