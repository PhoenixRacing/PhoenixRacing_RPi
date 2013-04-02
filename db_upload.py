from dbupload import upload_file, DropboxConnection
from getpass import getpass
import sys
# import mechanize

# This won't function until these variables are set to valid credentials
email = "olinphoenixracing@gmail.com"
password = "bajabaja"


def upload_db(fname = "First_CVT_Test.csv"):
    try:
        conn = DropboxConnection(email, password)
    except:
        print "login failed"
    try:
        conn.upload_file(fname, "/baja_pi", fname)
    except:
        print "upload failed"

        
if __name__ == '__main__':
    try:
        upload_db(sys.argv[1])
    except:
        upload_db()