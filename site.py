import streamlit as st
from streamlit_folium import st_folium
from datetime import datetime
import io
from mapa_alagoas import gerar_mapa
from dados_comex import consulta_comex  

# Configurações da página
st.set_page_config(
    layout="wide",
    page_title="Mapa de Comércio Exterior de Alagoas"
)

# Sidebar para configurações e links
with st.sidebar:
    st.header("Configurações")
   
    # Seleção de intervalo de anos na sidebar
    ano_inicio, ano_fim = st.select_slider(
        "Selecione o intervalo de anos:",
        options=list(range(1997, 2025)),
        value=(2023, 2024),
        key="intervalo_anos"
    )
   
    st.divider()
   
    # Seção de contato
    st.header("👨‍💻 Desenvolvedor")
    st.markdown("**Arthur Brasil**")
   
    # Links com ícones
    st.markdown(
        """
        [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/arthur-brasill/)
       
        [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Brasiliinho)
        """,
        unsafe_allow_html=True
    )
   
    # Informações adicionais
    st.markdown("---")
    st.markdown("### Sobre o Projeto")
    st.markdown(
        """
        Visualização interativa dos dados de comércio exterior
        de Alagoas baseada nos dados do ComexStat.
        """
    )

# Título principal
st.markdown("# Visualização da Exportação × Importação de Alagoas")

# Subtítulo com justificativa
st.markdown(
    """
    ### Análise geográfica das movimentações comerciais por município
    *Dados baseados no ComexStat - Sistema de análise das informações de comércio exterior*
    """
)

# Seção de Downloads logo após o subtítulo
st.markdown("### Downloads")

# Botões de download em duas colunas
download_col1, download_col2 = st.columns(2)

# Gerar o mapa uma vez para usar nos downloads
mapa = gerar_mapa(ano_inicio, ano_fim)

with download_col1:
    # Botão para baixar HTML do mapa - download direto
    html_string = mapa._repr_html_()
    st.download_button(
        label="🗺️ Baixar Mapa (HTML)",
        data=html_string,
        file_name=f"mapa_alagoas_{ano_inicio}_{ano_fim}.html",
        mime="text/html",
        use_container_width=True
    )

with download_col2:
    # Preparar dados para download
    try:
        df_dados = consulta_comex(ano_inicio, ano_fim)
        
        if not df_dados.empty:
            # Adicionar informações de período aos dados
            df_dados['periodo_inicio'] = ano_inicio
            df_dados['periodo_fim'] = ano_fim
            df_dados['data_consulta'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Reordenar colunas para melhor apresentação
            colunas_ordenadas = [
                'noMunMinsgUf', 
                'total_exportado', 
                'total_importado',
                'periodo_inicio',
                'periodo_fim',
                'data_consulta'
            ]
            
            # Verificar se todas as colunas existem
            colunas_existentes = [col for col in colunas_ordenadas if col in df_dados.columns]
            df_final = df_dados[colunas_existentes]
            
            # Converter para CSV
            csv_buffer = io.StringIO()
            df_final.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_data = csv_buffer.getvalue()
            
            # Botão para baixar dados - download direto
            st.download_button(
                label="📊 Baixar Dados (CSV)",
                data=csv_data,
                file_name=f"dados_comercio_alagoas_{ano_inicio}_{ano_fim}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("📊 Baixar Dados (CSV)", disabled=True, use_container_width=True)
            st.caption("⚠️ Nenhum dado disponível para o período")
            
    except Exception as e:
        st.button("📊 Baixar Dados (CSV)", disabled=True, use_container_width=True)
        st.caption(f"❌ Erro: {str(e)}")

# Container para o mapa com largura total
st.markdown("---")

# Usar container com largura total para o mapa
map_container = st.container()
with map_container:
    # Renderizar o mapa com largura total
    map_data = st_folium(
        mapa,
        width=None,  # Usar largura automática (vai ocupar toda a largura disponível)
        height=700,
        key="mapa_alagoas"
    )

# Rodapé com informações adicionais
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        📅 Dados atualizados até 2024 | 🔍 Fonte: ComexStat/MDIC
    </div>
    """,
    unsafe_allow_html=True
)