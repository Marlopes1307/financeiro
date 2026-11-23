import sqlite3
import hashlib
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Define a pasta base onde o .exe ou .py está rodando
if getattr(sys, 'frozen', False):
    PASTA_BASE = os.path.dirname(sys.executable)
else:
    PASTA_BASE = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(PASTA_BASE, "financas_local.db")

CATEGORIAS_PADRAO = [
    "Salário / Renda", "Renda Extra", "Moradia", "Alimentação",
    "Transporte", "Contas Fixas", "Saúde", "Lazer", "Educação", "Investimentos"
]
PAGAMENTOS_PADRAO = ["PIX", "Cartão Crédito", "Cartão Débito", "Boleto", "Dinheiro"]

# =========================================================================
# BANCO DE DADOS LOCAL (SQLITE)
# =========================================================================
def hash_senha(senha):
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def inicializar_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            tipo TEXT NOT NULL,
            pagamento TEXT NOT NULL,
            status TEXT NOT NULL,
            valor REAL NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# =========================================================================
# JANELA DE LOGIN / CADASTRO DE SENHA
# =========================================================================
class JanelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Acesso Seguro - Controle Financeiro")
        self.geometry("380x260")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.autenticado = False
        inicializar_banco()
        self.senha_salva = self.buscar_senha()

        titulo = "Digite sua Senha" if self.senha_salva else "Crie uma Senha de Acesso"
        ctk.CTkLabel(self, text=titulo, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30, 15))

        self.ent_senha = ctk.CTkEntry(self, width=240, show="*", placeholder_text="Senha...")
        self.ent_senha.pack(pady=10)
        self.ent_senha.bind("<Return>", lambda e: self.validar())

        btn_texto = "Entrar" if self.senha_salva else "Salvar e Entrar"
        ctk.CTkButton(self, text=btn_texto, width=240, command=self.validar).pack(pady=15)

    def buscar_senha(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM config WHERE chave = 'senha_acesso'")
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else None

    def validar(self):
        senha = self.ent_senha.get().strip()
        if not senha:
            messagebox.showwarning("Aviso", "Digite uma senha.")
            return

        if self.senha_salva is None:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO config (chave, valor) VALUES ('senha_acesso', ?)", (hash_senha(senha),))
            conn.commit()
            conn.close()
            self.autenticado = True
            self.destroy()
        else:
            if hash_senha(senha) == self.senha_salva:
                self.autenticado = True
                self.destroy()
            else:
                messagebox.showerror("Erro", "Senha incorreta!")
                self.ent_senha.delete(0, "end")

# =========================================================================
# JANELA MODAL DE EDIÇÃO DE LANÇAMENTO
# =========================================================================
class JanelaEdicao(ctk.CTkToplevel):
    def __init__(self, parent, dados_lancamento, callback_atualizar):
        super().__init__(parent)
        self.title("Editar Lançamento")
        self.geometry("420x460")
        self.resizable(False, False)
        self.grab_set()  # Mantém o foco nesta janela até salvar ou cancelar

        self.id_lanc = dados_lancamento[0]
        self.callback_atualizar = callback_atualizar

        ctk.CTkLabel(self, text=f"Alterar Lançamento #{self.id_lanc}", font=ctk.CTkFont(size=17, weight="bold")).pack(pady=(15, 10))

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=25)

        # Data
        ctk.CTkLabel(frame, text="Data (DD/MM/AAAA):").grid(row=0, column=0, sticky="w", pady=6)
        self.ent_data = ctk.CTkEntry(frame, width=210)
        self.ent_data.insert(0, dados_lancamento[1])
        self.ent_data.grid(row=0, column=1, pady=6)

        # Descrição
        ctk.CTkLabel(frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=6)
        self.ent_desc = ctk.CTkEntry(frame, width=210)
        self.ent_desc.insert(0, dados_lancamento[2])
        self.ent_desc.grid(row=1, column=1, pady=6)

        # Categoria
        ctk.CTkLabel(frame, text="Categoria:").grid(row=2, column=0, sticky="w", pady=6)
        self.cb_cat = ctk.CTkComboBox(frame, values=CATEGORIAS_PADRAO, width=210)
        self.cb_cat.set(dados_lancamento[3])
        self.cb_cat.grid(row=2, column=1, pady=6)

        # Tipo
        ctk.CTkLabel(frame, text="Tipo:").grid(row=3, column=0, sticky="w", pady=6)
        self.cb_tipo = ctk.CTkComboBox(frame, values=["Despesa", "Receita"], width=210)
        self.cb_tipo.set(dados_lancamento[4])
        self.cb_tipo.grid(row=3, column=1, pady=6)

        # Pagamento
        ctk.CTkLabel(frame, text="Pagamento:").grid(row=4, column=0, sticky="w", pady=6)
        self.cb_pgto = ctk.CTkComboBox(frame, values=PAGAMENTOS_PADRAO, width=210)
        self.cb_pgto.set(dados_lancamento[5])
        self.cb_pgto.grid(row=4, column=1, pady=6)

        # Status (Destaque para Pendente / Pago)
        ctk.CTkLabel(frame, text="Status:", font=ctk.CTkFont(weight="bold")).grid(row=5, column=0, sticky="w", pady=6)
        self.cb_status = ctk.CTkComboBox(frame, values=["Pago", "Pendente"], width=210)
        self.cb_status.set(dados_lancamento[6])
        self.cb_status.grid(row=5, column=1, pady=6)

        # Valor
        ctk.CTkLabel(frame, text="Valor (R$):").grid(row=6, column=0, sticky="w", pady=6)
        self.ent_valor = ctk.CTkEntry(frame, width=210)
        valor_limpo = str(dados_lancamento[7]).replace("R$", "").replace(".", "").replace(",", ".").strip()
        self.ent_valor.insert(0, valor_limpo)
        self.ent_valor.grid(row=6, column=1, pady=6)

        # Botões Salvar / Cancelar
        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(pady=15)

        ctk.CTkButton(
            frame_btns, text="Salvar Alterações", fg_color="#2EA043", hover_color="#238636",
            width=160, font=ctk.CTkFont(weight="bold"), command=self.salvar_edicao
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            frame_btns, text="Cancelar", fg_color="#484F58", hover_color="#30363D",
            width=120, command=self.destroy
        ).pack(side="left", padx=8)

    def salvar_edicao(self):
        data_txt = self.ent_data.get().strip()
        desc = self.ent_desc.get().strip()
        cat = self.cb_cat.get()
        tipo = self.cb_tipo.get()
        pgto = self.cb_pgto.get()
        status = self.cb_status.get()
        valor_txt = self.ent_valor.get().strip().replace(",", ".")

        if not desc or not valor_txt:
            messagebox.showwarning("Atenção", "Preencha a descrição e o valor.", parent=self)
            return

        try:
            datetime.strptime(data_txt, "%d/%m/%Y")
            valor = float(valor_txt)
        except ValueError:
            messagebox.showerror("Erro", "Data inválida (use DD/MM/AAAA) ou valor incorreto.", parent=self)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE lancamentos
            SET data = ?, descricao = ?, categoria = ?, tipo = ?, pagamento = ?, status = ?, valor = ?
            WHERE id = ?
        """, (data_txt, desc, cat, tipo, pgto, status, valor, self.id_lanc))
        conn.commit()
        conn.close()

        self.callback_atualizar()
        self.destroy()

# =========================================================================
# APLICATIVO PRINCIPAL
# =========================================================================
class AppFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Controle Financeiro Pro - Local")
        self.geometry("1140x710")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.criar_widgets()
        self.atualizar_dados()

    def criar_widgets(self):
        # --- TOPO: CARDS DE RESUMO (KPIs) ---
        self.frame_kpi = ctk.CTkFrame(self)
        self.frame_kpi.pack(fill="x", padx=20, pady=(15, 5))

        self.lbl_receita = self.criar_card_kpi(self.frame_kpi, "Receitas (Pago)", "R$ 0,00", "#2EA043", 0)
        self.lbl_despesa = self.criar_card_kpi(self.frame_kpi, "Despesas (Pago)", "R$ 0,00", "#DA3633", 1)
        self.lbl_saldo = self.criar_card_kpi(self.frame_kpi, "Saldo em Caixa", "R$ 0,00", "#1F6FEB", 2)
        self.lbl_pendente = self.criar_card_kpi(self.frame_kpi, "Contas Pendentes", "R$ 0,00", "#D29922", 3)

        # --- BARRA DE FILTRO E EXPORTAÇÃO ---
        self.frame_barra = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_barra.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(self.frame_barra, text="Mês/Ano (MM/AAAA):").pack(side="left", padx=(0, 6))
        self.ent_filtro_mes = ctk.CTkEntry(self.frame_barra, width=100, placeholder_text="Ex: 11/2026")
        self.ent_filtro_mes.pack(side="left", padx=(0, 6))
        ctk.CTkButton(self.frame_barra, text="Filtrar", width=80, command=self.atualizar_dados).pack(side="left", padx=(0, 6))
        ctk.CTkButton(self.frame_barra, text="Limpar Filtro", width=100, fg_color="#484F58", command=self.limpar_filtro).pack(side="left")
        ctk.CTkButton(
            self.frame_barra, text="Exportar Excel (.xlsx)", fg_color="#1F6FEB", width=160,
            command=self.exportar_excel
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            self.frame_barra, text="Importar CSV", fg_color="#6E40C9", width=130,
            command=self.importar_csv
        ).pack(side="right")

        # --- SISTEMA DE ABAS ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.tab_lanc = self.tabview.add("Lançamentos")
        self.tab_graf = self.tabview.add("Gráficos e Análise")
        self.montar_aba_lancamentos()
        self.montar_aba_graficos()

    def montar_aba_lancamentos(self):
        # Formulário de cadastro
        frame_form = ctk.CTkFrame(self.tab_lanc)
        frame_form.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(frame_form, text="Data:").grid(row=0, column=0, padx=8, pady=(8, 0), sticky="w")
        self.ent_data = ctk.CTkEntry(frame_form, width=110)
        self.ent_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ent_data.grid(row=1, column=0, padx=8, pady=(0, 10))
        ctk.CTkLabel(frame_form, text="Descrição:").grid(row=0, column=1, padx=8, pady=(8, 0), sticky="w")
        self.ent_desc = ctk.CTkEntry(frame_form, width=230, placeholder_text="Ex: Mercado, Salário...")
        self.ent_desc.grid(row=1, column=1, padx=8, pady=(0, 10))
        ctk.CTkLabel(frame_form, text="Categoria:").grid(row=0, column=2, padx=8, pady=(8, 0), sticky="w")
        self.cb_cat = ctk.CTkComboBox(frame_form, values=CATEGORIAS_PADRAO, width=160)
        self.cb_cat.grid(row=1, column=2, padx=8, pady=(0, 10))
        ctk.CTkLabel(frame_form, text="Tipo:").grid(row=0, column=3, padx=8, pady=(8, 0), sticky="w")
        self.cb_tipo = ctk.CTkComboBox(frame_form, values=["Despesa", "Receita"], width=110)
        self.cb_tipo.grid(row=1, column=3, padx=8, pady=(0, 10))
        ctk.CTkLabel(frame_form, text="Pagamento:").grid(row=0, column=4, padx=8, pady=(8, 0), sticky="w")
        self.cb_pgto = ctk.CTkComboBox(frame_form, values=PAGAMENTOS_PADRAO, width=130)
        self.cb_pgto.grid(row=1, column=4, padx=8, pady=(0, 10))
        ctk.CTkLabel(frame_form, text="Status:").grid(row=0, column=5, padx=8, pady=(8, 0), sticky="w")
        self.cb_status = ctk.CTkComboBox(frame_form, values=["Pago", "Pendente"], width=105)
        self.cb_status.grid(row=1, column=5, padx=8, pady=(0, 10))

        # Linha 2 de botões e valor
        ctk.CTkLabel(frame_form, text="Valor (R$):").grid(row=2, column=0, padx=8, pady=(0, 0), sticky="w")
        self.ent_valor = ctk.CTkEntry(frame_form, width=110, placeholder_text="0,00")
        self.ent_valor.grid(row=3, column=0, padx=8, pady=(0, 10))
        ctk.CTkButton(
            frame_form, text="+ Adicionar Lançamento", fg_color="#2EA043", hover_color="#238636",
            width=230, font=ctk.CTkFont(weight="bold"), command=self.adicionar_lancamento
        ).grid(row=3, column=1, padx=8, pady=(0, 10))
        ctk.CTkButton(
            frame_form, text="Editar Selecionado", fg_color="#1F6FEB", hover_color="#1158C7",
            width=160, font=ctk.CTkFont(weight="bold"), command=self.abrir_edicao
        ).grid(row=3, column=2, padx=8, pady=(0, 10))
        ctk.CTkButton(
            frame_form, text="Alternar Pago / Pendente", fg_color="#D29922", hover_color="#B08019",
            text_color="black", width=180, font=ctk.CTkFont(weight="bold"), command=self.alternar_status
        ).grid(row=3, column=3, columnspan=2, padx=8, pady=(0, 10))
        ctk.CTkButton(
            frame_form, text="Excluir", fg_color="#DA3633", hover_color="#B62324",
            width=105, command=self.excluir_selecionado
        ).grid(row=3, column=5, padx=8, pady=(0, 10))

        # Tabela
        frame_tab = ctk.CTkFrame(self.tab_lanc)
        frame_tab.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2B2B2B", foreground="white", fieldbackground="#2B2B2B", rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background="#1F4E78", foreground="white", font=("Calibri", 10, "bold"))
        style.map("Treeview", background=[("selected", "#1F6FEB")])
        colunas = ("id", "data", "descricao", "categoria", "tipo", "pagamento", "status", "valor")
        self.tree = ttk.Treeview(frame_tab, columns=colunas, show="headings")
        titulos = ["ID", "Data", "Descrição", "Categoria", "Tipo", "Pagamento", "Status", "Valor"]
        larguras = [50, 100, 270, 150, 90, 130, 100, 120]
        for col, titulo, larg in zip(colunas, titulos, larguras):
            self.tree.heading(col, text=titulo)
            self.tree.column(col, width=larg, anchor="center" if col != "descricao" else "w")

        # Duplo clique na linha abre a tela de edição
        self.tree.bind("<Double-1>", lambda e: self.abrir_edicao())
        scrollbar = ttk.Scrollbar(frame_tab, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        ctk.CTkLabel(
            self.tab_lanc, text="Dica: Dê um duplo clique em qualquer lançamento acima para editar ou mudar o status.",
            font=ctk.CTkFont(size=11, slant="italic"), text_color="#8B949E"
        ).pack(anchor="w", padx=12, pady=(0, 5))

    def montar_aba_graficos(self):
        self.frame_canvas_graf = ctk.CTkFrame(self.tab_graf)
        self.frame_canvas_graf.pack(fill="both", expand=True, padx=10, pady=10)

    def atualizar_graficos(self, rows):
        for widget in self.frame_canvas_graf.winfo_children():
            widget.destroy()

        gastos_cat = {}
        receita_total = 0.0
        despesa_total = 0.0
        for r in rows:
            _, _, _, cat, tipo, _, status, val = r
            if tipo == "Despesa":
                gastos_cat[cat] = gastos_cat.get(cat, 0.0) + val
            if status == "Pago":
                if tipo == "Despesa":
                    despesa_total += val
                elif tipo == "Receita":
                    receita_total += val

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), facecolor="#2B2B2B")
        fig.subplots_adjust(wspace=0.35)
        ax1.set_facecolor("#2B2B2B")
        if gastos_cat:
            cats = list(gastos_cat.keys())
            vals = list(gastos_cat.values())
            ax1.barh(cats, vals, color="#1F6FEB")
            ax1.set_title("Despesas por Categoria (R$)", color="white", fontsize=11, fontweight="bold")
            ax1.tick_params(colors="white", labelsize=9)
        else:
            ax1.text(0.5, 0.5, "Sem despesas no período", color="white", ha="center", va="center")
            ax1.axis("off")

        ax2.set_facecolor("#2B2B2B")
        ax2.bar(["Receitas (Pago)", "Despesas (Pago)"], [receita_total, despesa_total], color=["#2EA043", "#DA3633"], width=0.5)
        ax2.set_title("Balanço Realizado (R$)", color="white", fontsize=11, fontweight="bold")
        ax2.tick_params(colors="white", labelsize=9)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_canvas_graf)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def criar_card_kpi(self, parent, titulo, valor_inicial, cor_borda, coluna):
        card = ctk.CTkFrame(parent, border_width=2, border_color=cor_borda)
        card.grid(row=0, column=coluna, padx=8, pady=8, sticky="nsew")
        parent.grid_columnconfigure(coluna, weight=1)
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=12)).pack(pady=(6, 0))
        lbl_val = ctk.CTkLabel(card, text=valor_inicial, font=ctk.CTkFont(size=19, weight="bold"))
        lbl_val.pack(pady=(2, 8))
        return lbl_val

    def formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def adicionar_lancamento(self):
        data_txt = self.ent_data.get().strip()
        desc = self.ent_desc.get().strip()
        cat = self.cb_cat.get()
        tipo = self.cb_tipo.get()
        pgto = self.cb_pgto.get()
        status = self.cb_status.get()
        valor_txt = self.ent_valor.get().strip().replace(",", ".")

        if not desc or not valor_txt:
            messagebox.showwarning("Atenção", "Preencha a descrição e o valor.")
            return

        try:
            datetime.strptime(data_txt, "%d/%m/%Y")
            valor = float(valor_txt)
        except ValueError:
            messagebox.showerror("Erro", "Data inválida (use DD/MM/AAAA) ou valor numérico incorreto.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO lancamentos (data, descricao, categoria, tipo, pagamento, status, valor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (data_txt, desc, cat, tipo, pgto, status, valor),
        )
        conn.commit()
        conn.close()
        self.ent_desc.delete(0, "end")
        self.ent_valor.delete(0, "end")
        self.atualizar_dados()

    def abrir_edicao(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showinfo("Aviso", "Selecione um lançamento na tabela para editar.")
            return
        valores = self.tree.item(selecionado[0])["values"]
        JanelaEdicao(self, valores, self.atualizar_dados)

    def alternar_status(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showinfo("Aviso", "Selecione um lançamento na tabela para mudar o status.")
            return
        valores = self.tree.item(selecionado[0])["values"]
        item_id = valores[0]
        status_atual = valores[6]
        novo_status = "Pago" if status_atual == "Pendente" else "Pendente"
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE lancamentos SET status = ? WHERE id = ?", (novo_status, item_id))
        conn.commit()
        conn.close()
        self.atualizar_dados()

    def excluir_selecionado(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showinfo("Aviso", "Selecione uma linha na tabela para excluir.")
            return
        item_id = self.tree.item(selecionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este lançamento?"):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM lancamentos WHERE id = ?", (item_id,))
            conn.commit()
            conn.close()
            self.atualizar_dados()

    def exportar_excel(self):
        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Planilha Excel", "*.xlsx")],
            initialfile="Relatorio_Financeiro.xlsx",
        )
        if not caminho:
            return

        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT data AS Data, descricao AS Descrição, categoria AS Categoria, tipo AS Tipo, pagamento AS Pagamento, status AS Status, valor AS Valor FROM lancamentos",
            conn,
        )
        conn.close()
        df.to_excel(caminho, index=False)
        messagebox.showinfo("Sucesso", f"Relatório exportado para:\n{caminho}")

    def importar_csv(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
        if not caminho:
            return
        try:
            df = pd.read_csv(caminho)
            df.columns = [c.lower().strip() for c in df.columns]
            col_data = next(c for c in df.columns if 'data' in c or 'date' in c)
            col_desc = next(c for c in df.columns if 'desc' in c or 'title' in c or 'hist' in c)
            col_val = next(c for c in df.columns if 'val' in c or 'amount' in c)

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            importados = 0
            for _, row in df.iterrows():
                data_raw = str(row[col_data]).split(" ")[0]
                try:
                    data_fmt = datetime.strptime(data_raw, "%Y-%m-%d").strftime("%d/%m/%Y")
                except ValueError:
                    data_fmt = data_raw
                val_num = float(row[col_val])
                tipo = "Receita" if val_num > 0 else "Despesa"
                cursor.execute(
                    """
                    INSERT INTO lancamentos (data, descricao, categoria, tipo, pagamento, status, valor)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (data_fmt, str(row[col_desc]).strip(), "Outros", tipo, "PIX", "Pago", abs(val_num)),
                )
                importados += 1
            conn.commit()
            conn.close()
            self.atualizar_dados()
            messagebox.showinfo("Importação Concluída", f"{importados} lançamentos importados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro na Importação", f"Não foi possível ler o CSV:\n{e}")

    def limpar_filtro(self):
        self.ent_filtro_mes.delete(0, "end")
        self.atualizar_dados()

    def atualizar_dados(self):
        if hasattr(self, "tree"):
            for item in self.tree.get_children():
                self.tree.delete(item)

        filtro = self.ent_filtro_mes.get().strip() if hasattr(self, "ent_filtro_mes") else ""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if filtro:
            cursor.execute("SELECT * FROM lancamentos WHERE data LIKE ? ORDER BY id DESC", (f"%{filtro}",))
        else:
            cursor.execute("SELECT * FROM lancamentos ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        receitas = 0.0
        despesas = 0.0
        pendentes = 0.0
        for r in rows:
            id_lanc, data, desc, cat, tipo, pgto, status, val = r
            if tipo == "Receita" and status == "Pago":
                receitas += val
            elif tipo == "Despesa" and status == "Pago":
                despesas += val
            elif tipo == "Despesa" and status == "Pendente":
                pendentes += val

            if hasattr(self, "tree"):
                self.tree.insert("", "end", values=(
                    id_lanc, data, desc, cat, tipo, pgto, status, self.formatar_moeda(val)
                ))

        if hasattr(self, "lbl_receita"):
            self.lbl_receita.configure(text=self.formatar_moeda(receitas))
            self.lbl_despesa.configure(text=self.formatar_moeda(despesas))
            self.lbl_saldo.configure(text=self.formatar_moeda(receitas - despesas))
            self.lbl_pendente.configure(text=self.formatar_moeda(pendentes))
        self.atualizar_graficos(rows)


if __name__ == "__main__":
    login = JanelaLogin()
    login.mainloop()
    if login.autenticado:
        app = AppFinanceiro()
        app.mainloop()