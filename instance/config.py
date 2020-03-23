import os

# common Flask env config
API_URL_PREFIX = '/api'
ASSETS_PATH = './assets'
FE_BUILD_PATH = './build'

JWT_TOKEN_LOCATION = ['cookies']
JWT_ACCESS_COOKIE_PATH = '/api/'
JWT_REFRESH_COOKIE_PATH = '/api/token/refresh'
JWT_COOKIE_CSRF_PROTECT = False

ACCESS_TOKEN_EXPIRES_DAYS = 2
REFRESH_TOKEN_EXPIRES_DAYS = 10

JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

DIRNAME = os.path.dirname(os.path.abspath(__file__))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024
