from flask import Blueprint,render_template,url_for,flash,redirect,request
from flask_login import login_user,login_required,current_user,logout_user
from peter import db
from peter.models import User,Post
from peter.users.forms import RegistrationForm,LoginForm,UpdateAccountForm,RequestResetForm,ResetPasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import os 
import secrets
from PIL import Image
from flask import url_for,current_app
from flask_mail import Message
from peter import mail
users=Blueprint('users',__name__)
def send_reset_email(user):
	token = user.get_reset_token()
	msg=Message('password reset request',sender='petermbiriri8957@gmail.com',recipients=[user.email])
	msg.body=f'''To reset your password,visit the following link:
{url_for('users.reset_token',token=token,_external=True)}

If you did not make this request then ignore this email.
	'''
	mail.send(msg)
@users.route("/register",methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))

	form=RegistrationForm()
	if form.validate_on_submit():
		hashed_password=generate_password_hash(form.password.data)
		user=User(username=form.username.data,email=form.email.data,password=hashed_password)
		db.session.add(user)
		db.session.commit()

		flash('Your account has been created!')
		return redirect(url_for('users.login'))
	return render_template('register.html',title='register',form=form)
@users.route('/login',methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form=LoginForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user and check_password_hash(user.password,form.password.data):
			login_user(user,remember=form.remember.data)
			next_page=request.args.get('next')
			return redirect(next_page)if next_page else  redirect(url_for('main.home'))
		else:

			flash('login unsuccessful.please check email and password')
	return render_template('login.html',title='login',form=form)

@users.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('main.home'))


def save_picture(form_picture):
	random_hex=secrets.token_hex(8)
	_,f_ext=os.path.splitext(form_picture.filename)
	picture_fn=random_hex + f_ext
	picture_path=os.path.join(current_app.root_path,'static/profile_pics',picture_fn)
	output_size=(125,125)
	i=Image.open(form_picture)
	i.thumbnail(output_size)


	i.save(picture_path)

	return picture_fn
@users.route("/account",methods=['GET','POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file=save_picture(form.picture.data)

			current_user.image_file=picture_file

		current_user.username=form.username.data
		current_user.email=form.email.data
		db.session.commit()
		flash('your account has been updated!','success')

		return redirect(url_for('users.account'))
	elif request.method=='GET':
		form.username.data=current_user.username
		form.email.data=current_user.email
	image_file=url_for('static',filename='profile_pics/' + current_user.image_file)
	return render_template('account.html',title='Account',image_file=image_file,form=form)



@users.route("/user/<string:username>")
def user_posts(username):
	page=request.args.get('page',1,type=int)
	user=User.query.filter_by(username=username).first_or_404()
	posts=Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=3)

	return render_template('user_posts.html',posts=posts,user=user)



@users.route("/reset_password",methods=['GET','POST'])

def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form=RequestResetForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset password','info')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html',title='Reset Password',form=form)

@users.route("/reset_password/<token>",methods=['GET','POST'])

def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	user=User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token','warning')
		return redirect(url_for('users.reset_request'))

	form=RequestPasswordForm()
	if form.validate_on_submit():
		hashed_password=generate_password_hash(form.password.data)
		user.password=hashed_password
		db.session.commit()

		flash('Your password is updated!')
		return redirect(url_for('users.login'))
	return render_template('reset_token.html',title='Reset Password',form=form)