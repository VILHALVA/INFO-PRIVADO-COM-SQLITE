import requests
import json
import os
import sqlite3

class TelegramBot:
    def __init__(self):
        from TOKEN import TOKEN
        self.iURL = f"https://api.telegram.org/bot{TOKEN}/"
        self.db_path = os.path.join(os.path.dirname(__file__), 'usuarios.db') 
        self.criar_tabela()

    def criar_tabela(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                     (id INTEGER PRIMARY KEY, username TEXT, user_id INTEGER, first_name TEXT, last_name TEXT, language_code TEXT)''')
        conn.commit()
        conn.close()

    def salvar_usuario(self, username, user_id, first_name, last_name, language_code):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO usuarios (username, user_id, first_name, last_name, language_code)
                     VALUES (?, ?, ?, ?, ?)''', (username, user_id, first_name, last_name, language_code))
        conn.commit()
        conn.close()

    def Iniciar(self):
        iUPDATE_ID = None
        while True:
            ATUALIZACAO = self.ler_novas_mensagens(iUPDATE_ID)
            IDADOS = ATUALIZACAO["result"]
            if IDADOS:
                for dado in IDADOS:
                    iUPDATE_ID = dado['update_id']
                    if 'message' in dado:
                        self.processar_mensagem(dado['message'])

    def ler_novas_mensagens(self, iUPDATE_ID):
        iLINK_REQ = f'{self.iURL}getUpdates?timeout=5'
        if iUPDATE_ID:
            iLINK_REQ = f'{iLINK_REQ}&offset={iUPDATE_ID + 1}'
        iRESULT = requests.get(iLINK_REQ)
        return json.loads(iRESULT.content)

    def processar_mensagem(self, mensagem):
        texto = mensagem.get('text', '')
        if texto.startswith('/start'):
            self.gerar_resposta_start(mensagem)

    def gerar_resposta_start(self, mensagem):
        user = mensagem['from']
        response = ""
        if user:
            response += f"@{user.get('username', 'Unknown')}\n"
            response += f"SEU ID: {user['id']}\n"
            response += f"SEU NOME: {user.get('first_name', '')}\n"
            if user.get('last_name'):
                response += f"SEU SOBRENOME: {user['last_name']}\n"
            if user.get('language_code'):
                response += f"LINGUAGEM: {user['language_code']}\n"
            self.salvar_usuario(user.get('username'), user['id'], user.get('first_name'), user.get('last_name'), user.get('language_code'))
        self.responder(response, mensagem['chat']['id'])

    def responder(self, resposta, chat_id):
        iLINK_REQ = f'{self.iURL}sendMessage?chat_id={chat_id}&text={resposta}'
        requests.get(iLINK_REQ)
        print("=" * 100, "\n🤖SALVO:\n>>>" + str(resposta), "\n", "=" * 100)

if __name__ == "__main__":
    bot = TelegramBot()
    bot.Iniciar()
