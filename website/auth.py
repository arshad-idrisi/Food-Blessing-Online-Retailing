from flask import Blueprint, render_template, flash, redirect
from .forms import LoginForm, SignUpForm, PasswordChangeForm, EditProfileForm
from .models import Customer, Cart, Wishlist
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from flask import session


auth = Blueprint('auth', __name__)


#signup
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data

        if password1 == password2:
            new_customer = Customer()
            new_customer.email = email
            new_customer.username = username
            new_customer.password = password2
            new_customer.address = 'no_address'

            try:
                db.session.add(new_customer)
                db.session.commit()
                flash('Account Created Successfully, You can now Login')
                return redirect('/login')
            except Exception as e:
                print(e)
                flash('Account Not Created!!, Email already exists')

            form.email.data = ''
            form.username.data = ''
            form.password1.data = ''
            form.password2.data = ''

    return render_template('signup.html', form=form)


#login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        customer = Customer.query.filter_by(email=email).first()

        if customer:
            if customer.verify_password(password=password):
                login_user(customer)
                return redirect('/')
            else:
                flash('Incorrect Email or Password')

        else:
            flash('Account does not exist please Sign Up')

    return render_template('login.html', form=form)


#logout
@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def log_out():
    logout_user()
    return redirect('/')


#profile
@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html', cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [], wishlist=Wishlist.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


#change password
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if current_user.verify_password(current_password):
            if new_password == confirm_new_password:
                current_user.password = confirm_new_password
                db.session.commit()
                flash('Password Updated Successfully')
                return redirect('/profile')  
            else:
                flash('New Passwords do not match!!')
        else:
            flash('Current Password is Incorrect')

    return render_template('change_password.html', form=form, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                            if current_user.is_authenticated else [], wishlist=Wishlist.query.filter_by(customer_link=current_user.id).all()
                            if current_user.is_authenticated else [])


#edit profile
@auth.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        
        current_user.email = form.email.data
        current_user.username = form.username.data
        current_user.address = form.address.data
        db.session.commit()
        flash('Profile Updated Successfully')
        return redirect('/profile')  

    form.email.data = current_user.email
    form.username.data = current_user.username
    form.address.data = current_user.address

    return render_template('edit_profile.html', form=form, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                            if current_user.is_authenticated else [], wishlist=Wishlist.query.filter_by(customer_link=current_user.id).all()
                            if current_user.is_authenticated else [])
