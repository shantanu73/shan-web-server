# Modify these 7 variables below
SHAN_SERVER_SECRET_KEY = ""
CLIENT_ID = ""
CLIENT_SECRET = ""
SERVER_2_URL = ""
TENANT_ID = ""
ELEVATION_TIMES_LIST = [
    "1",
    "2",
    "3",
    "4",
]
ADMIN_GROUPS_LIST = [
    "adminGroup1",
    "adminGroup2",
    "adminGroup3",
]

# Do not modify these variables
AUTHORITY = "https://login.microsoftonline.com/" + TENANT_ID
APP_FOLDER_PATH = "/opt/shan-web-server/"
CERTS_FOLDER = APP_FOLDER_PATH + "certificates/"
CERTS_CHAIN_FILE = ""
KEY_FILE = ""
LOG_FOLDER = APP_FOLDER_PATH + "logs/"
LOG_FILE = LOG_FOLDER + "server1_logs.log"
REDIRECT_PATH = "/getAToken"
SCOPE = ["User.ReadBasic.All"]
SESSION_TYPE = "filesystem"
POST_REQUEST_STATUS_CODE = 201
HTTPS_SERVER = "0.0.0.0"
HTTPS_PORT = 443
MAX_NUMBER_OF_REQUESTS = 10000
