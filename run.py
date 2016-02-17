__author__ = 'Dmitry Kireev'
import psndeals.auth
import time
import config
import json

PROFILE_URL = 'https://vl.api.np.km.playstation.net/vl/api/v1/mobile/users/me/info'

# def get():
#     auth = psndeals.auth
#     profile = auth.get(PROFILE_URL)
#     return json.loads(profile.text)

if __name__ == '__main__':
    auth = psndeals.auth.auth()
    profile = auth.get(PROFILE_URL)
    print(json.loads(profile.text))
