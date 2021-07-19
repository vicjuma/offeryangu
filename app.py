from src import create_app
from flask import render_template, abort, json
from flask_socketio import SocketIO, emit
from src.models import User, Messages, Recepient, Likes
from src import db
from flask_login import current_user, login_required
import click
import os
import unittest
import math
import pymysql
from werkzeug.exceptions import HTTPException

pymysql.install_as_MySQLdb()

app = create_app()


def generate_code(sender: int, recepient: int) -> str:
    response = str(sender) + '_' + str(recepient)
    return response


socket = SocketIO(app)


# first id for the client and 2nd id for the seller
@app.route('/start/converse/<int:clientid>/<int:sellerid>')
@login_required
def chat(clientid, sellerid):
    user = User.query.filter_by()
    if clientid != sellerid:
        client = User.query.filter_by(id=clientid).first_or_404()
        seller = User.query.filter_by(id=sellerid).first_or_404()
        # client to sender
        if client.id != current_user.id:
            abort(404)
        msg = Messages.query.filter((
            Messages.code1 == generate_code(client.id, seller.id)) | (
                Messages.code1 == generate_code(
                    seller.id, client.id))).order_by(
                        Messages.date_created.asc())
        return render_template(
            'chat.html', client=client, seller=seller, user=user, msg=msg)
    abort(404)


@socket.on('receive message')
def get_message(data):
    sender = User.query.filter_by(id=int(data['sender'])).first()
    rec = User.query.filter_by(id=int(data['recepient'])).first()
    code = generate_code(sender.id, rec.id)
    txt = Messages(
        message=data['message'],
        sender_id=sender.id,
        code1=code
    )
    recepient = Recepient(
        recepient_id=rec.id,
        code2=code
    )

    db.session.add(txt)
    db.session.add(recepient)
    db.session.commit()
    emit(
        'broadcast', {
            "message": data['message'],
            "sender id": sender.id,
            "recepient": rec.id}, broadcast=True)


@app.cli.command(help="run tests in the application")
@click.option(
    "--filetest",
    help="enter the name of your test file", default='.', type=str)
def test(filetest):
    tests = unittest.TestLoader().discover(os.path.splitext(filetest)[0])
    unittest.TextTestRunner(verbosity=2).run(tests)


# filter to calculate discount
@app.template_filter('round')
def round_discount(number: int) -> int:
    return math.trunc(number)


@app.template_filter('likes')
def get_likes(number):
    return Likes.query.filter_by(product_id=number).all()


@app.template_filter('pipe')
def pipe_likes(number):
    return Likes.query.filter_by(product_id=number).count()


@login_required
@app.template_filter('restrictlikes')
def restrict_likes(product_id):
    res = []
    for x in product_id:
        res.append(x.user_id)
    if current_user.id in res:
        return False
    return True


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


app.jinja_env.filters['round'] = round_discount
app.jinja_env.filters['likes'] = get_likes
app.jinja_env.filters['pipe'] = pipe_likes
app.jinja_env.filters['restrict'] = restrict_likes


if __name__ == '__main__':
    socket.run(app, debug=True, port=4000)
