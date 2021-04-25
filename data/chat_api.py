from flask import Blueprint, jsonify, make_response
from data import db_session
from data.messages import Messages

blueprint = Blueprint(
    'chat_api',
    __name__,
    template_folder='templates'
)


@blueprint.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@blueprint.route('/api/get_all_messages')
def get_messages():
    db_sess = db_session.create_session()
    messages = db_sess.query(Messages).all()
    return jsonify(
        {
            'messages':
                [item.to_dict() for item in messages]
        }
    )


@blueprint.route('/api/get_message_by_id/<int:message_id>')
def get_one_message(message_id):
    if type(message_id) != int:
        raise 404
    db_sess = db_session.create_session()
    message = db_sess.query(Messages).filter(Messages.id == message_id).first()
    if not message:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'messages': message.to_dict()
        }
    )


