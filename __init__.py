import os

from werkzeug.contrib.cache import SimpleCache
# 버젼 조심 : pip install werkzeug==0.16.0


from flask import Flask, request, session, g, redirect, url_for, abort, \
	 render_template, flash

from sqlite3 import dbapi2 as sqlite3

import glob
import xml.etree.ElementTree as ET



# for user login
# pip install Flask-Login 
# 먼저 읽어볼것 ##############
# pip install flask-login==0.5.0 
# winpython37z 의 플라스크는  pip install flask==1.1.2
# 
########################################
#### WinPython37Z  tensorflow==1.15.0 ##

## autoquiz 는 Tensorflow 1.6.0 ==> 1.15 로 고침.
## autoquiz 는 python 2.7 만듦 => 3.7 버젼으로 고침.
# pip install flask==1.1.2
# pip install flask-login==0.5.0  
# pip install werkzeug==0.16.0



from flask_login import LoginManager, login_required, login_user, \
                                 logout_user, UserMixin, AnonymousUserMixin, current_user



# http://blog.csdn.net/yatere/article/details/78860852
# from time import sleep


from concurrent.futures import ThreadPoolExecutor, as_completed

OFFICIAL_MAILBOX = 'cs10.autoquiz@gmail.com'
# 버클리 대학 =================================



####################################################


DATABASE = './autoquiz.db'
FILE_DIR = './static/dataset/'
MODEL_LOG_FOLDER = "./log/"


#####################################################


DKT_SESS_DAT = "dkt_sessions.csv"

DKT_MODEL = "model.ckpt"

ID_ENCODING_FILE = 'id_encoding.csv'
ID_CATEGORY_FILE = 'id_category.csv'
EN_CATEGORY_FILE = 'en_category.csv'
TOPIC_NAMES_FILE = 'topic_names.csv'


DEBUG_FILE = 'debug_info.txt'
# 루트에 

######################################################




BATCH_SIZE = 16
MAX_SESS = 16
N_EPOCH = 16

THRESHOLD_ACC = 0.6
THRESHOLD_AUC = 0.5


# create the application
app = Flask(__name__)




## app.run 은 autoquiz.py #############
# if __name__ == '__main__':
#    app.run(debug=True, port=8000)

# http://blog.csdn.net/yannanxiu/article/details/52916892
# http://werkzeug.pocoo.org/docs/0.14/contrib/cache/
# cache




user_cache = SimpleCache()

executor = ThreadPoolExecutor(2)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'autoquiz.db'),
    # ==================================================
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='math4ai'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# login management
login_manager = LoginManager()
login_manager.setup_app(app)



def debug_output(output_string):
    # debug print into file
    file_path = os.path.join(app.root_path, DEBUG_FILE)
    with open(file_path, 'a') as f:
        f.write("{0}\n".format(output_string))
    return True

class User(UserMixin):
    def __init__(self, user_name, user_id):
        self.user_id = user_id
        self.user_name = user_name
    def get_id(self):
        try:
            return unicode(self.user_id)  # python 2
        except NameError:
            return str(self.user_id)  # 파이썬 3
    def get_name(self):
        try:
            return unicode(self.user_name)  # python 2
        except NameError:
            return str(self.user_name)  # 파이썬 3
    def debug_introduce(self):
        print ("hello, I am {0}, my id is {1}".format(self.user_name, self.user_id))

class AnonymousUser(AnonymousUserMixin):
    def get_name(self):
        return None
    def debug_introduce(self):
        print ("hello, I am annonymous user")

login_manager.anonymous_user = AnonymousUser
