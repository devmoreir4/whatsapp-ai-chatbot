from flask import Flask, request, jsonify
from decouple import config

from bot.ai_bot import AIBot
from services.waha import Waha


app = Flask(__name__)


@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.json
    chat_id = data['payload']['from']
    received_message = data['payload']['body']
    is_group = '@g.us' in chat_id

    if is_group:
        return jsonify({'status': 'success', 'message': 'Group message ignored.'}), 200

    waha = Waha()
    ai_bot = AIBot()

    waha.start_typing(chat_id=chat_id)
    history_limit = config('HISTORY_LIMIT', default=10, cast=int)
    history_messages = waha.get_history_messages(
        chat_id=chat_id,
        limit=history_limit,
    )
    response_message = ai_bot.get_response(
        question=received_message,
        chat_history=history_messages,
    )
    waha.send_message(
        chat_id=chat_id,
        message=response_message,
    )
    waha.stop_typing(chat_id=chat_id)

    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    host = config('FLASK_HOST', default='0.0.0.0')
    port = config('FLASK_PORT', default=5000, cast=int)
    debug = config('FLASK_DEBUG', default=True, cast=bool)
    app.run(host=host, port=port, debug=debug)
