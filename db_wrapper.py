import cmd
import locale
import os
import pprint
import shlex

from dropbox import client, rest, session

# XXX Fill in your consumer key and secret below
# You can find these at http://www.dropbox.com/developers/apps
APP_KEY = 'y42yz1pultu5sxv'
APP_SECRET = '7jjkbatb0fphh8e'
ACCESS_TYPE = 'dropbox'  # should be 'dropbox' or 'app_folder' as configured for your app

class DropboxTerm():
    def __init__(self, app_key = APP_KEY, app_secret = APP_SECRET):
        self.sess = StoredSession(app_key, app_secret, access_type=ACCESS_TYPE)

        try:
        	self.sess.load_creds()
        except:
        	self.sess.link()

        self.api_client = client.DropboxClient(self.sess)
        self.current_path = ''
        self.sess.load_creds()

    def do_account_info(self):
        """display account information"""
        f = self.api_client.account_info()
        pprint.PrettyPrinter(indent=2).pprint(f)

    def do_put(self, from_path, to_path):
        """
        upload to dropbox
        """
        from_file = open(os.path.expanduser(from_path), "rb")

        self.api_client.put_file(self.current_path + "/" + to_path, from_file)


class StoredSession(session.DropboxSession):
    """a wrapper around DropboxSession that stores a token to a file on disk"""
    TOKEN_FILE = "token_store.txt"

    def load_creds(self):
        stored_creds = open(self.TOKEN_FILE).read()
        self.set_token(*stored_creds.split('|'))
        print "[loaded access token]"

    def write_creds(self, token):
        f = open(self.TOKEN_FILE, 'w')
        f.write("|".join([token.key, token.secret]))
        f.close()

    def delete_creds(self):
        os.unlink(self.TOKEN_FILE)

    def link(self):
        request_token = self.obtain_request_token()
        url = self.build_authorize_url(request_token)
        print "url:", url
        print "Please authorize in the browser. After you're done, press enter."
        raw_input()

        self.obtain_access_token(request_token)
        self.write_creds(self.token)

    def unlink(self):
        self.delete_creds()
        session.DropboxSession.unlink(self)