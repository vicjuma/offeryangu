from flask import Blueprint, g, render_template, \
    request, flash, jsonify, current_app, abort, redirect, url_for
from src.models import Likes, Picture, Product, User, \
    Recepient, Reviews, Subcategory, Messages
from src import db
from src.forms import SignupForm, LoginForm, AddProductForm
import datetime
import calendar
from flask_login import current_user, login_required
import os
from src.utils import cat, loc, validate_image

product = Blueprint(
    __name__, 'product', template_folder='../templates/',
    static_folder='../static/')


@product.before_request
def before():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        db.session.commit()


# Home route with / and /home route
# GET /products limited
@product.route('/', methods=['GET'])
@product.route('/home', methods=['GET'])
def home():
    signup_form = SignupForm()
    log_form = LoginForm()
    products = Product.query.filter_by().limit(16).all()
    products_autocomplete = Product.query.with_entities(
        Product.name, Product.id).filter(
            Product.name.ilike('%' + '%')).all()
    return render_template(
        'home.html', cat=cat, title="home", products=products,
        loc=loc, datetime=datetime, calendar=calendar,
        sign_form=signup_form, log_form=log_form,
        products_autocomplete=products_autocomplete)


# GET /products
@product.route('/products')
def allproducts():
    signup_form = SignupForm()
    log_form = LoginForm()
    page = request.args.get('page', type=int)
    products = Product.query.filter_by().paginate(per_page=32)
    return render_template(
        'all.html', products=products, cat=cat,
        loc=loc, page=page, calendar=calendar,
        sign_form=signup_form, log_form=log_form)


# Get /products:id
@product.route('/products/<int:id>', methods=['GET'])
def viewproduct(id):
    signup_form = SignupForm()
    log_form = LoginForm()
    page= request.args.get('page', type=int)
    product = Product.query.filter_by(id=id).first_or_404()
    pic = Picture.query.filter_by(product_id=id)
    sim = Product.query.filter_by(category=product.category).paginate(per_page=16)
    review = Reviews.query.filter_by(creator_id=product.id)
    likes = Likes.query.filter_by(product_id=product.id)
    users = User.query.filter_by()
    return render_template(
        'product.html', product=product, sim=sim, pic=pic, loc=loc,
        cat=cat, review=review, likes=likes,
        sign_form=signup_form, log_form=log_form, users=users)


# POST /products
@product.route('/products/add', methods=['GET', 'POST'])
@login_required
def addproduct():
    add_product_form = AddProductForm()
    add_product_form.product_subcategory.choices = [
        (
            subcategory.subcategory_name,
            subcategory.subcategory_name
            ) for subcategory in Subcategory.query.filter_by(
            category_name="Supermarket").all()]
    if request.method == 'POST':
        if add_product_form.validate_on_submit():
            name = add_product_form.product_name.data
            location = add_product_form.product_location.data
            market_price = add_product_form.offer_previous_price.data
            price = add_product_form.offer_current_price.data
            category = add_product_form.product_category.data
            date_ending = add_product_form.offer_end_date.data
            subcategory = request.form.get('subcategory')
            print(subcategory)
            stock = add_product_form.stock_available.data
            image_one = add_product_form.product_image_one.data
            image_2 = add_product_form.product_image_two.data
            description = add_product_form.product_description.data
            product = Product(
                name=name,
                price=price,
                description=description,
                category=category,
                stock=stock,
                subcategory=subcategory,
                date_ending=date_ending,
                owner_id=current_user.id,
                location=location,
                path_1=validate_image(image_one),
                path_2=validate_image(image_2),
                market_price=market_price
            )
            db.session.add(product)
            db.session.commit()
            flash("product added successfully", "success")
            return redirect(url_for("src.views.products.home"))
        if add_product_form.errors != {}:
            for err_msg in add_product_form.errors.values():
                flash(err_msg[0], "danger")
    return render_template(
        'create.html', cat=cat, title="Add Product",
        loc=loc, add_product_form=add_product_form)


# PATCH /products:id
@product.route('/products/update/<int:id>', methods=['GET', 'POST'])
@login_required
def updateproduct(id):
    product = Product.query.filter_by(id=id).first_or_404()
    products = Product.query.filter_by(owner_id=current_user.id)
    users = User.query.filter_by()
    if product.needs.name == current_user.name:
        if request.method == 'GET':
            return render_template(
                'update.html', product=product, loc=loc, products=products,
                cat=cat, users=users)
        name = request.form.get('name')
        price = request.form.get('price')
        desc = request.form.get('description')
        locs = request.form.get('location')
        product.name = name
        product.price = price
        product.description = desc
        product.location = locs
        db.session.commit()
        flash("product updated successfully", "success")
        return redirect(url_for('src.views.products.account'))
    abort(403)


# GET subcategories

@product.route('/subcategory/<category_name>')
def subcategory(category_name):
    subcategories = Subcategory.query.filter_by(
        category_name=category_name).all()
    subcategoryArr = []
    for subcategory in subcategories:
        subcategoryObj = {}
        subcategoryObj["id"] = subcategory.id
        subcategoryObj["subcategory_name"] = subcategory.subcategory_name
        subcategoryArr.append(subcategoryObj)
    return jsonify({"subcategories": subcategoryArr})


# POST /reviews
@product.route('/products/reviews/add/<int:id>', methods=['POST'])
@login_required
def add_review(id):
    product = Product.query.filter_by(id=id).first()
    message = request.form.get('review')
    review = Reviews(
        message=message, author_id=current_user.id,
        creator_id=product.id)
    db.session.add(review)
    db.session.commit()
    flash("review added successfully", "success")
    return redirect(url_for('src.views.products.viewproduct', id=id))


# POST /likes
@product.route('/like/product/<int:id>', methods=['POST'])
@login_required
def like(id):
    product = Product.query.filter_by(id=id).first()
    like = Likes(
        product_id=product.id, user_id=current_user.id,
        likescount=+1)
    db.session.add(like)
    db.session.commit()
    flash(
        "you liked the product by %s you can add reviews to this \
            product" % product.needs.name, "success")
    return redirect(url_for('src.views.products.home'))


# DELETE /products:id
@product.route('/delete/product/<int:id>', methods=['POST'])
@login_required
def deleteprod(id):
    product = Product.query.filter_by(id=id).first_or_404()
    pic = Picture.query.filter_by(product_id=id).all()
    if product.needs.name == current_user.name:
        if pic:
            for pics in pic:
                os.unlink(
                    os.path.join(
                        current_app.config['UPLOAD_FOLDER'],
                        pics.path))
                db.session.delete(pics)
        db.session.delete(product)
        os.unlink(os.path.join(
            current_app.config['UPLOAD_FOLDER'], product.path_1))
        os.unlink(os.path.join(
            current_app.config['UPLOAD_FOLDER'], product.path_2))
        db.session.commit()
        flash("Product deleted successfully", "success")
        return redirect(url_for('src.views.products.account'))
    else:
        abort(403)


# PATCH /products/pictures
@product.route('/add/picture/<int:id>', methods=['GET', 'POST'])
@login_required
def addphotos(id):
    prod = Product.query.filter_by(id=id).first_or_404()
    products = Product.query.filter_by(owner_id=current_user.id)
    users = User.query.filter_by()
    if prod.needs.name == current_user.name:
        if request.method == 'POST':
            pic = request.files["pic"]
            pic = Picture(
                product_id=prod.id,
                path=validate_image(pic)
            )
            db.session.add(pic)
            db.session.commit()
            return redirect(url_for('src.views.products.home'))
        return render_template(
            'addpic.html', products=products, users=users,
            loc=loc, cat=cat)
    abort(403)


# GET /search
@product.route('/search', methods=['GET'])
def search():
    signup_form = SignupForm()
    log_form = LoginForm()
    query = request.args.get('q')
    page = request.args.get('page', type=int)
    if query != None and len(query) >=2 :
        output = Product.query.msearch(query).paginate(per_page=16)
        return render_template(
            'search.html', output=output, cat=cat, loc=loc, calendar=calendar,
            sign_form=signup_form, log_form=log_form, query=query)
    abort(404)


# POST /followers
@product.route('/follow/<int:id>', methods=['POST'])
@login_required
def follow(id):
    users = User.query.filter_by(id=id).first()
    if users:
        current_user.follow(users)
        users.follow(current_user)
        db.session.commit()
        return {
            "message": 'you started following %s' % users.name
        }
    abort(404)


# DELETE /followers:id
@product.route('/unfollow/<int:id>', methods=['POST'])
@login_required
def unfollow(id):
    users = User.query.filter_by(id=id).first()
    current_user.unfollow(users)
    flash(f"you unfollowed {users.name}", 'success')
    return redirect(url_for('src.views.products.account'))


# GET /account
@product.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user_img = url_for(
        'static', filename='images/profile_pics/' + current_user.user_img)
    products = Product.query.filter_by(owner_id=current_user.id)
    messages = Messages.query.filter_by().all()
    users = User.query.filter_by()
    rec = Recepient.query.filter_by(recepient_id=current_user.id)
    return render_template(
        'account.html', products=products, loc=loc,
        cat=cat, users=users, rec=rec, user_img=user_img, messages=messages)


@product.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    query = Product.query(Product.name).filter(
        Product.name.like('%' + str(search) + '%'))
    results = [mv[0] for mv in query.all()]
    return jsonify(matching_results=results)
