import time
import os
import json
from pipelines import pipe
from config_listener import SHARED_FOLDER

def handle_file(current, previous):
    print("Changed from {} to {}".format(previous, current))

    for (_,_, files) in os.walk(SHARED_FOLDER, topdown=True):
            files = files

    files = [os.path.join(SHARED_FOLDER, i) for i in files]
    time_sorted_list = sorted(files, key=os.path.getmtime)
    last_added_file = time_sorted_list[-1]

    with open(last_added_file,) as f:
        form = json.load(f)
      
    print("newest file: {}".format(last_added_file))
    print('Submission form {} through pipe'.format(last_added_file))
    pipe(form)

if __name__ == "__main__":
    
    current_lenght = len(os.listdir(SHARED_FOLDER))
    try:
        while True:
            live_lenght = len(os.listdir(SHARED_FOLDER))
            if live_lenght != current_lenght:
                handle_file(live_lenght, current_lenght)
                current_lenght = live_lenght

            time.sleep(1)


    except KeyboardInterrupt:
        print('Observer stopped (Keyboard Interrupt)')
