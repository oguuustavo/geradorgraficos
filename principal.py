# Modelo de Resposta para Relatório Financeiro
class RelatorioFinanceiroResponse(BaseModel):
    periodo: Dict[str, date]
    total_despesas: float
    total_receitas: float
    imagem: str


# Função para gerar gráficos
def gerar_graficos(
    despesas_por_categoria: Dict[str, float],
    receitas_por_categoria: Dict[str, float]
) -> str:
    # Criação de duas subplots lado a lado
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle("Relatório Financeiro - COFIPEI", fontsize=16)

    # Gráfico de Pizza para Despesas
    if despesas_por_categoria:
        ax1.pie(
            despesas_por_categoria.values(),
            labels=despesas_por_categoria.keys(),
            autopct="%1.1f%%"
        )
        ax1.set_title("Distribuição de Despesas por Categoria")
    else:
        ax1.text(0.5, 0.5, 'Sem Despesas', horizontalalignment='center')
        ax1.set_title("Distribuição de Despesas por Categoria")

    # Gráfico de Barras para Receitas
    if receitas_por_categoria:
        ax2.bar(
            receitas_por_categoria.keys(),
            receitas_por_categoria.values()
        )
        ax2.set_title("Receitas por Categoria")
        ax2.set_xlabel("Categorias")
        ax2.set_ylabel("Valor (R$)")
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    else:
        ax2.text(0.5, 0.5, 'Sem Receitas', horizontalalignment='center')
        ax2.set_title("Receitas por Categoria")

    # Salvar gráfico em memória
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Converter para base64
    imagem_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    return imagem_base64


# Inicialização do FastAPI
app = FastAPI(title="COFIPEI - Controle Financeiro Pessoal Inteligente")


# Endpoint para Relatório Financeiro
@app.post("/relatorio-financeiro", response_model=RelatorioFinanceiroResponse)
def gerar_relatorio_financeiro(request: RelatorioFinanceiroRequest):
    # Converter lista de lançamentos para DataFrame
    df = pd.DataFrame([lancamento.dict() for lancamento in request.lancamentos])

    # Filtrar lançamentos por período
    df_filtrado = df[
        (df['data'] >= request.data_inicial) &
        (df['data'] <= request.data_final)
    ]

    # Processar despesas por categoria
    despesas = df_filtrado[df_filtrado['tipo'] == 'Despesa']
    despesas_por_categoria = despesas.groupby('categoria')['valor'].sum().to_dict()
    total_despesas = despesas['valor'].sum()

    # Processar receitas por categoria
    receitas = df_filtrado[df_filtrado['tipo'] == 'Receita']
    receitas_por_categoria = receitas.groupby('categoria')['valor'].sum().to_dict()
    total_receitas = receitas['valor'].sum()

    # Gerar gráficos
    imagem = gerar_graficos(despesas_por_categoria, receitas_por_categoria)

    return {
        "periodo": {
            "data_inicial": request.data_inicial,
            "data_final": request.data_final,
        },
        "total_despesas": total_despesas,
        "total_receitas": total_receitas,
        "imagem": imagem
    }
