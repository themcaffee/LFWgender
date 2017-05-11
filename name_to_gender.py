import os
import sys
from django.http import request
import requests
import shutil
from genderize import Genderize
from pprint import pprint
import time

from config import API_KEY, ROOTDIR, MALE_FOLDER, FEMALE_FOLDER

# It is highly recommended to use an API key for genderize because of the large amount of names
gender = Genderize(api_key=API_KEY)
# Amount of time to sleep for if timed out of requests
SLEEP_TIME = 60


def get_gender(name):
    result = None
    tries = 0
    while not result:
        try:
            return gender.get([name])[0]
        except Exception as e:
            tries += 1
            if tries > 3:
                print('Too many tries')
                raise Exception("Too many tries")
            print('Too many requests, waiting for {} seconds... ({})'.format(str(SLEEP_TIME), str(tries)))
            # Wait for timeout to refresh
            time.sleep(SLEEP_TIME)


def main(argv):
    fileList = []
    fileSize = 0
    folderCount = 0
    count = 0
    tmp = ""

    for root, subFolders, files in os.walk(ROOTDIR):
        folderCount += len(subFolders)
        for file in files:
            f = os.path.join(root,file)
            fileSize = fileSize + os.path.getsize(f)
            fileSplit = file.split("_")
            fileList.append(f)
            count += 1

            if count == 1 or tmp != fileSplit[0]:
                result = get_gender(fileSplit[0])
                tmp = fileSplit[0]
            else:
                tmp = fileSplit[0]

            try:
                if float(result['probability']) > 0.9:
                    if result['gender'] == 'male':
                        print('Copying male file...')
                        shutil.copyfile(f,"%s/%s" % (MALE_FOLDER,file))
                    elif result['gender'] == 'female':
                        print('Copying female file...')
                        shutil.copyfile(f,"%s/%s" % (FEMALE_FOLDER,file))
            except Exception as e:
                print('Exception occured parsing result!')
                pprint(e)
                print('Result:')
                pprint(result)

            print(count)


if __name__ == "__main__":
    main(sys.argv)
