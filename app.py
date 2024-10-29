import re

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Nome do banco de dados SQLite
DB_NAME = 'audio_files.db'

# Modelo de usuário para Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

# Função para validar o e-mail
def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None


@login_manager.user_loader
def load_user(user_id):
    # Conectar ao banco de dados e buscar o usuário pelo ID
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return User(*user_data)
    return None



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validação do e-mail
        if not is_valid_email(username):
            flash("O campo 'username' deve ser um e-mail válido.", "error")
            return redirect(url_for('register'))

        # Gerar hash da senha
        password_hash = generate_password_hash(password)

        # Salvar o usuário no banco de dados
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Usuário já existe!')
            return redirect(url_for('register'))
        conn.close()

        flash('Usuário registrado com sucesso!')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Verificar se o usuário existe e a senha está correta
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and check_password_hash(user_data[2], password):
            user = User(*user_data)
            login_user(user)
            flash('Login bem-sucedido!')
            return redirect(url_for('home'))  # Redirecionar para a página principal
        else:
            flash('Login ou senha incorretos!')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.')
    return redirect(url_for('login'))



# Página Home: Lista apenas as palavras únicas
@app.route('/')
@login_required
def home():
    # Conectar ao banco de dados
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    filter_type = request.args.get('filter_type')
    sql_filter = ''
    if filter_type:
        sql_filter = f"JOIN wav_file_to_check ON wav_file_to_check.wav_file = wav_data.wav_file AND wav_file_to_check.filter = '{filter_type}'"


    # Buscar todas as palavras únicas
    sql = f'''
        SELECT wav_data.palavra, count(*) as qnt 
        FROM wav_data
        {sql_filter}
        GROUP BY wav_data.palavra 
        ORDER BY wav_data.palavra
    '''
    # cursor.execute('SELECT  palavra, count(*) as qnt FROM wav_data GROUP BY palavra ORDER BY palavra')
    cursor.execute(sql)
    palavras = cursor.fetchall()

    sql = f'select distinct filter from wav_file_to_check'
    cursor.execute(sql)
    filters = cursor.fetchall()


    # Fechar a conexão
    conn.close()

    return render_template('home.html', 
                        palavras=palavras, 
                        filter_type=filter_type,
                        filters=filters)

# Página Wav Files: Lista os arquivos .wav filtrados pela palavra selecionada
@app.route('/wavfiles/<palavra>')
@login_required
def wav_files(palavra):
    
    filter_type = request.args.get('filter_type')

    # Conectar ao banco de dados
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # user_id = current_user.id  # Pega o ID do usuário logado
    username = current_user.username  # Obtém o username do usuário logado

    # Paginação
    page = request.args.get('page', 1, type=int)  # Página atual, padrão é 1
    page_size = 10  # Número de registros por página

    offset = (page - 1) * page_size  # Cálculo para o deslocamento

    sql_filter = ''
    if filter_type:
        sql_filter = f"JOIN wav_file_to_check ON wav_file_to_check.wav_file = wav_data.wav_file AND wav_file_to_check.filter = '{filter_type}'"


    # Buscar todos os dados filtrados pela palavra selecionada
    sql = f'''
    SELECT wav_data.wav_file, wav_data.palavra, wav_data.falado, wav_data.tipo, wav_data.is_error, wav_data.docid, user_choices.user_choice
    FROM wav_data
    {sql_filter}
    LEFT JOIN user_choices ON wav_data.wav_file = user_choices.wav_file AND user_choices.username = ?
    WHERE wav_data.palavra = ? 
    ORDER BY wav_data.wav_file
        LIMIT ? OFFSET ?
    '''    

    print(sql)

    cursor.execute(sql, (username, palavra, page_size, offset))
    wav_files = cursor.fetchall()

    cursor.execute(f"""
        SELECT COUNT(*) 
        FROM wav_data
        {sql_filter}
        WHERE wav_data.palavra = ? 
    """, (palavra,))
    total_items = cursor.fetchone()[0]
    total_pages = (total_items + page_size - 1) // page_size  # Total de páginas (arredondando para cima)




    sql = f'select distinct filter from wav_file_to_check'
    cursor.execute(sql)
    filters = cursor.fetchall()

    conn.close()

    print( "page..........: ", page )
    print( "page_size.....: ", page_size )
    print( "offset........: ", offset )
    print( "total_items...: ", total_items )
    print( "total_pages...: ", total_pages )

    return render_template('wavfiles.html', 
                        wav_files=wav_files, 
                        page=page, 
                        total_pages=total_pages, 
                        palavra=palavra, 
                        filter_type=filter_type,
                        filters=filters)






@app.route('/update_choice', methods=['POST'])
@login_required
def update_choice():
    try:
        # Receber os dados do POST
        data = request.json
        wav_file = data.get('wav_file')
        choice = data.get('choice')

        # user_id = current_user.id  # ID do usuário logado
        username = current_user.username  # Obtém o username do usuário logado
        print(f"Estamos aqui com o {username}!")

        # Conectar ao banco de dados
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Insere ou atualiza a escolha para o usuário logado com base no username
        cursor.execute("""
            INSERT INTO user_choices(wav_file, username, user_choice) VALUES (?, ?, ?)
            ON CONFLICT(wav_file, username) DO UPDATE SET user_choice=excluded.user_choice
        """, (wav_file, username, choice ))

        # Salvar e fechar a conexão
        conn.commit()
        conn.close()

        # Retornar a resposta JSON de sucesso
        return jsonify({"status": "success"})

    except Exception as e:
        # Log de erro para ver o que aconteceu
        print(f"Erro ao processar a escolha: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500





# Rota para listar os filtros únicos
@app.route('/filters')
@login_required
def list_filters():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # cursor.execute
    filters = cursor.execute("SELECT DISTINCT filter FROM wav_file_to_check").fetchall()
    conn.close()

    return render_template('list_filters.html', filters=filters)



# Rota para excluir todos os arquivos associados a um filtro específico
@app.route('/delete_filter/<filter_text>', methods=['POST'])
@login_required
def delete_filter(filter_text):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM wav_file_to_check WHERE filter = ?", (filter_text,))

    # Salvar e fechar a conexão
    conn.commit()
    conn.close()
    flash(f"Filtro '{filter_text}' e seus WAV files associados foram excluídos.", "success")
    return redirect(url_for('list_filters'))


# Rota para exibir todos os arquivos associados a um filtro específico
@app.route('/view_filter/<filter_text>')
@login_required
def view_filter(filter_text):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    wav_files = cursor.execute("SELECT * FROM wav_file_to_check WHERE filter = ?", (filter_text,)).fetchall()
    conn.close()
    count_wav_files = len(wav_files)

    return render_template('view_filter_wav_files.html', 
                wav_files=wav_files, 
                filter_text=filter_text,
                count_wav_files=count_wav_files
                )



# Rota para exibir o formulário de inserção de filtro e wav_files
@app.route('/add_filter', methods=['GET', 'POST'])
@login_required
def add_filter():
    if request.method == 'POST':
        filter_text = request.form['filter']
        wav_files_text = request.form['wav_files']
        wav_files = wav_files_text.strip().splitlines()  # Separa cada linha em um wav_file

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        for wav_file in wav_files:
            try:
                cursor.execute("""
                    INSERT INTO wav_file_to_check (filter, wav_file) VALUES (?, ?)
                    ON CONFLICT(wav_file, filter) DO NOTHING
                """, (filter_text, wav_file.strip()))
            except Exception as e:
                flash(f"Erro ao inserir wav_file '{wav_file}': {e}", "error")
        
        conn.commit()
        conn.close()
        flash("WAV files adicionados com sucesso!", "success")
        return redirect(url_for('list_filters'))
    
    return render_template('add_filter.html')


if __name__ == '__main__':
    # app.run(debug=True)
    # app.run(debug=True, threaded=True)
    app.run(debug=True, host="0.0.0.0", port=5005)



