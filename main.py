from data import db_session
from data.users import User
from data.messages import Messages
from data import chat_api
from flask import Flask, url_for, request, render_template, redirect, make_response, jsonify
import os
import datetime
from waitress import serve

app = Flask(__name__)


@app.route('/')
def main():
    try_authorized = request.cookies.get("authorized", '0')
    if try_authorized in ['0', 'No']:
        res = make_response(
            redirect(url_for('log_form')))
        res.set_cookie("authorized", 'No',
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = redirect(url_for('chat'))
    return res


@app.route('/reg_log', methods=['POST', 'GET'])
def log_form():
    if request.method == 'GET':
        return render_template('reg_log.html', path=url_for('static', filename='css/reg_log.css'))
    elif request.method == 'POST':
        if not request.form["login"] or not request.form["password"]:
            return render_template('reg_log.html', path=url_for('static', filename='css/reg_log.css'))
        db_sess = db_session.create_session()
        check = db_sess.query(User).filter(User.name == request.form["login"]).first()
        res = make_response(redirect(url_for('chat')))
        if check:
            if check.password == request.form["password"]:
                res.set_cookie('authorized', 'Yes', max_age=60 * 60 * 24 * 365 * 2)
                res.set_cookie('user_id', str(check.id), max_age=60 * 60 * 24 * 365 * 2)
                return res
            return render_template('try_again.html')
        res.set_cookie('authorized', 'Yes', max_age=60 * 60 * 24 * 365 * 2)
        user = User()
        user.name = request.form["login"]
        user.password = request.form["password"]
        db_sess.add(user)
        db_sess.commit()
        user_id = db_sess.query(User).filter(User.name == request.form["login"]).first()
        res.set_cookie('user_id', str(user_id.id), max_age=60 * 60 * 24 * 365 * 2)
        return res


def delete_database():
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db/chat.db')
    os.remove(path)


@app.route('/logout')
def logout():
    res = make_response(redirect(url_for('main')))
    res.delete_cookie('authorized')
    res.delete_cookie('user_id')
    return res


@app.route('/chat', methods=['POST', 'GET'])
def chat():
    if not check_login():
        return redirect(url_for('main'))
    if request.method == 'GET':
        db_sess = db_session.create_session()
        messages = db_sess.query(Messages).all()
        user = db_sess.query(User).filter(User.id == int(request.cookies.get('user_id'))).first()
        return render_template("chat.html",
                               messages=messages if len(messages) != 0 else '', user_name=user.name)
    else:
        if not request.form["message"]:
            return redirect('#bar')
        db_sess = db_session.create_session()
        message = Messages()
        message.content = request.form["message"]
        user = db_sess.query(User).filter(User.id == int(request.cookies.get('user_id'))).first()
        message.user_name = user.name
        message.created_date = datetime.datetime.now().strftime("%H:%M")
        db_sess.add(message)
        db_sess.commit()
        return redirect('#bar')


@app.route('/getMessages', methods=['POST', 'GET'])
def getMessages():
    if not check_login():
        return redirect(url_for('main'))
    db_sess = db_session.create_session()
    messages = db_sess.query(Messages).all()
    some_dict = []
    for message in messages:
        user = db_sess.query(User).filter(User.id == int(request.cookies.get('user_id'))).first()
        some_dict.append({'id': message.id, 'editable': True if user.name == message.user_name else False,
                          'content': message.content, 'date': message.created_date, 'name': message.user_name})
    return make_response(jsonify(some_dict))


def check_login():
    try_authorized = request.cookies.get("authorized", '0')
    if try_authorized in ['0', 'No']:
        return False
    return True


@app.route('/chat/<int:message_id>', methods=['GET', 'POST'])
def edit_message(message_id):
    if request.method == 'GET':
        db_sess = db_session.create_session()
        message = db_sess.query(Messages).filter(Messages.id == message_id).first()
        res = make_response(render_template('edit_message.html', message=message.content))
        res.set_cookie('message_id', str(message_id), max_age=60 * 60 * 24 * 365 * 2)
        return res
    else:
        message_id = request.cookies.get("message_id")
        if not request.form["new_message"]:
            return redirect(message_id)
        res = make_response(redirect(url_for('chat')))
        db_sess = db_session.create_session()
        message = db_sess.query(Messages).filter(Messages.id == int(message_id)).first()
        message.content = request.form["new_message"]
        message.created_date = datetime.datetime.now().strftime("%H:%M")
        db_sess.commit()
        return res


@app.route('/message_delete/<int:message_id>')
def delete_message(message_id):
    db_sess = db_session.create_session()
    message = db_sess.query(Messages).filter(Messages.id == message_id).first()
    db_sess.delete(message)
    db_sess.commit()
    return redirect(url_for('chat'))


@app.route('/account')
def account():
    try_authorized = request.cookies.get("authorized", '0')
    if try_authorized in ['0', 'No']:
        return redirect(url_for('main'))
    return render_template('account.html')


if __name__ == '__main__':
    db_session.global_init("db/chat.db")
    app.register_blueprint(chat_api.blueprint)
    serve(app, host='0.0.0.0', port=8080)
