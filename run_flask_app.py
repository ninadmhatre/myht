#! /usr/bin/env python
__author__ = "ninad"

import os
from application import app

if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=True)
