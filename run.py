__author__ = 'Dmitry Kireev'
import os
from psndeals import app

if __name__ == '__main__':
    if 'PORT' in os.environ:
        PORT = os.environ['PORT']
    else:
        PORT = 5000
    app.run(host='0.0.0.0', port=PORT)