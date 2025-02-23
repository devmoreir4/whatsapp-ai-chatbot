from flask import Flask, request, jsonify, send_from_directory

from bot.ai_bot import AIBot
from services.waha import Waha
from commands.commands import handle_command

import os


app = Flask(__name__)

# rota alternativa para imagens
@app.route('/images/<path:filename>')
def serve_image(filename):
    image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'commands', 'images')
    return send_from_directory(image_dir, filename)

@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.json
    chat_id = data['payload']['from']
    received_message = data['payload']['body']
    is_group = '@g.us' in chat_id

    if is_group:
        return jsonify({'status': 'success', 'message': 'Mensagem de grupo ignorada.'}), 200

    waha = Waha()

    if received_message.startswith("/"):
        if handle_command(waha, chat_id, received_message):
            return jsonify({'status': 'success'}), 200

    ai_bot = AIBot()

    waha.start_typing(chat_id=chat_id)
    history_messages = waha.get_history_messages(
        chat_id=chat_id,
        limit=10,
    )
    response_message = ai_bot.invoke(
        history_messages=history_messages,
        question=received_message,
    )
    waha.send_message(
        chat_id=chat_id,
        message=response_message,
    )
    waha.stop_typing(chat_id=chat_id)

    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
