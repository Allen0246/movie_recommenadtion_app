import os

_basedir = os.path.abspath(os.path.dirname(__file__))


# GENERAL
if os.getenv('FLASK_ENV') == 'production':
    DEBUG = False
else:
    DEBUG = True

USE_RELOADER = os.getenv('USE_RELOADER')


# FLASK
BCRYPT_LOG_ROUNDS = 12  # Configuration for the Flask-Bcrypt extension
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG_TB_INTERCEPT_REDIRECTS = False
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

# WTF CSRF Secret Key
WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY')

# LOG
LOG_PATH = '{0}/log/'.format(os.getenv('FLASK_PATH'))
if isinstance(os.getenv('LOG_BACKUP_COUNT'), int):
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT')) # days
else:
    LOG_BACKUP_COUNT = 0
if 'LOG_LEVEL' in os.environ:
    if os.getenv('LOG_LEVEL') == 'CRITICAL':
        LOG_LEVEL = 50
    elif os.getenv('LOG_LEVEL') == 'ERROR':
        LOG_LEVEL = 40
    elif os.getenv('LOG_LEVEL') == 'WARNING':
        LOG_LEVEL = 30
    elif os.getenv('LOG_LEVEL') == 'INFO':
        LOG_LEVEL = 20
    elif os.getenv('LOG_LEVEL') == 'DEBUG':
        LOG_LEVEL = 10
    else:
        LOG_LEVEL = 10
else:
    LOG_LEVEL = 10


# Default roles
DEFAULT_ROLES = ['admin', 'user']

# Default admin user
DEFAULT_ADMIN_USERNAME = os.getenv('DEFAULT_ADMIN_USERNAME')
DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD')
DEFAULT_ADMIN_ROLE = 'admin'

# Default 'user' user
DEFAULT_USER_USERNAME = os.getenv('DEFAULT_USER_USERNAME')
DEFAULT_USER_PASSWORD = os.getenv('DEFAULT_USER_PASSWORD')
DEFAULT_USER_ROLE = 'user'

# DATABASE
SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
  os.getenv('POSTGRES_USER'),
  os.getenv('POSTGRES_PASSWORD'),
  os.getenv('POSTGRES_HOST'),
  os.getenv('POSTGRES_PORT'),
  os.getenv('POSTGRES_DB')
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True, 'pool_size': 30, 'max_overflow': 15, 'pool_recycle': 60 * 60,}


# THEMOVEIDB
THEMOVIEDB_HOSTNAME = os.getenv('THEMOVIEDB_HOSTNAME')
THEMOVIEDB_TOKEN = os.getenv('THEMOVIEDB_TOKEN')
PRIMARY_RELEASE_DATE_GTE = os.getenv('PRIMARY_RELEASE_DATE_GTE')
THEMOVIEDB_API_VERSION = '/3'
THEMOVIEDB_HEADERS = {
  'Accept': 'application/json'
}


del os