# -*- coding: UTF-8 -*-

import sqlite3
from flask import Flask,g,session,request,redirect,url_for,abort,render_template,flash,jsonify
from contextlib import closing
from datetime import timedelta

error=''

app=Flask(__name__)
app.config.from_pyfile('yourconfig.cfg', silent=True)

def db_conn():
	connection=sqlite3.connect(app.config['DATABASE'])
	return connection
 
#connect the db before request
@app.before_request
def before_request():
	g.db = db_conn()
	g.cursor=g.db.cursor()

#close sqlite after request
@app.teardown_request
def teardown_request(exception):
	#if db attribute in g ,return it ,otherwise return None
	#that means,if db is being connected,close it
	db =getattr(g,'db','None')
	if db is not None:
		db.close()

@app.route('/login',methods=['GET','POST'])
def login():
	error=''
	if request.method=='POST':
		usrtologin=request.form['username']
		pswtologin=request.form['password']
		usrexist=g.cursor.execute('select * from user where uaername=(?)', [usrtologin]).fetchall()
		pswexist=g.cursor.execute('select * from user where uaername=(?) and password=(?)', [usrtologin,pswtologin]).fetchall()
		if ((usrtologin == app.config['USERNAME']) & (pswtologin == app.config['PASSWORD'])):
			session['logined']=True
			return redirect(url_for('user_list'))
		elif not (usrexist):
			error='username not exist'
		elif not (pswexist):
			error='wrong password!'
		else:
			session.permanent = True
			app.permanent_session_lifetime = timedelta(minutes=10)
			session['logined']=True
			global usrtemp
			usrtemp=usrtologin
			return redirect(url_for('user_list'))
	return render_template('login.html',error=error)

@app.route('/logout',methods=['GET','POST'])
def logout():
	session.pop('logined',None)
	flash('log out successfgully!','info') 
	return redirect(url_for('user_list'))

@app.route('/',methods=['GET','POST'])
def user_list():
	userlist=g.cursor.execute('select uaername,password from user order by id desc')
	listvalue=userlist.fetchall() #list
	userlist1=[dict(uaername=row[0], password=row[1]) for row in listvalue]
	return render_template('userlist1.html',userlist1=userlist1,error=error)

#if not stated ,default 'get'
@app.route('/add_user',methods=['POST'])
def add_user():
	if not session.get('logined'):
		abort(401)
	try:
		usr=request.form['addusername']
		psw=request.form['addpassword']
		ulevel=request.form['AccessLevel']
		usrexist=g.cursor.execute('select * from user where uaername=(?)', [usr]).fetchall()
		if not (usrexist):
			g.cursor.execute('insert into user(uaername,password,level) values (?,?,?)', [usr,psw,ulevel])
			g.db.commit()
			return jsonify(result='add successfully！')
		else:
			return jsonify(result='usr already exist,change it')			
		#return redirect(url_for('user_list'))
	except Exception,e:
		return jsonify(result=e)
	return redirect(url_for('user_list'))

@app.route('/del_user',methods=['POST'])
def del_user():
	error=''
	if not session.get('logined'):
		return redirect(url_for('user_list'))
	try:
		usr=request.form['nameofuser']
		level1=g.cursor.execute('select level from user where uaername=(?)', [usr]).fetchall()
		level2=g.cursor.execute('select level from user where uaername=(?)', [usrtemp]).fetchall()
		if level1 > level2:
			g.cursor.execute('delete from user where uaername=(?)', [usr])
			g.db.commit()
			return jsonify(result='successfully')
		else:
			return jsonify(result='嘤嘤嘤···权限不够')
	except Exception, e:
		return jsonify(result=e)
	return redirect(url_for('user_list'))

if __name__ == '__main__':
	app.run(host='0.0.0.0')


		
	
