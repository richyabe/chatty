from datetime import timedelta
import hashlib
import os
from flask import flash, redirect, request, render_template, session, url_for, send_from_directory
from app import app
from app import db
from models import Blog, User
from auth import check_login
from werkzeug.utils import secure_filename

    
@app.route('/')
def home_page():
    current_user = None  # Initialize as None

    if 'user_id' in session:
        user_id = session['user_id']
        current_user = User.query.get(user_id)  # Fetch user from DB

    blogs = Blog.query.order_by(Blog.date_published.desc()).all()
    
    return render_template('index.html', current_user=current_user, blogs=blogs, session=session)


@app.route('/admin')
def admin_page():
   users=User.query.all()
   return render_template('admin.html', users=users)

@app.route('/signup')
def sign_up():
    return render_template('signup.html')

@app.route('/do-signup', methods=['POST'])
def do_signup():
   username = request.form.get('username')
   email = request.form.get('email')
   phone = request.form.get('phone')
   password = request.form.get('password')
   confirmpassword = request.form.get('confirmpassword')
   # validation
   if username == '':
      flash('Please enter your username!')
      return redirect(url_for('sign_up'))
   elif email == '':
      flash('Please enter your email')
      return redirect(url_for('sign_up'))
   if User.query.filter_by(email=email).first():
       flash('Email already exists. Please use a different email.', 'error')
       return redirect(url_for('sign_up'))
   elif phone == '':
      flash('Please enter your Phone Number')
      return redirect(url_for('sign_up'))
   
   elif password  != confirmpassword:
      flash('Please enter correct password')
      return redirect(url_for('sign_up'))
   

   # hash the password
   pw = hashlib.sha256(password.encode()).hexdigest()
   # save the user details 
   new_user = User(username = username, email=email, phone = phone, 
                   password_hash=pw)
   db.session.add(new_user)
   db.session.commit()
   flash('Account Created successfully, please login.' ,'success')
   return redirect(url_for('login_page'))

@app.route('/blog')
def blog():
   #  users = User.query.all()  # Fetch all users
   #  blogs = Blog.query.order_by(Blog.date_published.desc()).all()  # Get all blogs
   #  return render_template('blog.html', users=users, blogs=blogs)

    profile = check_login()    
    blogs = Blog.query.order_by(Blog.date_published.desc()).all()  # Newest first
    return render_template('index.html', current_user=profile, blogs=blogs, session=session)

@app.route('/add')
def add_post():
    users = User.query.all()  # Fetch all users
    
    # Check if a user is logged in
    current_user = None
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])

    return render_template('blog.html', users=users, current_user=current_user)  # ✅ Pass current_user

@app.route('/login')
def login_page():
    return render_template ('login.html')

@app.route('/create-blog', methods=['POST'])
def create_blog():
    if 'user_id' not in session:
        flash("You need to log in first!", "danger")
        return redirect(url_for('login_page')) 
    user = User.query.get(session['user_id'])  # Get the logged-in user

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        if not title or not description:
            flash("Title and description are required!", "danger")
            return redirect(url_for('blog'))

        new_blog = Blog(title=title, description=description, user_id=user.id)
        db.session.add(new_blog)
        db.session.commit()

        flash("Blog post created successfully!", "success")
        return redirect(url_for('home_page'))  # Redirect to homepage after posting

    blogs = Blog.query.order_by(Blog.date_published.desc()).all()  # Get all blogs
    return render_template('blog.html', user=user, blogs=blogs)
   
@app.route('/process-login', methods=['POST'])
def process_login():
   email = request.form.get('email')
   password = request.form.get('password')
   if email == '':
      flash('Please enter email.', 'error')
      return redirect(url_for('login_page'))
   # find user in database
   correct_user = User.query.filter(User.email == email).first()
   if correct_user is None:
      flash('Invalid email or password', 'error')
      return redirect(url_for('login_page'))
   # hash password
   pw = hashlib.sha256(password.encode()).hexdigest()
   # check if password is the same
   if correct_user.password_hash != pw:
      flash('Invalid email or password', 'error')
      return redirect(url_for('login_page'))
   # login is correct 
   session['user_id'] = correct_user.id  # Instead of session['id']
   resp = redirect(url_for('home_page'))
   # set cookie
   resp.set_cookie('id', str(correct_user.id), max_age=timedelta(days=5))
   resp.set_cookie('p_hash', pw, max_age=timedelta(days=5))
   return resp

@app.route('/edit-blog/<int:blog_id>', methods=['GET', 'POST'])
def edit_blog(blog_id):
    if 'user_id' not in session:  # Ensure user is logged in
        flash('You need to log in to edit a post.', 'error')
        return redirect(url_for('login_page')) 

    current_user = check_login()  # Get the logged-in user

    if not current_user:
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('login_page'))

    blog = Blog.query.get_or_404(blog_id)

    # Check if the logged-in user is the owner of the post
    if blog.user_id != current_user.id:
        abort(403)  # Forbidden access if the user is not the owner

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        if not title or not description:
            flash('Title and description are required.', 'error')
        else:
            blog.title = title
            blog.description = description
            db.session.commit()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('home_page'))

    return render_template('edit_blog.html', blog=blog, current_user=current_user)

 
@app.route('/delete-blog/<int:blog_id>', methods=['POST'])
def delete_blog(blog_id):
    if 'user_id' not in session:
        flash('You need to log in to delete a post.', 'error')
        return redirect(url_for('login'))

    blog = Blog.query.get_or_404(blog_id)  # Fetch the blog, return 404 if not found

    # Check if the logged-in user is the owner of the post
    if blog.user_id != session['user_id']:
        abort(403)  # Forbidden

    db.session.delete(blog)  
    db.session.commit()  

    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('home_page'))

@app.route('/my_posts')
def my_posts():
    if 'user_id' not in session:
        flash('You need to log in first!', 'warning')
        return redirect(url_for('login'))
    
    profile = check_login()  # Assuming this function fetches user details
  # Order posts by latest date
    user_posts = Blog.query.filter_by(user_id=session['user_id']).order_by(Blog.date_published.desc()).all()


    return render_template('my_posts.html', blogs=user_posts, current_user=profile)




@app.route('/logout')
def logout():
   # clear session
   session.pop('user_id')
   # expire cookies
   resp = redirect(url_for('login_page'))
   resp.set_cookie('user_id', expires=0)
   resp.set_cookie('p_hash', expires=0)
   flash("You are Logged Out!")
   return resp
   # return render_template('login.html')


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('You need to log in to view your profile.', 'error')
        return redirect(url_for('login'))

    current_user = User.query.get(session['user_id'])  # Fetch the logged-in user

    if not current_user:  # Ensure user exists
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('login'))
     
    post_count = Blog.query.filter_by(user_id=current_user.id).count()  # ✅ Use current_user.id

    return render_template('profile.html', current_user=current_user, post_count=post_count)  # ✅ Pass current_user


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        flash('You need to log in to access settings.', 'error')
        return redirect(url_for('login'))

    current_user = User.query.get(session['user_id'])

    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')

        if new_username:
            user.username = new_username
        if new_email:
            user.email = new_email

        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('settings.html',  current_user=current_user)