import sqlite3
import os
from tkinter import *
from tkinter import ttk

class Produto:
    def __init__(self, root):
        self.janela = root
        self.janela.title("App Gestor de Produtos")
        self.janela.resizable(1, 1)

        # Definição do banco de dados
        self.db = 'database/produtos.db'

        # Definindo o estilo para os textos
        self.font_16_bold = ('Calibri', 16, 'bold')
        self.font_13 = ('Calibri', 13)

        # Frame para adicionar um novo produto
        frame = LabelFrame(self.janela, text="Registar um novo Produto", font=self.font_16_bold)
        frame.grid(row=0, column=0, columnspan=3, pady=20)

        # Label Nome
        self.etiqueta_nome = Label(frame, text="Nome: ", font=self.font_13)
        self.etiqueta_nome.grid(row=1, column=0)
        self.nome = Entry(frame, font=self.font_13)
        self.nome.focus()
        self.nome.grid(row=1, column=1)

        # Label Preço
        self.etiqueta_preco = Label(frame, text="Preço: ", font=self.font_13)
        self.etiqueta_preco.grid(row=2, column=0)
        self.preco = Entry(frame, font=self.font_13)
        self.preco.grid(row=2, column=1)

        # Botão Adicionar Produto
        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri', 14, 'bold'))
        self.botao_adicionar = ttk.Button(frame, text="Guardar Produto", command=self.add_produto, style='my.TButton')
        self.botao_adicionar.grid(row=3, columnspan=2, sticky=W + E)

        # Mensagem informativa para o utilizador
        self.mensagem = Label(text='', fg='red', font=self.font_13)
        self.mensagem.grid(row=3, column=0, columnspan=2, sticky=W + E)

        # Tabela de Produtos
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=self.font_13)
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 13, 'bold'))
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        self.tabela = ttk.Treeview(height=20, columns=2, style="mystyle.Treeview")
        self.tabela.grid(row=4, column=0, columnspan=2)
        self.tabela.heading('#0', text='Nome', anchor=CENTER)
        self.tabela.heading('#1', text='Preço', anchor=CENTER)

        # Botões de Eliminar e Editar
        botão_eliminar = ttk.Button(text='ELIMINAR', command=self.del_produto, style='my.TButton')
        botão_eliminar.grid(row=5, column=0, sticky=W + E)
        botão_editar = ttk.Button(text='EDITAR', command=self.edit_produto, style='my.TButton')
        botão_editar.grid(row=5, column=1, sticky=W + E)

        # Define o ícone da janela
        icon_path = os.path.abspath("recursos/icon.ico")
        if os.path.exists(icon_path):
            self.janela.wm_iconbitmap(icon_path)
        else:
            print(f"⚠️ Arquivo do ícone não encontrado: {icon_path}")

        # Agora que a tabela foi criada, chamamos get_produtos()
        self.get_produtos()

    def db_consulta(self, consulta, parametros=()):
        """Executa consultas no banco de dados"""
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            resultado = cursor.execute(consulta, parametros)
            con.commit()
        return resultado

    def get_produtos(self):
        """Obtém e exibe os produtos na tabela"""
        # Limpar a tabela antes de inserir novos dados
        registos_tabela = self.tabela.get_children()
        for linha in registos_tabela:
            self.tabela.delete(linha)

        # Executar consulta SQL
        query = 'SELECT * FROM produto ORDER BY nome DESC'
        registos_db = self.db_consulta(query)

        # Garantir que os dados são recuperados corretamente
        registos = registos_db.fetchall()

        # Se não houver produtos
        if not registos:
            print("Nenhum produto encontrado na base de dados.")
            return

        # Exibir os dados na interface e console
        for linha in registos:
            print(linha)
            self.tabela.insert('', 'end', text=linha[1], values=(linha[2],))

    def validacao_nome(self):
        nome_introduzido_por_utilizador = self.nome.get()
        return len(nome_introduzido_por_utilizador) != 0

    def validacao_preco(self):
        preco_introduzido_por_utilizador = self.preco.get()
        return len(preco_introduzido_por_utilizador) != 0

    def add_produto(self):
        nome_valido = self.validacao_nome()
        preco_valido = self.validacao_preco()

        if nome_valido and preco_valido:
            query = 'INSERT INTO produto VALUES(NULL, ?, ?)'  # Consulta SQL (sem os dados)
            parametros = (self.nome.get(), self.preco.get())  # Parâmetros da consulta SQL
            self.db_consulta(query, parametros)
            print("Dados guardados")

            self.mensagem['text'] = 'Produto {} adicionado com êxito'.format(self.nome.get())
            # Atualiza a mensagem para o usuário

            self.nome.delete(0, END)  # Apagar o campo nome do formulário
            self.preco.delete(0, END)  # Apagar o campo preço do formulário

        elif not nome_valido and not preco_valido:
            print("O nome e o preço são obrigatórios")
            self.mensagem['text'] = 'O nome e o preço são obrigatórios'

        elif not preco_valido:
            print("O preço é obrigatório")
            self.mensagem['text'] = 'O preço é obrigatório'

        elif not nome_valido:
            print("O nome é obrigatório")
            self.mensagem['text'] = 'O nome é obrigatório'

        # Atualiza a lista de produtos após a inserção
        self.get_produtos()

    def del_produto(self):
        # Limpa qualquer mensagem anterior
        self.mensagem['text'] = ''

        # Verifica se algum item foi selecionado
        try:
            nome = self.tabela.item(self.tabela.selection())['text']
            if not nome:  # Se `nome` estiver vazio, lançar exceção manualmente
                raise IndexError
        except IndexError:
            self.mensagem['text'] = 'Por favor, selecione um produto'
            return  # Interrompe a execução se nada foi selecionado

        # Consulta SQL para deletar o produto
        query = 'DELETE FROM produto WHERE nome = ?'
        self.db_consulta(query, (nome,))  # Executa a consulta

        # Exibe mensagem de sucesso
        self.mensagem['text'] = f'Produto {nome} eliminado com êxito'

        # Atualiza a tabela para refletir a remoção
        self.get_produtos()

    def edit_produto(self):
        self.mensagem['text'] = ''  # Mensagem inicialmente vazia

        try:
            self.tabela.item(self.tabela.selection())['text'][0]
        except IndexError:
            self.mensagem['text'] = 'Por favor, selecione um produto'
            return  # Interrompe a execução se nenhum item foi selecionado

        nome = self.tabela.item(self.tabela.selection())['text']
        old_preco = self.tabela.item(self.tabela.selection())['values'][0]  # O preço está dentro de uma lista

        # Janela nova (editar produto)
        self.janela_editar = Toplevel()  # Criar uma janela à frente da principal
        self.janela_editar.title = "Editar Produto"  # Título da janela
        self.janela_editar.resizable(1, 1)  # Ativar o redimensionamento da janela. Para desativá-la: (0, 0)
        self.janela_editar.wm_iconbitmap('recursos/icon.ico')  # Ícone da janela
        título = Label(self.janela_editar, text='Edição de Produtos', font=('Calibri', 50, 'bold'))
        título.grid(column=0, row=0)

        # Criação do recipiente Frame da janela de Editar Produto
        frame_ep = LabelFrame(self.janela_editar, text="Editar o seguinte Produto", font=self.font_16_bold)
        frame_ep.grid(row=1, column=0, columnspan=20, pady=20)

        # Label Nome antigo
        self.etiqueta_nome_antigo = Label(frame_ep, text="Nome antigo: ", font=self.font_13)
        self.etiqueta_nome_antigo.grid(row=2, column=0)

        # Entry Nome antigo (texto que não se poderá modificar)
        self.input_nome_antigo = Entry(frame_ep, textvariable=StringVar(self.janela_editar, value=nome), state='readonly', font=self.font_13)
        self.input_nome_antigo.grid(row=2, column=1)

        # Label Nome novo
        self.etiqueta_nome_novo = Label(frame_ep, text="Nome novo: ", font=self.font_13)
        self.etiqueta_nome_novo.grid(row=3, column=0)

        # Entry Nome novo (texto que se poderá modificar)
        self.input_nome_novo = Entry(frame_ep, font=self.font_13)
        self.input_nome_novo.grid(row=3, column=1)
        self.input_nome_novo.focus()

        # Label Preço antigo
        self.etiqueta_preco_antigo = Label(frame_ep, text="Preço antigo: ", font=self.font_13)
        self.etiqueta_preco_antigo.grid(row=4, column=0)

        # Entry Preço antigo (texto que não se poderá modificar)
        self.input_preco_antigo = Entry(frame_ep, textvariable=StringVar(self.janela_editar, value=old_preco), state='readonly', font=self.font_13)
        self.input_preco_antigo.grid(row=4, column=1)

        # Label Preço novo
        self.etiqueta_preco_novo = Label(frame_ep, text="Preço novo: ", font=self.font_13)
        self.etiqueta_preco_novo.grid(row=5, column=0)

        # Entry Preço novo (texto que se poderá modificar)
        self.input_preco_novo = Entry(frame_ep, font=self.font_13)
        self.input_preco_novo.grid(row=5, column=1)

        # Botão Atualizar Produto
        self.botao_atualizar = ttk.Button(frame_ep, text="Atualizar Produto", command=lambda: self.atualizar_produtos(
            self.input_nome_novo.get(),
            self.input_nome_antigo.get(),
            self.input_preco_novo.get()
        ), style='my.TButton')
        self.botao_atualizar.grid(row=6, columnspan=2, sticky=W + E)

    def atualizar_produtos(self, nome_novo, nome_antigo, preco_novo):
        # Validação dos campos de edição
        if nome_novo or preco_novo:  # Verifica se pelo menos um valor foi alterado
            # Se o nome novo estiver vazio, mantém o nome antigo
            if not nome_novo:
                nome_novo = nome_antigo

            # Se o preço novo estiver vazio, mantém o preço antigo
            if not preco_novo:
                preco_novo = self.input_preco_antigo.get()

            # Atualiza no banco de dados apenas o que foi alterado
            query = 'UPDATE produto SET nome = ?, "preço" = ? WHERE nome = ?'
            self.db_consulta(query, (nome_novo, preco_novo, nome_antigo))
            print("Produto atualizado")

            self.mensagem['text'] = f"Produto {nome_antigo} atualizado com sucesso"
            self.get_produtos()  # Atualiza a tabela com os novos dados

            self.janela_editar.destroy()  # Fecha a janela de edição
        else:
            self.mensagem['text'] = 'Nome ou preço precisam ser informados!'


if __name__ == "__main__":
    root = Tk()
    Produto(root)
    root.mainloop()
