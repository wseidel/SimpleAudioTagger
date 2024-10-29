import sqlite3
import csv

# Nome do banco de dados SQLite
DB_NAME = 'audio_files.db'

# Caminho para o arquivo CSV
CSV_FILE = '../datasets/corpus-mec-ita/99_output/base_pseudo_palavras/metadata.csv'

# Conectar ao banco de dados (ou criar se não existir)
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Criar a tabela se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS wav_data (
    wav_file TEXT PRIMARY KEY,
    palavra TEXT,
    falado TEXT,
    tipo TEXT,
    is_error INTEGER,
    docid TEXT
)
''')

# Criar a tabela para armazenar as opções do usuário
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_choices (
    wav_file TEXT PRIMARY KEY,
    user_choice TEXT,
    FOREIGN KEY(wav_file) REFERENCES wav_data(wav_file)
)
''')

# Ler o CSV e inserir os dados no banco de dados
with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile,  delimiter=';')
    for row in reader:
        cursor.execute('''
        INSERT OR IGNORE INTO wav_data (wav_file, palavra, falado, tipo, is_error, docid)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (row['wav_file'], row['palavra'], row['falado'], row['tipo'], row['is_error'], row['docid']))

# Salvar e fechar a conexão
conn.commit()
conn.close()

print("Banco de dados alimentado com os dados do CSV.")
