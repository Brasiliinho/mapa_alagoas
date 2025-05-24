import requests
import pandas as pd
import streamlit as st

@st.cache_data
def consulta_comex(ano_inicio, ano_fim):
    url = "https://api-comexstat.mdic.gov.br/cities?language=pt"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    def consulta_fluxo(flow):
        payload = {
            "flow": flow,
            "monthDetail": True,
            "period": {
                "from": f"{ano_inicio}-01",
                "to": f"{ano_fim}-12"
            },
            "filters": [
                {
                    "filter": "state",
                    "values": [27]
                }
            ],
            "details": ["city", "country", "economicBlock"],
            "metrics": ["metricFOB"]
        }
        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and data["data"].get("list"):
                df = pd.DataFrame(data["data"]["list"])
                df['flow'] = flow
                return df
        return pd.DataFrame()
    
    # Consultar dados de importação e exportação
    df_import = consulta_fluxo("import")
    df_export = consulta_fluxo("export")
    
    if df_import.empty and df_export.empty:
        return pd.DataFrame()
    
    # Combinar dados
    df_total = pd.concat([df_import, df_export], ignore_index=True)
    df_total["metricFOB"] = df_total["metricFOB"].astype(int)
    
    # Ajustar nome do município se necessário
    if "noMunMinsgUf" in df_total.columns:
        df_total["noMunMinsgUf"] = df_total["noMunMinsgUf"].astype(str).str[:-5]
    
    # Agregar dados por município usando pivot_table (otimizado)
    df_combined_acum = pd.pivot_table(
        df_total,
        values='metricFOB',
        index='noMunMinsgUf',
        columns='flow',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Renomear colunas para o formato final esperado
    df_combined_acum.rename(
        columns={'import': 'total_importado', 'export': 'total_exportado'},
        inplace=True
    )
    
    return df_combined_acum