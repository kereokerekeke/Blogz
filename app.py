from flask import Flask, request, redirect, flash, render_template, session
from models import db, Blog, User


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'WowSoSecretMuchCharactersWow'

db.init_app(app)


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in", category="alert-success")
            return redirect('/')
        else:
            flash('User password is incorrect or user does not exist', category="alert-danger")
            return redirect('/')

    return render_template('login.html')    


@app.route('/logout', methods=['GET', 'POST'])
def logout():

    del session['username']
    return redirect('/blog')    


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(blog_title, blog_body, owner.id)
        if len(new_blog.body) > 1000:
            flash('Body of the post can not be longer than 1000 characters', category='alert-danger')
            return redirect('/newpost')
        if not new_blog.title or not new_blog.body:
            flash('Title or body can not be empty', category='alert-danger')
            return redirect('/newpost')
        db.session.add(new_blog)
        db.session.commit()
        flash('Post created', category='alert-success')
        return redirect('/blog?id={user_id}'.format(user_id=new_blog.owner_id))
    
    return render_template('newpost.html')


@app.route('/blog')
def blog():
    
    blog_id = request.args.get('blog_id')
    user_id = request.args.get('user')
    
    if user_id:
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html',
                               blogs=blogs)
    
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('post.html',
                               blog=blog)
    
    blogs = Blog.query.order_by(Blog.created_at).all()
    
    return render_template('blog.html',
                           blogs=blogs)
    

def check_validity(type, string):
    error = False

    if (string != ''):
        if (' ' in string) or (3 > len(string) or len(string) > 21):
            error = True
    else:
        error = True
    
    if error:
        return type + ' not valid' 
    else:
        return ''


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    
    username_error = ''
    password_error = ''
    verify_error = ''
    username = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = check_validity('Username', username)
        password_error = check_validity('Password', password)
            
        if verify != password:
            verify_error = 'Passwords do not match'
        
        if not username_error and not password_error and not verify_error:
            pass
        else:
            for err in [username_error, password_error, verify_error]:
                if err:
                    flash(err, category="alert-danger")
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            flash('User already exists', category='alert-danger')
            return redirect('/signup')
    
    return render_template('signup.html')
    

@app.route('/')
def index():
    
    users = User.query.all()
    
    return render_template('index.html',
                           users=users)


if __name__ == '__main__':
    app.run()