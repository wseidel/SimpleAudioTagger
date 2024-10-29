# SimpleAudioTagger

## Avaliador manual de pronúncias

Este projeto é uma ferramenta web desenvolvida em Flask para auxiliar especialistas na qualificação manual de áudios, permitindo a análise, categorização e registro sobre a qualidade e precisão dos conteúdos em formato .wav. Com funcionalidades de organização e filtragem de arquivos, além de opções para classificar a correção dos áudios, o sistema facilita a coleta e o gerenciamento de avaliações. A interface otimiza o fluxo de trabalho, oferecendo uma plataforma centralizada para documentar e revisar resultados em projetos que dependem de observações auditivas detalhadas.


## Funcionalidades

- **Cadastro e Login de Usuário**: Validação de e-mail para o campo `username`.
- **Gestão de Arquivos `.wav`**: Listagem com filtros dinâmicos e opções de classificação.
- **Classificação de Áudio**: Opções de classificação para cada arquivo como "Correto", "Incorreto" ou "Descartar".
- **Filtro e Exclusão de Categorias**: Adição e exclusão de categorias (`filter`) com vários arquivos `.wav` associados.

## Estrutura do Projeto
. 
├── app.py # Arquivo principal do aplicativo Flask 
├── requirements.txt # Dependências do projeto 
├── templates/ # Diretório de templates HTML 
├── db_scripts/ # Diretório com scripts para inicialização
└── README.md # Documentação do projeto


## Instalação

1. **Clone este repositório**:
	```bash
	git clone https://github.com/seu-usuario/wav-file-manager.git
	cd wav-file-manager
	```

2. **Instale as dependências**:
	```bash
	python3 -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt
	```

3. **Configure o banco de dados**:
	```bash
	cat db_scripts/create_tables.sql | sqlite3 audio_files.db
	cat db_scripts/input_initial_data.sql | sqlite3 audio_files.db
	```

4. **Inicie o servidor**:
	```bash
	flask run
	```

## Contribuições

Contribuições são bem-vindas! Para mudanças maiores, abra um issue primeiro para discutirmos o que você gostaria de mudar.
