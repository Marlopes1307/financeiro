import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.chart import BarChart, Reference
from datetime import date

def criar_planilha_pro():
    wb = openpyxl.Workbook()    
    ws_dash = wb.active
    ws_dash.title = "Dashboard"
    ws_lanc = wb.create_sheet(title="Lançamentos")
    ws_config = wb.create_sheet(title="Categorias e Metas")

    # Estilos
    cor_header = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    cor_filtro = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    cor_sub = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    fonte_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    fonte_titulo = Font(name="Calibri", size=14, bold=True, color="1F4E78")
    fonte_negrito = Font(name="Calibri", size=11, bold=True)
    borda_fina = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    formato_moeda = 'R$ #,##0.00'
    formato_data = 'DD/MM/YYYY'

    # =========================================================================
    # ABA 3: CATEGORIAS, METAS E LISTAS AUXILIARES
    # =========================================================================
    ws_config.append(["Categoria", "Tipo", "Orçamento Mensal", "", "Formas de Pagamento", "Status", "Meses"])
    
    dados_categorias = [
        ["Salário / Renda Principal", "Receita", 5000.00],
        ["Renda Extra / Dividendos", "Receita", 500.00],
        ["Moradia (Aluguel/Condomínio)", "Despesa", 1500.00],
        ["Alimentação (Mercado/Restaurante)", "Despesa", 1000.00],
        ["Transporte / Combustível", "Despesa", 500.00],
        ["Contas Fixas (Luz/Água/Internet)", "Despesa", 400.00],
        ["Saúde e Farmácia", "Despesa", 300.00],
        ["Lazer e Assinaturas", "Despesa", 400.00],
        ["Educação", "Despesa", 300.00],
        ["Investimentos / Reserva", "Despesa", 1100.00]
    ]

    formas_pgto = ["PIX / Transferência", "Cartão de Crédito", "Cartão de Débito", "Boleto", "Débito Automático", "Dinheiro"]
    status_lista = ["Pago", "Pendente"]
    meses_lista = ["01/2026", "02/2026", "03/2026", "04/2026", "05/2026", "06/2026", 
                   "07/2026", "08/2026", "09/2026", "10/2026", "11/2026", "12/2026"]

    max_linhas_cfg = max(len(dados_categorias), len(meses_lista))
    for i in range(max_linhas_cfg):
        row_idx = i + 2
        if i < len(dados_categorias):
            ws_config.cell(row=row_idx, column=1, value=dados_categorias[i][0])
            ws_config.cell(row=row_idx, column=2, value=dados_categorias[i][1])
            c_meta = ws_config.cell(row=row_idx, column=3, value=dados_categorias[i][2])
            c_meta.number_format = formato_moeda
        if i < len(formas_pgto):
            ws_config.cell(row=row_idx, column=5, value=formas_pgto[i])
        if i < len(status_lista):
            ws_config.cell(row=row_idx, column=6, value=status_lista[i])
        if i < len(meses_lista):
            ws_config.cell(row=row_idx, column=7, value=meses_lista[i])

    for col in range(1, 8):
        if col == 4:
            continue
        cell = ws_config.cell(row=1, column=col)
        cell.fill = cor_header
        cell.font = fonte_header
        cell.alignment = Alignment(horizontal="center")

    # =========================================================================
    # ABA 2: LANÇAMENTOS (Com Validação de Dados e Coluna Mês/Ano)
    # =========================================================================
    headers_lanc = ["Data", "Mês/Ano", "Descrição", "Categoria", "Tipo", "Forma de Pagamento", "Status", "Valor"]
    ws_lanc.append(headers_lanc)

    for col in range(1, 9):
        cell = ws_lanc.cell(row=1, column=col)
        cell.fill = cor_header
        cell.font = fonte_header
        cell.alignment = Alignment(horizontal="center")

    # Validações de dados (Listas suspensas até a linha 1000)
    dv_cat = DataValidation(type="list", formula1="='Categorias e Metas'!$A$2:$A$11", allow_blank=True)
    dv_pgto = DataValidation(type="list", formula1="='Categorias e Metas'!$E$2:$E$7", allow_blank=True)
    dv_status = DataValidation(type="list", formula1="='Categorias e Metas'!$F$2:$F$3", allow_blank=True)

    ws_lanc.add_data_validation(dv_cat)
    ws_lanc.add_data_validation(dv_pgto)
    ws_lanc.add_data_validation(dv_status)

    dv_cat.add("D2:D1000")
    dv_pgto.add("F2:F1000")
    dv_status.add("G2:G1000")

    # Pré-configurando fórmulas automáticas nas linhas 2 a 500
    for r in range(2, 501):
        ws_lanc.cell(row=r, column=2, value=f'=IF(A{r}="","",TEXT(A{r},"mm/yyyy"))')
        ws_lanc.cell(row=r, column=5, value=f'=IF(D{r}="","",IFERROR(VLOOKUP(D{r},\'Categorias e Metas\'!$A$2:$B$11,2,FALSE),""))')
        
        ws_lanc.cell(row=r, column=1).number_format = formato_data ='DD/MM/YYYY'
        ws_lanc.cell(row=r, column=1).alignment = Alignment(horizontal="center")
        ws_lanc.cell(row=r, column=2).alignment = Alignment(horizontal="center")
        ws_lanc.cell(row=r, column=8).number_format = formato_moeda = "R$#,##0.00"

    # Inserindo 3 exemplos iniciais
    exemplos = [
        [date(2026, 11, 5), "Salário Mensal", "Salário / Renda Principal", "PIX / Transferência", "Pago", 5000.00],
        [date(2026, 11, 6), "Aluguel Apartamento", "Moradia (Aluguel/Condomínio)", "Boleto", "Pago", 1450.00],
        [date(2026, 11, 8), "Supermercado", "Alimentação (Mercado/Restaurante)", "Cartão de Crédito", "Pago", 420.50],
    ]
    for idx, ex in enumerate(exemplos, start=2):
        ws_lanc.cell(row=idx, column=1, value=ex[0])
        ws_lanc.cell(row=idx, column=3, value=ex[1])
        ws_lanc.cell(row=idx, column=4, value=ex[2])
        ws_lanc.cell(row=idx, column=6, value=ex[3])
        ws_lanc.cell(row=idx, column=7, value=ex[4])
        ws_lanc.cell(row=idx, column=8, value=ex[5])

    # =========================================================================
    # ABA 1: DASHBOARD COM FILTRO DE MÊS/ANO
    # =========================================================================
    ws_dash["B2"] = "CONTROLE FINANCEIRO PESSOAL - DASHBOARD"
    ws_dash["B2"].font = fonte_titulo

    ws_dash["F2"] = "SELECIONE O MÊS:"
    ws_dash["F2"].font = fonte_negrito
    ws_dash["F2"].alignment = Alignment(horizontal="right")

    ws_dash["G2"] = "11/2026"
    ws_dash["G2"].fill = cor_filtro
    ws_dash["G2"].font = Font(name="Calibri", size=12, bold=True)
    ws_dash["G2"].alignment = Alignment(horizontal="center")
    ws_dash["G2"].border = borda_fina

    dv_mes = DataValidation(type="list", formula1="='Categorias e Metas'!$G$2:$G$13", allow_blank=False)
    ws_dash.add_data_validation(dv_mes)
    dv_mes.add("G2")

    kpis = [
        ("B4", "Receitas do Mês (Pago)", "B5", '=SUMIFS(Lançamentos!H:H, Lançamentos!E:E, "Receita", Lançamentos!G:G, "Pago", Lançamentos!B:B, $G$2)'),
        ("D4", "Despesas do Mês (Pago)", "D5", '=SUMIFS(Lançamentos!H:H, Lançamentos!E:E, "Despesa", Lançamentos!G:G, "Pago", Lançamentos!B:B, $G$2)'),
        ("F4", "Saldo do Mês", "F5", '=B5-D5'),
        ("H4", "Contas Pendentes", "H5", '=SUMIFS(Lançamentos!H:H, Lançamentos!E:E, "Despesa", Lançamentos!G:G, "Pendente", Lançamentos!B:B, $G$2)')
    ]

    for title_cell, title_text, val_cell, formula in kpis:
        ws_dash[title_cell] = title_text
        ws_dash[title_cell].fill = cor_header
        ws_dash[title_cell].font = fonte_header
        ws_dash[title_cell].alignment = Alignment(horizontal="center")
        
        ws_dash[val_cell] = formula
        ws_dash[val_cell].font = Font(name="Calibri", size=14, bold=True)
        ws_dash[val_cell].number_format = formato_moeda
        ws_dash[val_cell].alignment = Alignment(horizontal="center")
        ws_dash[val_cell].border = borda_fina

    ws_dash["B8"] = "ORÇAMENTO VS. REALIZADO POR CATEGORIA"
    ws_dash["B8"].font = fonte_titulo

    headers_resumo = ["Categoria", "Meta Mensal", "Gasto no Mês", "Saldo da Meta", "% Utilizado"]
    for idx, text in enumerate(headers_resumo, start=2):
        cell = ws_dash.cell(row=9, column=idx, value=text)
        cell.fill = cor_header
        cell.font = fonte_header
        cell.alignment = Alignment(horizontal="center")

    linha_dash = 10
    for linha_cat in range(4, 12):
        ws_dash.cell(row=linha_dash, column=2, value=f"='Categorias e Metas'!A{linha_cat}")
        ws_dash.cell(row=linha_dash, column=3, value=f"='Categorias e Metas'!C{linha_cat}")
        ws_dash.cell(row=linha_dash, column=4, value=f'=SUMIFS(Lançamentos!H:H, Lançamentos!D:D, B{linha_dash}, Lançamentos!B:B, $G$2)')
        ws_dash.cell(row=linha_dash, column=5, value=f'=C{linha_dash}-D{linha_dash}')
        ws_dash.cell(row=linha_dash, column=6, value=f'=IF(C{linha_dash}>0, D{linha_dash}/C{linha_dash}, 0)')

        for c in range(3, 6):
            ws_dash.cell(row=linha_dash, column=c).number_format = formato_moeda
        ws_dash.cell(row=linha_dash, column=6).number_format = '0.0%'
        for c in range(2, 7):
            ws_dash.cell(row=linha_dash, column=c).border = borda_fina
        linha_dash += 1

    ws_dash.cell(row=linha_dash, column=2, value="TOTAL DESPESAS").font = fonte_negrito
    ws_dash.cell(row=linha_dash, column=3, value=f"=SUM(C10:C{linha_dash-1})").number_format = formato_moeda
    ws_dash.cell(row=linha_dash, column=4, value=f"=SUM(D10:D{linha_dash-1})").number_format = formato_moeda
    ws_dash.cell(row=linha_dash, column=5, value=f"=SUM(E10:E{linha_dash-1})").number_format = formato_moeda
    ws_dash.cell(row=linha_dash, column=6, value=f"=IF(C{linha_dash}>0, D{linha_dash}/C{linha_dash}, 0)").number_format = '0.0%'
    
    for c in range(2, 7):
        ws_dash.cell(row=linha_dash, column=c).fill = cor_sub
        ws_dash.cell(row=linha_dash, column=c).font = fonte_negrito
        ws_dash.cell(row=linha_dash, column=c).border = borda_fina

    grafico = BarChart()
    grafico.type = "col"
    grafico.style = 10
    grafico.title = "Meta vs. Gasto Realizado (Mês Selecionado)"
    grafico.y_axis.title = "Valor (R$)"
    dados_graf = Reference(ws_dash, min_col=3, min_row=9, max_col=4, max_row=linha_dash-1)
    cats_graf = Reference(ws_dash, min_col=2, min_row=10, max_row=linha_dash-1)
    grafico.add_data(dados_graf, titles_from_data=True)
    grafico.set_categories(cats_graf)
    grafico.width = 18
    grafico.height = 10
    ws_dash.add_chart(grafico, "B20")

    for sheet in [ws_dash, ws_lanc, ws_config]:
        for col in sheet.columns:  
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                if cell.value and not str(cell.value).startswith("="):
                    max_length = max(max_length, len(str(cell.value)))
            sheet.column_dimensions[column].width = max((max_length + 4), 16)

    wb.save("Controle_Financeiro_Pro.xlsx")
    print("Planilha 'Controle_Financeiro_Pro.xlsx' criada com sucesso!")

if __name__ == "__main__":
    criar_planilha_pro()
