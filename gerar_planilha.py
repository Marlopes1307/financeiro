import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import PieChart, BarChart, Reference
from datetime import date

def criar_planilha_financeira():
    wb = openpyxl.Workbook()
    
    # Criando as abas
    ws_dash = wb.active
    ws_dash.title = "Dashboard"
    ws_lanc = wb.create_sheet(title="Lançamentos")
    ws_config = wb.create_sheet(title="Categorias e Metas")

    # Estilos padronizados (Paleta Azul e Cinza moderno)
    cor_header = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
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
    # ABA 3: CATEGORIAS E METAS
    # =========================================================================
    ws_config.append(["Categoria", "Tipo", "Orçamento Mensal (Meta)"])
    
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

    for row in dados_categorias:
        ws_config.append(row)

    # Formatação da Aba Categorias
    for col in range(1, 4):
        cell = ws_config.cell(row=1, column=col)
        cell.fill = cor_header
        cell.font = fonte_header
        cell.alignment = Alignment(horizontal="center")

    for row in range(2, len(dados_categorias) + 2):
        ws_config.cell(row=row, column=3).number_format = formato_moeda
        for col in range(1, 4):
            ws_config.cell(row=row, column=col).border = borda_fina

    # =========================================================================
    # ABA 2: LANÇAMENTOS (Com dados de exemplo)
    # =========================================================================
    headers_lanc = ["Data", "Descrição", "Categoria", "Tipo", "Forma de Pagamento", "Status", "Valor"]
    ws_lanc.append(headers_lanc)

    exemplos_lancamentos = [
        [date(2026, 11, 5), "Salário Mensal", "Salário / Renda Principal", "Receita", "PIX / Transferência", "Pago", 5000.00],
        [date(2026, 11, 6), "Aluguel Apartamento", "Moradia (Aluguel/Condomínio)", "Despesa", "Boleto", "Pago", 1450.00],
        [date(2026, 11, 8), "Supermercado Semana 1", "Alimentação (Mercado/Restaurante)", "Despesa", "Cartão de Crédito", "Pago", 420.50],
        [date(2026, 11, 10), "Conta de Internet", "Contas Fixas (Luz/Água/Internet)", "Despesa", "Débito Automático", "Pago", 120.00],
        [date(2026, 11, 12), "Aporte Tesouro Selic", "Investimentos / Reserva", "Despesa", "PIX / Transferência", "Pago", 1000.00],
        [date(2026, 11, 15), "Abastecimento Carro", "Transporte / Combustível", "Despesa", "Cartão de Débito", "Pago", 210.00],
        [date(2026, 11, 18), "Cinema e Jantar", "Lazer e Assinaturas", "Despesa", "Cartão de Crédito", "Pendente", 180.00],
    ]

    for row in exemplos_lancamentos:
        ws_lanc.append(row)

    # Formatação da Aba Lançamentos
    for col in range(1, 8):
        cell = ws_lanc.cell(row=1, column=col)
        cell.fill = cor_header
        cell.font = fonte_header
        cell.alignment = Alignment(horizontal="center")

    for row in range(2, len(exemplos_lancamentos) + 2):
        ws_lanc.cell(row=row, column=1).number_format = formato_data
        ws_lanc.cell(row=row, column=1).alignment = Alignment(horizontal="center")
        ws_lanc.cell(row=row, column=7).number_format = formato_moeda
        for col in range(1, 8):
            ws_lanc.cell(row=row, column=col).border = borda_fina

    # =========================================================================
    # ABA 1: DASHBOARD (Resumo com Fórmulas Excel)
    # =========================================================================
    ws_dash["B2"] = "CONTROLE FINANCEIRO PESSOAL - RESUMO"
    ws_dash["B2"].font = fonte_titulo

    # Cards de KPIs (Usando fórmulas SOMASES do Excel)
    kpis = [
        ("B4", "Total Receitas (Realizado)", "B5", '=SUMIFS(Lançamentos!G:G, Lançamentos!D:D, "Receita", Lançamentos!F:F, "Pago")'),
        ("D4", "Total Despesas (Realizado)", "D5", '=SUMIFS(Lançamentos!G:G, Lançamentos!D:D, "Despesa", Lançamentos!F:F, "Pago")'),
        ("F4", "Saldo Atual em Caixa", "F5", '=B5-D5'),
        ("H4", "Despesas Pendentes", "H5", '=SUMIFS(Lançamentos!G:G, Lançamentos!D:D, "Despesa", Lançamentos!F:F, "Pendente")')
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

    # Tabela de Acompanhamento por Categoria no Dashboard
    ws_dash["B8"] = "ACOMPANHAMENTO DE DESPESAS POR CATEGORIA"
    ws_dash["B8"].font = fonte_titulo

    headers_resumo = ["Categoria", "Meta Mensal", "Gasto Realizado", "Saldo da Meta", "% Utilizado"]
    for idx, text in enumerate(headers_resumo, start=2):
        cell = ws_dash.cell(row=9, column=idx, value=text)
        cell.fill = cor_header
        cell.font = fonte_header
        cell.alignment = Alignment(horizontal="center")

    # Puxando apenas as categorias de Despesa (linhas 4 a 11 da aba Categorias)
    linha_dash = 10
    for linha_cat in range(4, 12):
        ws_dash.cell(row=linha_dash, column=2, value=f"='Categorias e Metas'!A{linha_cat}")
        ws_dash.cell(row=linha_dash, column=3, value=f"='Categorias e Metas'!C{linha_cat}")
        ws_dash.cell(row=linha_dash, column=4, value=f'=SUMIFS(Lançamentos!G:G, Lançamentos!C:C, B{linha_dash})')
        ws_dash.cell(row=linha_dash, column=5, value=f'=C{linha_dash}-D{linha_dash}')
        ws_dash.cell(row=linha_dash, column=6, value=f'=IF(C{linha_dash}>0, D{linha_dash}/C{linha_dash}, 0)')

        # Formatação das células da tabela resumo
        for c in range(3, 6):
            ws_dash.cell(row=linha_dash, column=c).number_format = formato_moeda
        ws_dash.cell(row=linha_dash, column=6).number_format = '0.0%'
        
        for c in range(2, 7):
            ws_dash.cell(row=linha_dash, column=c).border = borda_fina
            
        linha_dash += 1

    # Linha de Total
    ws_dash.cell(row=linha_dash, column=2, value="TOTAL DESPESAS").font = fonte_negrito
    ws_dash.cell(row=linha_dash, column=3, value=f"=SUM(C10:C{linha_dash-1})").number_format = formato_moeda
    ws_dash.cell(row=linha_dash, column=4, value=f"=SUM(D10:D{linha_dash-1})").number_format = formato_moeda
    ws_dash.cell(row=linha_dash, column=5, value=f"=SUM(E10:E{linha_dash-1})").number_format = formato_moeda
    ws_dash.cell(row=linha_dash, column=6, value=f"=D{linha_dash}/C{linha_dash}").number_format = '0.0%'
    
    for c in range(2, 7):
        ws_dash.cell(row=linha_dash, column=c).fill = cor_sub
        ws_dash.cell(row=linha_dash, column=c).font = fonte_negrito
        ws_dash.cell(row=linha_dash, column=c).border = borda_fina

    # =========================================================================
    # GRÁFICO AUTOMÁTICO NO DASHBOARD
    # =========================================================================
    grafico = BarChart()
    grafico.type = "col"
    grafico.style = 10
    grafico.title = "Meta vs. Gasto Realizado por Categoria"
    grafico.y_axis.title = "Valor (R$)"
    
    dados_graf = Reference(ws_dash, min_col=3, min_row=9, max_col=4, max_row=linha_dash-1)
    cats_graf = Reference(ws_dash, min_col=2, min_row=10, max_row=linha_dash-1)
    
    grafico.add_data(dados_graf, titles_from_data=True)
    grafico.set_categories(cats_graf)
    grafico.width = 18
    grafico.height = 10
    ws_dash.add_chart(grafico, "B20")

    # =========================================================================
    # AJUSTE AUTOMÁTICO DA LARGURA DAS COLUNAS
    # =========================================================================
    for sheet in [ws_dash, ws_lanc, ws_config]:
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if cell.value and not str(cell.value).startswith("="):
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = max((max_length + 4), 16)
            sheet.column_dimensions[column].width = adjusted_width

    # Salvar o arquivo
    nome_arquivo = "Controle_Financeiro_Completo.xlsx"
    wb.save(nome_arquivo)
    print(f"Planilha '{nome_arquivo}' gerada com sucesso!")

if __name__ == "__main__":
    criar_planilha_financeira()
