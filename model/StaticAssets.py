__author__ = 'ninad'

# Flask
from flask_assets import Bundle, Environment
# from application import app


bundles = {
    'third_party_js': Bundle(
        "js/bootstrap.min.js",
        "js/bootstrap.min.js.map",
        "js/lblrsm.js",
        filters='jsmin'
        ),

    'third_party_css': Bundle(
        "css/bootstrap-grid.min.css",
        "css/bootstrap-grid.min.css.map",
        "css/bootstrap.min.css",
        "css/bootstrap.min.css.map",
        "css/bootstrap-reboot.min.css",
        "css/bootstrap-reboot.min.css.map",
        "css/myht.css",
        filters='cssmin'
    )
}

# lblrsm_assets = Environment(app)
# lblrsm_assets.register(bundles)


# def get_assets():
#     print('Here from lblrsm.assets....')
#     return lblrsm_assets

