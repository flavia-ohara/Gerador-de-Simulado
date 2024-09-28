import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Conecta ao banco de dados SQLite e cria tabelas
conn = sqlite3.connect('BD_Simulado.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS aluno (
    aluno_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_unico TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    serie INTEGER NOT NULL,
    grau_ensino TEXT NOT NULL,
    email TEXT,
    telefone TEXT       
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS questao (
    questao_id INTEGER PRIMARY KEY AUTOINCREMENT,
    enunciado TEXT NOT NULL,
    resposta_correta TEXT NOT NULL,
    tema TEXT NOT NULL,
    serie INTEGER NOT NULL,
    grau_ensino TEXT NOT NULL,
    nivel_dificuldade TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS simulado (
    simulado_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    aluno_id INTEGER,
    tema TEXT NOT NULL,
    nivel_dificuldade TEXT NOT NULL,
    data_geracao TEXT,
    FOREIGN KEY(aluno_id) REFERENCES aluno(aluno_id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS simulado_questao (
    simulado_questao_id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulado_id INTEGER,
    questao_id INTEGER,
    FOREIGN KEY(simulado_id) REFERENCES simulado(simulado_id),
    FOREIGN KEY(questao_id) REFERENCES questao(questao_id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS resultado_simulado (
    resultado_id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulado_id INTEGER,
    aluno_id INTEGER,
    nota FLOAT,
    data_realizacao TEXT,
    FOREIGN KEY(simulado_id) REFERENCES simulado(simulado_id),
    FOREIGN KEY(aluno_id) REFERENCES aluno(aluno_id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS resposta_aluno (
    resposta_id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    simulado_id INTEGER,
    questao_id INTEGER,
    resposta_aluno TEXT,
    correta BOOLEAN NOT NULL,
    FOREIGN KEY(aluno_id) REFERENCES aluno(aluno_id),    
    FOREIGN KEY(simulado_id) REFERENCES simulado(simulado_id),
    FOREIGN KEY(questao_id) REFERENCES questao(questao_id)
)
''')

# Salva as mudanças e fecha a conexão temporária
conn.commit()
conn.close()

# Adiciona aluno
def add_aluno(entry_nome_unico_aluno, entry_nome_aluno, entry_serie_aluno, entry_grau_aluno, entry_email_aluno, entry_tel_aluno):
    nome_unico = entry_nome_unico_aluno.get()
    nome = entry_nome_aluno.get()
    serie = entry_serie_aluno.get()
    grau_ensino = entry_grau_aluno.get()
    email = entry_email_aluno.get()
    telefone = entry_tel_aluno.get()

    conn = sqlite3.connect('BD_Simulado.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO aluno (nome_unico, nome, serie, grau_ensino, email, telefone) VALUES (?, ?, ?, ?, ?, ?)", (nome_unico, nome, serie, grau_ensino, email, telefone))
        conn.commit()
        messagebox.showinfo("Sucesso", "Aluno adicionado com sucesso!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Aluno já cadastrado!")
    finally:
        conn.close()

# Adiciona questão
def add_questao(entry_enunciado,entry_resposta_correta,entry_tema,entry_serie,entry_grau,entry_nivel):
    enunciado = entry_enunciado.get()
    resposta_correta = entry_resposta_correta.get()
    tema = entry_tema.get()
    serie = entry_serie.get()
    grau_ensino = entry_grau.get()
    nivel_dificuldade = entry_nivel.get()

    conn = sqlite3.connect('BD_Simulado.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO questao (enunciado, resposta_correta, tema, serie, grau_ensino, nivel_dificuldade) VALUES (?, ?, ?, ?, ?, ?)", 
                  (enunciado, resposta_correta, tema, serie, grau_ensino, nivel_dificuldade))
        conn.commit()
        messagebox.showinfo("Sucesso", "Questão adicionada com sucesso!")
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao adicionar questão: {e}")
    finally:
        conn.close()

# Gera simulado
def gerar_e_salvar_simulado(entry_nome_aluno,entry_tema,entry_nivel,entry_num_questoes):
    nome_aluno = entry_nome_aluno.get()
    tema = entry_tema.get()
    nivel_dificuldade = entry_nivel.get()
    num_questoes = int(entry_num_questoes.get())

    conn = sqlite3.connect('BD_Simulado.db')
    c = conn.cursor()

    # Obtém dados do aluno
    c.execute('''
    SELECT aluno_id, serie, grau_ensino
    FROM aluno
    WHERE nome_unico = ?
    ''', (nome_aluno,))

    aluno = c.fetchall()
    
    if not aluno:
        messagebox.showinfo("Informação", "Aluno não identifcado.")
        conn.close()
        return

    aluno_id = aluno[0][0]
    serie = aluno[0][1]
    grau_ensino = aluno[0][2]
    
    # Seleciona questões
    c.execute('''
    SELECT q.questao_id, q.enunciado
    FROM questao q
    LEFT JOIN (
        SELECT questao_id, correta
        FROM resposta_aluno
        WHERE aluno_id = ?
    ) AS respostas ON q.questao_id = respostas.questao_id
    WHERE (respostas.questao_id IS NULL OR respostas.correta = 0)
    AND q.tema = ?
    AND q.serie = ?
    AND q.grau_ensino = ?
    AND q.nivel_dificuldade = ?
    LIMIT ?
    ''', (aluno_id, tema, serie, grau_ensino, nivel_dificuldade,num_questoes,))

    questoes_selecionadas = c.fetchall()

    if not questoes_selecionadas:
        messagebox.showinfo("Informação", "Não há questões disponíveis para os critérios selecionados.")
        conn.close()
        return

    # Insere novo simulado no banco de dados
    nome_simulado = f"Simulado {nome_aluno} - {tema} - {nivel_dificuldade}"
    data_geracao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO simulado (nome, descricao, aluno_id, tema, nivel_dificuldade, data_geracao) VALUES (?, ?, ?, ?, ?, ?)",
              (nome_simulado, f"Simulado gerado automaticamente para o aluno {nome_aluno}, tema: {tema}, dificuldade: {nivel_dificuldade}", aluno_id, tema, nivel_dificuldade, data_geracao))
    simulado_id = c.lastrowid

    # Insere as questões selecionadas no simulado
    questoes = [questao[0] for questao in questoes_selecionadas]
    for questao_id in questoes:
        c.execute("INSERT INTO simulado_questao (simulado_id, questao_id) VALUES (?, ?)", (simulado_id, questao_id))

    conn.commit()

    # Exporta simulado
    nome_arquivo = exportar_simulado(simulado_id, questoes_selecionadas, nome_simulado)

    conn.close()
    messagebox.showinfo("Simulado Gerado e Exportado", f"Simulado gerado e exportado para um arquivo como '{nome_arquivo}'.")

# Exporta simulado para um arquivo de texto
def exportar_simulado(simulado_id, questoes_selecionadas, nome_simulado):
    nome_simulado_completo = f"{simulado_id} - {nome_simulado}"
    nome_arquivo = f"{nome_simulado_completo.replace(' ', '_')}.txt"

    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        for questao_id, enunciado in questoes_selecionadas:
            f.write(f"\nQuestão ID: {questao_id}\n")
            f.write(f"{enunciado}\n")         
    print(f"Simulado exportado para {nome_arquivo}")
    return nome_arquivo


# Abre formulário de cadastro de respostas do simulado
def abrir_form_resposta(entry_nome_aluno,entry_simulado,entry_data):
    nome_aluno = entry_nome_aluno.get()
    simulado_id = entry_simulado.get()
    data_realizacao = entry_data.get()

    conn = sqlite3.connect('BD_Simulado.db')
    c = conn.cursor()

    # Obtém dados do aluno
    c.execute('''
    SELECT aluno_id
    FROM aluno
    WHERE nome_unico = ?
    ''', (nome_aluno,))

    aluno = c.fetchall()
    
    if not aluno:
        messagebox.showinfo("Informação", "Aluno não identifcado.")
        conn.close()
        return

    aluno_id = aluno[0][0]

    # Obtém dados do Simulado
    c.execute('''
    SELECT q.questao_id, q.resposta_correta
    FROM questao q
    INNER JOIN simulado_questao sq ON q.questao_id = sq.questao_id
    WHERE sq.simulado_id = ?
    ''', (simulado_id,))

    respostas = c.fetchall()
    
    if not respostas:
        messagebox.showinfo("Informação", "Simulado não identificado.")
        conn.close()
        return

    janela_respostas = tk.Toplevel()
    janela_respostas.title("Inserir Respostas")  
    
    respostas_aluno = []

    for questao, resposta_correta in respostas:
        tk.Label(janela_respostas, text=f"Questão ID: {questao}").pack(pady=5)
        entry_resposta = tk.Entry(janela_respostas)
        entry_resposta.pack(pady=5)
        linha = (questao, resposta_correta, entry_resposta)
        respostas_aluno.append(linha)

    # Botão para corrigir o simulado
    btn_corrigir = tk.Button(janela_respostas, text="Corrigir", command=lambda:corrigir_simulado(nome_aluno, aluno_id, simulado_id, data_realizacao, respostas_aluno))
    btn_corrigir.pack(pady=20)

# Corrige o simulado
def corrigir_simulado(nome_aluno, aluno_id, simulado_id, data_realizacao, respostas_aluno):
    conn = sqlite3.connect('BD_Simulado.db')
    c = conn.cursor()

    nota = 0
    resultados = []
    for questao_id, resposta_correta, entry_resposta in respostas_aluno:
        resposta_aluno = entry_resposta.get()
        correta = resposta_aluno.lower().strip() == resposta_correta.lower().strip()
        if correta:
            nota += 1
            linha = (questao_id, resposta_correta, resposta_aluno, "Correto")
        else:
            linha = (questao_id, resposta_correta, resposta_aluno, "Errado")
        c.execute("INSERT INTO resposta_aluno (aluno_id, simulado_id, questao_id, resposta_aluno, correta) VALUES (?, ?, ?, ?, ?)",
                    (aluno_id, simulado_id, questao_id, resposta_aluno, correta))
        resultados.append(linha)

    total_questoes = len(respostas_aluno)
    nota_final = (nota / total_questoes) * 100 

    # Salva resultado final
    c.execute("INSERT INTO resultado_simulado (simulado_id, aluno_id, nota, data_realizacao) VALUES (?, ?, ?, ?)",
              (simulado_id, aluno_id, nota_final, data_realizacao))

    conn.commit()
    conn.close()

    messagebox.showinfo("Correção Finalizada", f"Nota final do aluno {nome_aluno}: {nota} de {total_questoes} ou {nota_final}%")

    mostrar_resultados(nota_final, resultados)

# Mostra os resultados
def mostrar_resultados(nota, resultados):
    janela_resultados = tk.Toplevel()
    janela_resultados.title("Resultados do Simulado")

    # Exibe a nota
    tk.Label(janela_resultados, text=f"Nota: {nota:.2f}%", font=("Arial", 14)).pack(pady=10)

    # Exibe cada questão e resultado
    for questao_id, resposta_correta, resposta_aluno, status in resultados:
        tk.Label(janela_resultados, text=f"Questão ID: {questao_id}").pack()
        tk.Label(janela_resultados, text=f"Resposta Correta: {resposta_correta}").pack()
        tk.Label(janela_resultados, text=f"Resposta do Aluno: {resposta_aluno}").pack()
        tk.Label(janela_resultados, text=f"Resultado: {status}").pack()
        tk.Label(janela_resultados, text="").pack()

# Mostra Relatório de Desempenho
def gerar_relatorio(entry_nome_aluno):
    nome_aluno = entry_nome_aluno.get()

    conn = sqlite3.connect('BD_Simulado.db')
    c = conn.cursor()

    # Obtém dados do aluno
    c.execute('''
    SELECT aluno_id
    FROM aluno
    WHERE nome_unico = ?
    ''', (nome_aluno,))

    aluno = c.fetchall()
    
    if not aluno:
        messagebox.showinfo("Informação", "Aluno não identifcado.")
        conn.close()
        return

    aluno_id = aluno[0][0]

    # Obtém resultados dos simulados
    c.execute('''
    SELECT rs.simulado_id, s.tema, s.nivel_dificuldade, rs.nota, rs.data_realizacao
    FROM resultado_simulado rs
    LEFT JOIN simulado s ON rs.simulado_id = s.simulado_id
    WHERE rs.aluno_id = ?
    ''', (aluno_id,))

    resultado = c.fetchall()
    
    if not resultado:
        messagebox.showinfo("Informação", "Não há dados para o Relatório de Desempenho do aluno.")
        conn.close()
        return

    janela_relatorio = tk.Toplevel()
    janela_relatorio.title("Relatório de Desempenho")

    # Exibe nome do aluno
    tk.Label(janela_relatorio, text=f"Aluno: {nome_aluno}", font=("Arial", 14)).pack(pady=10)

    # Exibe cada resultado
    for simulado_id, tema, nivel_dificuldade, nota, data_realizacao in resultado:
        tk.Label(janela_relatorio, text=f"Simulado ID: {simulado_id}").pack()
        tk.Label(janela_relatorio, text=f"Tema: {tema}").pack()
        tk.Label(janela_relatorio, text=f"Nível de Dificuldade: {nivel_dificuldade}").pack()
        tk.Label(janela_relatorio, text=f"Nota: {nota}").pack()
        tk.Label(janela_relatorio, text=f"Data de realização: {data_realizacao}").pack()
        tk.Label(janela_relatorio, text="").pack()

# Interface Tkinter
# Janela para cadastro de aluno
def abrir_cadastro_aluno():
    janela_aluno = tk.Toplevel()
    janela_aluno.title("Cadastro de Aluno")

    tk.Label(janela_aluno, text="Nome único:").grid(row=0, column=0)
    entry_nome_unico_aluno = tk.Entry(janela_aluno)
    entry_nome_unico_aluno.grid(row=0, column=1)

    tk.Label(janela_aluno, text="Nome completo:").grid(row=1, column=0)
    entry_nome_aluno = tk.Entry(janela_aluno)
    entry_nome_aluno.grid(row=1, column=1)

    tk.Label(janela_aluno, text="Série:").grid(row=2, column=0)
    entry_serie_aluno = tk.Entry(janela_aluno)
    entry_serie_aluno.grid(row=2, column=1)

    tk.Label(janela_aluno, text="Grau de Ensino (Fundamental ou Médio):").grid(row=3, column=0)
    entry_grau_aluno = tk.Entry(janela_aluno)
    entry_grau_aluno.grid(row=3, column=1)

    tk.Label(janela_aluno, text="Email:").grid(row=4, column=0)
    entry_email_aluno = tk.Entry(janela_aluno)
    entry_email_aluno.grid(row=4, column=1)

    tk.Label(janela_aluno, text="Telefone:").grid(row=5, column=0)
    entry_tel_aluno = tk.Entry(janela_aluno)
    entry_tel_aluno.grid(row=5, column=1)

    btn_add_aluno = tk.Button(janela_aluno, text="Adicionar Aluno", command=lambda:add_aluno(entry_nome_unico_aluno, entry_nome_aluno, entry_serie_aluno, entry_grau_aluno, entry_email_aluno, entry_tel_aluno))
    btn_add_aluno.grid(row=6, columnspan=2, pady=5)

# Janela para cadastro de questões
def abrir_cadastro_questao():    
    janela_questao = tk.Toplevel()
    janela_questao.title("Cadastro de Questão")  

    tk.Label(janela_questao, text="Enunciado:").grid(row=0, column=0)
    entry_enunciado = tk.Entry(janela_questao)
    entry_enunciado.grid(row=0, column=1)

    tk.Label(janela_questao, text="Resposta Correta:").grid(row=1, column=0)
    entry_resposta_correta = tk.Entry(janela_questao)
    entry_resposta_correta.grid(row=1, column=1)

    tk.Label(janela_questao, text="Tema:").grid(row=2, column=0)
    entry_tema = tk.Entry(janela_questao)
    entry_tema.grid(row=2, column=1)

    tk.Label(janela_questao, text="Série:").grid(row=3, column=0)
    entry_serie = tk.Entry(janela_questao)
    entry_serie.grid(row=3, column=1)

    tk.Label(janela_questao, text="Grau de Ensino:").grid(row=4, column=0)
    entry_grau = tk.Entry(janela_questao)
    entry_grau.grid(row=4, column=1)

    tk.Label(janela_questao, text="Nível de Dificuldade:").grid(row=5, column=0)
    entry_nivel = tk.Entry(janela_questao)
    entry_nivel.grid(row=5, column=1)

    btn_add_questao = tk.Button(janela_questao, text="Adicionar Questão", command=lambda:add_questao(entry_enunciado,entry_resposta_correta,entry_tema,entry_serie,entry_grau,entry_nivel))
    btn_add_questao.grid(row=6, columnspan=2, pady=5)

# Janela para gerar simulado
def abrir_geracao_simulado():  
    janela_simulado = tk.Toplevel()
    janela_simulado.title("Gerar Simulado")  

    tk.Label(janela_simulado, text="Nome único do aluno:").grid(row=0, column=0)
    entry_nome_aluno = tk.Entry(janela_simulado)
    entry_nome_aluno.grid(row=0, column=1)

    tk.Label(janela_simulado, text="Tema:").grid(row=1, column=0)
    entry_tema = tk.Entry(janela_simulado)
    entry_tema.grid(row=1, column=1)

    tk.Label(janela_simulado, text="Nível de dificuldade:").grid(row=2, column=0)
    entry_nivel = tk.Entry(janela_simulado)
    entry_nivel.grid(row=2, column=1)

    tk.Label(janela_simulado, text="Número de questões:").grid(row=3, column=0)
    entry_num_questoes = tk.Entry(janela_simulado)
    entry_num_questoes.grid(row=3, column=1)

    btn_add_questao = tk.Button(janela_simulado, text="Gerar Simulado", command=lambda:gerar_e_salvar_simulado(entry_nome_aluno,entry_tema,entry_nivel,entry_num_questoes))
    btn_add_questao.grid(row=4, columnspan=2, pady=5)

# Janela para cadastrar e corrigir respostas do aluno no simulado
def abrir_cadastro_respostas():  
    janela_respostas = tk.Toplevel()
    janela_respostas.title("Cadastro de respostas do aluno")  

    tk.Label(janela_respostas, text="Nome único do aluno:").grid(row=0, column=0)
    entry_nome_aluno = tk.Entry(janela_respostas)
    entry_nome_aluno.grid(row=0, column=1)

    tk.Label(janela_respostas, text="Simulado ID:").grid(row=1, column=0)
    entry_simulado = tk.Entry(janela_respostas)
    entry_simulado.grid(row=1, column=1)

    tk.Label(janela_respostas, text="Data de Realização do Simulado:").grid(row=2, column=0)
    entry_data = tk.Entry(janela_respostas)
    entry_data.grid(row=2, column=1)

    btn_add_questao = tk.Button(janela_respostas, text="Cadastrar Respostas do Aluno", command=lambda:abrir_form_resposta(entry_nome_aluno,entry_simulado,entry_data))
    btn_add_questao.grid(row=3, columnspan=2, pady=5)

# Janela para gerar relatório de desempenho do aluno
def abrir_geracao_relatorio():  
    janela_respostas = tk.Toplevel()
    janela_respostas.title("Gerar Relatório de Desempenho do aluno")  

    tk.Label(janela_respostas, text="Nome único do aluno:").grid(row=0, column=0)
    entry_nome_aluno = tk.Entry(janela_respostas)
    entry_nome_aluno.grid(row=0, column=1)

    btn_add_questao = tk.Button(janela_respostas, text="Gerar Relatório", command=lambda:gerar_relatorio(entry_nome_aluno))
    btn_add_questao.grid(row=3, columnspan=2, pady=5)

# Janela Principal
root = tk.Tk()
root.title("Sistema Gerador de Simulados")
root.geometry("400x300")

# Botões na janela principal
btn_cadastrar_aluno = tk.Button(root, text="Cadastrar Aluno", command=abrir_cadastro_aluno)
btn_cadastrar_aluno.pack(pady=10)

btn_cadastrar_questao = tk.Button(root, text="Cadastrar Questão", command=abrir_cadastro_questao)
btn_cadastrar_questao.pack(pady=10)

btn_cadastrar_questao = tk.Button(root, text="Gerar Simulado", command=abrir_geracao_simulado)
btn_cadastrar_questao.pack(pady=10)

btn_cadastrar_questao = tk.Button(root, text="Cadastrar Respostas do Aluno e Corrigir Simulado", command=abrir_cadastro_respostas)
btn_cadastrar_questao.pack(pady=10)

btn_cadastrar_questao = tk.Button(root, text="Gerar Relatório de Desempenho do aluno", command=abrir_geracao_relatorio)
btn_cadastrar_questao.pack(pady=10)

root.mainloop()
