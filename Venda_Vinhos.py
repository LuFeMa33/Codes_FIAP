# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "numpy==2.2.6",
#     "pandas==2.3.3",
#     "statsmodels==0.14.6",
# ]
# ///

import marimo

__generated_with = "0.18.4"
app = marimo.App(
    width="medium",
    css_file="/usr/local/_marimo/custom.css",
    auto_download=["html"],
)


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    return ExponentialSmoothing, pd


@app.cell
def _(pd):
    df = pd.read_excel("ExportacaoVinhos_Tratada.xlsx")
    return (df,)


@app.cell
def _(df):
    df
    return


@app.cell
def _(df, pd):
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    return


@app.cell
def _(df, pd):
    df['Quantidade (Kg)'] = pd.to_numeric(df['Quantidade (Kg)'], errors='coerce')
    return


@app.cell
def _(df, pd):
    df['Valor (US$)'] = pd.to_numeric(df['Valor (US$)'], errors='coerce')
    return


@app.cell
def _(df):
    base = (
        df
        .groupby(
            ['Ano', 'Países_Destino', 'Tipo'],
            as_index=False
        )
        .agg({
            'Quantidade (Kg)': 'sum',
            'Valor (US$)': 'sum'
        })
    )
    return (base,)


@app.cell
def _(ExponentialSmoothing, pd):
    def prever_serie(df, coluna, anos_futuros=5):
        df = df.sort_values('Ano')

        serie = pd.to_numeric(df[coluna], errors='coerce').dropna()
        serie.index = df.loc[serie.index, 'Ano']

        if len(serie) == 0:
            return None

        # Apenas 1 ponto → repetir último valor
        if len(serie) == 1:
            return pd.Series([serie.iloc[-1]] * anos_futuros)

        # 2+ pontos → modelo Holt
        modelo = ExponentialSmoothing(
            serie.astype(float),
            trend='add',
            seasonal=None
        ).fit()

        return modelo.forecast(anos_futuros)
    return (prever_serie,)


@app.cell
def _():
    resultado = []
    return (resultado,)


@app.cell
def _(base, prever_serie, resultado):
    ano_max = base['Ano'].max()

    for (pais, tipo), grupo in base.groupby(['Países_Destino', 'Tipo']):
        prev_litros = prever_serie(grupo, 'Quantidade (Kg)')
        prev_valor = prever_serie(grupo, 'Valor (US$)')

        if prev_litros is None or prev_valor is None:
            continue

        for i in range(1, 6):
            resultado.append({
                'Ano': int(ano_max + i),
                'País Destino': pais,
                'Tipo de Vinho': tipo,
                'Litros Previstos': round(float(prev_litros.iloc[i-1]), 2),
                'Valor Previsto (US$)': round(float(prev_valor.iloc[i-1]), 2)
            })
    return


@app.cell
def _(pd, resultado):
    df_previsao = pd.DataFrame(resultado)
    return (df_previsao,)


@app.cell
def _(df_previsao):
    df_previsao
    return


@app.cell
def _(df_previsao):
    df_previsao.to_csv("Exportacao_Previsao_5_anos.csv", index=False)
    return


if __name__ == "__main__":
    app.run()
