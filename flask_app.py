#!/usr/bin/python2.7 ==>  파이썬 3.7로 고침 


from __init__ import *
import os
from sqlite3 import dbapi2 as sqlite3

from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import xml.etree.ElementTree as ET
import json

import time
import datetime

from fileio_func import read_xml, save_session_data
from database_func import check_user, get_user, get_next_id, user_registration, user_login, log_exercise_db, get_topic_info, fetch_questions, get_challenge_questions, get_topic_correctness_DKT


#####  from flask import Flask, render_template, request


#########################  챗 복 ########################


# 챗봇 엔진 query 전송 API
@app.route('/query/<bot_type>', methods=['POST'])
def query(bot_type):
    body = request.get_json()

    try:

        if bot_type == "KAKAO":
            # 카카오톡 스킬 처리
            body = request.get_json()
            utterance = body['userRequest']['utterance']
            #ret = get_answer_from_engine(bottype=bot_type, query=utterance)


            ret = "goto 와 doit 거북명령 그리고 정직구원 입체 집합명령 기반의 터북이 코딩수학입니다"

            if 'jpg' in utterance or 'png' in utterance:
                #urllib.request.urlretrieve(utterance, 'img')
                #image = Image.open('img').convert('RGB')
                ret="강아지 사진? 고양이? 인공지능으로 !!"
                res = {
                   "version": "2.0",
                   "template": {
                       "outputs": [
                          {
                            "basicCard": {
                               "title": ret,
                               "description": "",
                               "thumbnail": {
                                 "imageUrl": utterance
                                 },
                               "buttons": [
                                   {
                                    "action":  "webLink",
                                    "label": "사진보기",
                                    "webLinkUrl": utterance
                                   }
                               ]
                            }
                          }
                       ]
                   }
                }
                print(res)
                return jsonify(res)



            if utterance.find("터북")>=0 :
                ret="마인드스톰에서는 스티브, 터틀크래프트에서는 터북이 (터틀+거북)"
            if utterance.find("코딩")>=0 :
                ret="codingmath.org 및 snucode.org 주소와 SNU코딩수학 밴드와 유튜브를 보세요"
            if utterance.find("함수")>=0 :
                ret="nemo(x,y) sqrt(x,y) 길이, abs(a,b)=|a-b| 차이, atan(x,y) 각도 sin cos exp min max 등"
            if utterance.find("goto")>=0 :
                ret="goto(x,y,z,d) : 거북이를 (x,y,z) 위치와 d직각 방향으로 보낸다. 터북이는 turbook(x,y,z, d직각,e시선각도)"
            if utterance.find("doit")>=0 :
                ret="doit( s t u d l r L R ; item=블럭타입 ) ++ 치환문자와 [ ] 사용"
            if utterance.find("begin")>=0 :
                ret="beginxyz 아래는 집합 조건제시법, 위에는 doit 원소나열법, beginsxyz 성벽 거북명령"
            if utterance.find("거북")>=0 :
                ret="doit 가자돌자, dovt 쌓기나무 행렬, dost 애니메이션, beginsxyz 성벽"

            if utterance == "정" :
                ret="정(X중심, Y중심, Z시작, 반지름, Z까지) ++ nemo"
            if utterance == "직" :
                ret="직(X중심, Y중심, Z시작, 가로반지름, 세로반지름, Z까지)"
            if utterance == "구" :
                ret="구(X중심, Y시작, Z중심, X반지름, Z반지름) ++ 타원구"
            if utterance == "원" :
                ret="원(X중심, Y중심, Z시작, X반지름, Y반지름, Z까지) ++ sqrt"
            if utterance == "입" :
                ret="입(길이시작, 각도시작, Z시작, 길이까지, 각도까지, Z까지) ++ (X중심,Y중심)"
            if utterance == "체" :
                ret="체(X시작, Y시작, Z시작, X까지, Y까지, Z까지) ++ cubexyz(x,y,z,dx,dy,dz)"




            #from KakaoTemplate import KakaoTemplate
            #skillTemplate = KakaoTemplate()
            #return skillTemplate.send_response(ret)


            responseBody = {
              "version": "2.0",
              "template": {
              "outputs": [
                    {
                    "simpleText": {
                        "text":  ret
                         }
                    }
                  ]
                }
            }
            return responseBody


        elif bot_type == "NAVER":
            # 네이버톡톡 이벤트 처리
            pass

        else:
            # 정의되지 않은 bot type인 경우 404 오류
            abort(404)

    except Exception as ex:
        # 오류 발생시 500 오류
        abort(500)



####################################################





@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

	
@app.before_request
def before_request():
    g.user = current_user
    # if g.user.is_authenticated:
    #     g.user.debug_introduce()



@app.teardown_appcontext
def close_db(error=None):
    # Closes the database again at the end of the request.
    # print "tear down?"
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()



@login_manager.user_loader
def load_user(user_id):
    user_name = user_cache.get('user_name')
    user_id_cached = user_cache.get('user_id')
    if user_name is None or int(user_id_cached) != int(user_id):
        success, user_name = get_user(user_id)
        user_cache.set('user_id', user_id, timeout=0)
        user_cache.set('user_name', user_name, timeout=0)
    return User(user_name, user_id)



@app.route('/topic/<topic_id_marked>')
def topic_question_lst(topic_id_marked):
    topic_id = int(topic_id_marked) - 1
    # print "topic id = {0}".format(topic_id)
    user_id = current_user.get_id()
    questions = fetch_questions(topic_id, user_id)
    return json.dumps(questions)



@app.route('/exercise/', methods=['GET', 'POST'])
@app.route('/exercise/<question_id>/', methods=['GET', 'POST'])
def exercise_section(question_id=None):

    # request.args.get('name', '')
    if request.method == 'POST':
        # print request.values
        # print request.args     
        question_id = request.form['question_id']
    else:
        #본래는 로그인을 안해도 각각 문제를 exercise 할 수 있었는데 이제는 막음 !!
        #if question_id is None:
        #    return redirect(url_for('welcome'))
        #else:
        #    question_id = int(question_id)
        
        if question_id is None:
            return redirect(url_for('welcome'))
        else:
            user_id = current_user.get_id()
            if user_id is None:
                login = False
                username=None
                show_msg = True
                msg = ['warning', ' [가입] 로그인을 먼저 하세요. 로그인하고 과제문제를 풀어보세요 !!']
                return render_template('welcome.html', login=login, username=username, show_msg=show_msg, msg=msg)
            else:
                question_id = int(question_id)
                      
            
    next_id = get_next_id(question_id)
    if next_id is None:
        next_id = -1
    question_fname = "Q{0}.xml".format(question_id)
    # print "question file name {0}".format(question_fname)
    question, answers, correct_ans_id, hint, description, multi_answers = read_xml(question_fname, os.path.join(app.root_path, 'static', 'dataset'))
    # print "next question is {0}".format(next_id)

    #print correct_ans_id
    #print answers

    return render_template('exercise.html', question=question, answers=answers, \
        question_id=question_id, correct_ans_id=correct_ans_id, hint=hint, next_id=next_id, description=description, multi_answers=multi_answers)
    # return render_template('exercise.html', **locals())










@app.route('/challenge/', methods=['GET', 'POST'])
@app.route('/challenge/<num_id>/', methods=['GET', 'POST'])
def challenge_section(NUM=None):

    questions_lst = []
    num_id = NUM
    #print( " 시작 ==> ", num_id ) 
    #question_id_lst = []
    user_id = current_user.get_id()
  
    
    if request.method == 'POST':
        # print request.values
        # print request.args
        num_id = request.form['num_id']
        #print("=== num_id ===> ", num_id)
        # 여기까지 제대로 작동 11번 12번까지 온다 good !!!!!!
        
        
    #print( " 중간 ==> ", num_id )
    



    
    if user_id is None:
        #root = tk.Tk()
        #root.title("주의 !!")
        #tk.Label(root, text="로그인을 먼저하세요").pack()
        #root.after(5000, lambda: root.destroy())     # time in ms
        #root.mainloop()
        login = False
        username=None
        show_msg = True
        msg = ['warning', ' [가입] 로그인을 먼저 하세요. 로그인하고 과제문제를 풀어보세요 !!']
        return render_template('welcome.html', login=login, username=username, show_msg=show_msg, msg=msg)
        #return
    
    else: 
        question_id = user_cache.get("question_id")
        correctness = user_cache.get("correctness")
        next_session = user_cache.get("next_session")
        user_cache.set("next_session", [], timeout=0)
        
        # question_id_lst = get_challenge_questions( num_id, user_id, model_dir=app.root_path, prev_load=next_session)
        
        question_id_lst = []
        # 아하 스트링으로 오는구나 !!!!!!!!!!!
        #print(" 끝전 == num_id  ======================> ", num_id,  num_id +1 , num_id == 7 )


        if num_id=='0':
            question_id_lst = [901,902,903,904,905,906,907,908,909,910]     
        elif num_id=='1':
            question_id_lst = [1,2,3,4,5,6,7,8,9,10]
        elif num_id=='2':
            question_id_lst = [11,12,13,14,15,16,17,18,19,20]
        elif num_id=='3':
            question_id_lst = [21,22,23,24,25,26,27,28,29,30]
        elif num_id=='4':
            question_id_lst = [31,32,33,34,35,36,37,38,39,40]
        elif num_id=='5':
            question_id_lst = [41,42,43,44,45,46,47,48,49,50]
        elif num_id=='6':
            question_id_lst = [51,52,53,54,55,56,57,58,59,60]
        elif num_id=='7':
            question_id_lst = [61,62,63,64,65,66,67,68,69,70]
            #print( question_id_lst )
        elif num_id=='8':
            question_id_lst = [71,72,73,74,75,76,77,78,79,80]
        elif num_id=='9':
            question_id_lst = [81,82,83,84,85,86,87,88,89,90]
        elif num_id=='10':
            question_id_lst = [91,92,93,94,95,96,97,98,99,100]
        elif num_id=='11':
            question_id_lst = [101,102,103,104,105,106,107,108,109,110]
        elif num_id=='12':
            question_id_lst = [111,112,113,114,115,116,117,118,119,120]
        
        #print(" 끝 중간 == num_id  ======================> ", num_id)
        #print(" 끝끝 == num_id  ======================> ", num_id ==  7  )
        
        
        for question_id in question_id_lst:
            question_fname = "Q{0}.xml".format(question_id)
            
            # print "question file name {0}".format(question_fname)
            question, answers, correct_ans_id, hint, description, multi_answers = read_xml(question_fname, os.path.join(app.root_path, 'static', 'dataset'))
            # print "next question is {0}".format(next_id)
            questions_lst.append([question_id, question, answers, correct_ans_id, hint, description, multi_answers])
            
            
        return render_template('challenge.html', questions_lst=questions_lst)






def update_session(question_id_lst, correctness_lst, new_data):
    # print "tear down?"
    if question_id_lst is not None and len(question_id_lst) >= MAX_SESS:
        session_data = {
            "correctness": correctness_lst,
            "question_id": question_id_lst
        }
        # save_session_data(session_data, os.path.join(app.root_path, DKT_SESS_DAT))
        executor.submit(set_topic_correctness, session_data, model_dir=app.root_path, update=True)
        question_id_lst=[]
        correctness_lst=[]
    else:
        question_id_lst.append(new_data["question_id"])
        correctness_lst.append(new_data["correctness"])
    return question_id_lst, correctness_lst






@app.route('/log_exercise', methods=['GET', 'POST'])
def log_exercise_result():
    jsondata = request.form.get('data')
    data = json.loads(jsondata)
    
    question_id = data["question_id"]
    correctness = data["correctness"]
    id_selected = data["id_selected"]
    txt_selected = data["txt_selected"]
    
    # timestamp = time.time()
    # timestring = datetime.datetime.fromtimestamp(timestamp).strftime('%Y/%m/%d %H:%M:%S')
    user_id = current_user.get_id()
    log_ip = request.remote_addr
    log_time = datetime.datetime.now()
    #print( "user {0} do exe {1} ans_int: {2} , ans_txt: {3}".format(user_id, question_id, id_selected, txt_selected))
    result = log_exercise_db(question_id, user_id, correctness, log_ip, log_time, id_selected, txt_selected)
    if result:
        success = 1
    else:
        success = 0
    info = [{
            "success": success
        }
    ]
    if session.get("question_id") is None:
        session["question_id"] = []
    if session.get("correctness") is None:
        session["correctness"] = []
    session["question_id"], session["correctness"] = update_session(session["question_id"], session["correctness"], data)
    return json.dumps(info)









def set_topic_correctness(data, model_dir=app.root_path, update=True):
    # print "update DKT model"
    question_id = data["question_id"]
    correctness = data["correctness"]
    # save the session
    save_session_data(data, file_name = os.path.join(app.root_path, DKT_SESS_DAT))
    # print "finished saving DKT session data of {0}, {1}".format(question_id, correctness)
    # debug_output("start executing DKT model")
    category_correctness, next_session, accuracy, auc = get_topic_correctness_DKT(question_id, correctness, model_dir=model_dir, update=update)
    # debug_output("end executing DKT model")
    # print category_correctness, next_session
    user_cache.set("next_session", next_session, timeout=0)
    user_cache.set("category_correctness", category_correctness, timeout=0)
    # print "finished updating DKT model"
    return next_session, category_correctness














@app.route('/log_session', methods=['GET', 'POST'])
def log_challenge_session():

    jsondata = request.form.get('data')
    data = json.loads(jsondata)
    
    question_id = data["question_id"]
    correctness = data["correctness"]
    
    id_selected = data["id_selected"]
    txt_selected = data["txt_selected"]

    # print question_id
    # print correctness
    # log the data
    assert len(question_id) == len(correctness), "log error: questions and answers number not match"
    len_session = len(question_id)
    user_id = current_user.get_id()
    log_ip = request.remote_addr
    
    for i in range(len_session):
        log_time = datetime.datetime.now()
        log_exercise_db(question_id[i], user_id, correctness[i], log_ip, log_time, id_selected[i], txt_selected[i] )
        
    # save the session and set the value
    # debug_output("start executing parallel submit")
    # next_session, category_correctness = set_topic_correctness(data, model_dir=app.root_path, update=True)
    executor.submit(set_topic_correctness, data, model_dir=app.root_path, update=True)
    # debug_output("end executing parallel submit")
    topic_info, _ = get_topic_info(user_id)
    category_correctness = {str(t[1]): float(t[2] / (t[2] + t[3])) if (t[2] + t[3]) > 0 else 0 for t in topic_info}
    session_topic_info = user_cache.get('category_correctness')
    if session_topic_info is None:
        session_topic_info = {'your recent bahaviors': 0}
    # print category_correctness
    '''
    session_topic_info = {
            "Math and Logic Basics": 0.6,
            "Programming and Algorithm": 0.4,
            "Lists and HOFs": 0.3,
            "Recursion": 0.2,
            "Concurrency": 0.1
        }
    '''
    info = [category_correctness, session_topic_info]
    return json.dumps(info)














@app.route('/check_user', methods=['GET', 'POST'])
def check_user_exists():
    jsondata = request.form.get('data')
    data = json.loads(jsondata)
    username = data["username"]
    if check_user(username):
        success = 0
    else:
        success = 1
    info = [{
            "success": success
        }
    ]
    return json.dumps(info)

@app.route('/home/', methods=['GET', 'POST'])
def welcome():
    print(request.form.get('form_name', 'null')) 
    if request.method == 'POST' and request.form.get('form_name', 'null') in ['login', 'logout']:
        # if it is login, not logout
        status = request.form.get('confirm_logout', '0')
        if str(status) == '1':
            # logout
            username = current_user.get_name()
            show_msg = True
            msg = ['success', 'Done', '로그아웃 !! 굿바이 {0}'.format(username)]
            login = False
            username=None
            logout_user()
        else:
            # get login / register information
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            confirm = request.form.get('confirm', '')
            to_register = len(request.form.get('reg', '')) > 0 # on or None
            # print "User Name is: {0}, password {1}, confirm {2}, to register {3}.".format(username, password, confirm, to_register)
            # try to login
            if to_register:
                # print "register"
                log_time = datetime.datetime.now()
                reg_success, user_id = user_registration(username, password, log_time)
                if reg_success:
                    show_msg = True
                    msg = ['success', 'Welcome', ' 회원 가입이 되었습니다 ::  {0}'.format(username)]
                    login = True
                    tmp_user = User(user_name= username, user_id=user_id)
                    login_user(tmp_user, remember=True)
                    user_cache.set('user_id', user_id, timeout=0)
                    user_cache.set('user_name', username, timeout=0)
                else:
                    show_msg = True
                    msg = ['danger', 'Sorry', ' "{0}" 는 이미 사용되는 ID 입니다. 다른 ID 이름으로 신청하세요.'.format(username)]
                    login = False
            else:
                # login
                # print "login"
                login_success, user_id = user_login(username, password)
                if login_success:
                    show_msg = True
                    msg = ['success', '안녕 ! 웰컴 back !!  {0}'.format(username) , ' '.format(username) ]
                    login = True
                    tmp_user = User(user_name= username, user_id=user_id)
                    login_user(tmp_user, remember=True)
                    user_cache.set('user_id', user_id, timeout=0)
                    user_cache.set('user_name', username, timeout=0)
                else:
                    login = False
                    show_msg = True
                    msg = ['danger', 'ERROR', ' 틀린 패스워드 또는 ID 이름 ;  다시 로그인하세요 {0} for help.'.format(OFFICIAL_MAILBOX)]
    else:
        # check it up in cache
        username = current_user.get_name()
        if username is None:
            # userip = request.remote_addr
            login = False
            # message to show when not logged in
            show_msg = True
            msg = ['warning', 'WARNING', '로그인을 하지 않으면 ==> 문제를 풀 수 없습니다 !']
        else:
            login = True
            # no message
            show_msg = False
            msg = []

    # fetch personal topic information from database
    user_id = current_user.get_id()
    print( user_id)
    all_topics, topic_links = get_topic_info(user_id)
    print( all_topics)
    print( topic_links )
    print( username )
    print( login )
    print( show_msg )
    """
    user_id = 48
    all_topics = [[1, 'Math and Logic Basics', 0, 0, [300.0, 300.0]], [2, 'Programming and Algorithm', 0, 0, [466.66666666666663, 300.0]], [3, 'Lists and HOFs', 0, 0, [633.3333333333333, 100.0]], [4, 'Recursion', 0, 0, [633.3333333333333, 300.0]], [5, 'Concurrency', 0, 0, [633.3333333333333, 500.0]], [6, 'Python', 0, 0, [800.0, 300.0]]]
    topic_link = [[0, 1], [1, 2], [1, 3], [1, 4], [3, 5], [2, 5], [1, 5]]
    username= 'admin'
    login = True
    show_msh = True
    msg = [ ] 
    """
	
    return render_template('welcome.html', login=login, username=username, \
        all_topics=all_topics, topic_links=topic_links,\
        show_msg=show_msg, msg=msg)



@app.route('/')
def default_entry():
    return redirect(url_for('welcome'))

	
if __name__ == '__main__':
    app.run(debug=True, port=8000)