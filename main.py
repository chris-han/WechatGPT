
from bot import mybot
from werobot.contrib.flask import make_view
from flask import Flask,request,abort,send_file
import hashlib
import config as cfg

app = Flask(__name__)
app.add_url_rule(rule='/', # WeRoBot 挂载地址
                 endpoint='werobot', # Flask 的 endpoint
                 view_func=make_view(mybot),
                 methods=['GET', 'POST'])



@app.route('/',methods=['GET','POST'])
def wechat():
    '''对接微信公众号'''

    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    echostr = request.args.get("echostr")
    if not all([signature, timestamp, nonce]):
        abort(400)

    li = [cfg.token, timestamp, nonce]
    li.sort()
    tmp_str = "".join(li).encode('utf-8')
    sign = hashlib.sha1(tmp_str).hexdigest()
    if signature != sign:
        abort(403)
    else:
        return echostr

@app.route('/hello/')
def hello():
    return '<h1>欢迎来到系统之美</h1>'

@app.route('/favicon.ico')    
def favicon():    
    return send_file('favicon.ico', mimetype='image/vnd.microsoft.icon')
    
if(__name__=="__main__"):
    app.run()