import json
import folium
import requests
import geopandas as gpd
from dados_comex import consulta_comex

def gerar_mapa(ano_inicio, ano_fim):
    # Função para construir SVG para grupo de legenda
    def build_svg(di, group_name, edge='#D3D3D3', fill_opacity=0.5, edge_weight=1):
        if edge_weight == 0:
            loc_edge = 0
        else:
            loc_edge = 2
        fin_leg = f"<span>{group_name}"
        for lab, col in di.items():
            fin_leg += '<br><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<svg width="10" height="10">'
            fin_leg += f'<rect width="12" height="12" fill-opacity="{fill_opacity}"'
            fin_leg += f' fill="{col}" style="stroke-width:{loc_edge};stroke:{edge}" />'
            fin_leg += f'</svg> {lab}</span>'
        fin_leg += "</span>"
        return fin_leg

    # URL GeoJSON dos municípios de Alagoas
    geojson_url = 'https://raw.githubusercontent.com/tbrugz/geodata-br/refs/heads/master/geojson/geojs-27-mun.json'
    response = requests.get(geojson_url)
    geojson_data = response.json()

    # Converter para GeoDataFrame
    gdf_alagoas = gpd.GeoDataFrame.from_features(geojson_data)
    gdf_alagoas = gdf_alagoas.rename(columns={'name': 'municipio'})

    # Juntar os dados com a geometria dos municípios
    gdf_merged = gdf_alagoas.merge(
        consulta_comex(f"{ano_inicio}", f"{ano_fim}"),
        # consulta_comex(2020,2024),
        left_on='municipio',
        right_on='noMunMinsgUf',
        how='left'
    )
    gdf_merged.fillna(0, inplace=True)

    # Calcular saldo comercial
    gdf_merged['saldo_comercial'] = gdf_merged['total_exportado'] - gdf_merged['total_importado']

    # Categorizar os municípios baseado no saldo comercial
    def categorize_balance(row):
        if row['total_exportado'] == 0 and row['total_importado'] == 0:
            return "Sem dados"
        elif row['saldo_comercial'] > 0:
            return "Superávit"
        elif row['saldo_comercial'] < 0:
            return "Déficit"
        else:
            return "Equilíbrio"

    gdf_merged['categoria_saldo'] = gdf_merged.apply(categorize_balance, axis=1)

    # Formatação de valor
    def format_value(value):
        if value >= 1_000_000:
            return f"US$ {value/1_000_000:.2f} milhões"
        elif value >= 1_000:
            return f"US$ {value/1_000:.2f} mil"
        else:
            return f"US$ {value:.2f}"

    gdf_merged['importado_fmt'] = gdf_merged['total_importado'].apply(format_value)
    gdf_merged['exportado_fmt'] = gdf_merged['total_exportado'].apply(format_value)
    gdf_merged['saldo_fmt'] = gdf_merged['saldo_comercial'].apply(lambda x: format_value(abs(x)))

    # Mapa centrado em Alagoas
    m = folium.Map(
    location=[-9.5713, -36.7820],
    zoom_start=9,
    tiles=None,
    control_scale=True
    )

    # Adiciona o OpenStreetMap como camada base alternativa
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='Street Map',
        control=True
    ).add_to(m)
    
    # Adiciona o CartoDB Positron como camada base inicial
    folium.TileLayer(
        tiles='cartodbpositron',
        name='White board',
        control=True
    ).add_to(m)

    # Criar paletas de cores
    import_palette = {
        'Muito Alto (>100M)': '#08306b',
        'Alto (>50M-100M)': '#2171b5',
        'Médio (>10M-50M)': '#6baed6',
        'Baixo (>1M-10M)': '#c6dbef',
        'Muito Baixo (<1M)': '#f7fbff',
        'Sem importação': '#f0f0f0'
    }

    export_palette = {
        'Muito Alto (>100M)': '#00441b',
        'Alto (>50M-100M)': '#238b45',
        'Médio (>10M-50M)': '#74c476',
        'Baixo (>1M-10M)': '#c7e9c0',
        'Muito Baixo (<1M)': '#f7fcf5',
        'Sem exportação': '#f0f0f0'
    }

    balance_palette = {
        'Superávit': '#238b45',
        'Déficit': '#cb181d',
        'Equilíbrio': '#9467bd',
        'Sem dados': '#f0f0f0'
    }

    # Função para determinar categoria de importação
    def import_category(value):
        if value == 0:
            return 'Sem importação'
        elif value < 1000000:
            return 'Muito Baixo (<1M)'
        elif value <= 10000000:
            return 'Baixo (>1M-10M)'
        elif value <= 50000000:
            return 'Médio (>10M-50M)'
        elif value <= 100000000:
            return 'Alto (>50M-100M)'
        else:
            return 'Muito Alto (>100M)'

    # Função para determinar categoria de exportação
    def export_category(value):
        if value == 0:
            return 'Sem exportação'
        elif value < 1000000:
            return 'Muito Baixo (<1M)'
        elif value <= 10000000:
            return 'Baixo (>1M-10M)'
        elif value <= 50000000:
            return 'Médio (>10M-50M)'
        elif value <= 100000000:
            return 'Alto (>50M-100M)'
        else:
            return 'Muito Alto (>100M)'
    
    # Adicionar categorias aos dados
    gdf_merged['import_cat'] = gdf_merged['total_importado'].apply(import_category)
    gdf_merged['export_cat'] = gdf_merged['total_exportado'].apply(export_category)

    # Função de estilo para importações
    def style_import(feature):
        municipality = feature['properties']['municipio']
        imp_value = feature['properties'].get('total_importado', 0)
        category = import_category(imp_value)

        if imp_value == 0:
            return {
                'fillColor': import_palette[category],
                'color': '#5A5A5A',
                'weight': 0.5,
                'fillOpacity': 0
            }
        else:
            return {
                'fillColor': import_palette[category],
                'color': '#5A5A5A',
                'weight': 0.5,
                'fillOpacity': 0.7
            }

    # Função de estilo para exportações
    def style_export(feature):
        municipality = feature['properties']['municipio']
        exp_value = feature['properties'].get('total_exportado', 0)
        category = export_category(exp_value)

        if exp_value == 0:
            return {
                'fillColor': export_palette[category],
                'color': '#5A5A5A',
                'weight': 0.5,
                'fillOpacity': 0
            }
        else:
            return {
                'fillColor': export_palette[category],
                'color': '#5A5A5A',
                'weight': 0.5,
                'fillOpacity': 0.7
            }

    # Função de estilo para saldo comercial
    def style_balance(feature):
        balance_cat = feature['properties'].get('categoria_saldo', 'Sem dados')

        if balance_cat == 'Sem dados':
            return {
                'fillColor': balance_palette[balance_cat],
                'color': '#5A5A5A',
                'weight': 0.5,
                'fillOpacity': 0
            }
        else:
            return {
                'fillColor': balance_palette[balance_cat],
                'color': '#5A5A5A',
                'weight': 0.5,
                'fillOpacity': 0.7
            }

    # Função de highlight para tooltip
    def highlight_function(feature):
        return {
            'weight': 3,
            'color': '#666',
            'fillOpacity': 0.9
        }

    # Preparar os dados para GeoJSON
    gdf_merged_json = gdf_merged.to_json()
    gdf_merged_dict = json.loads(gdf_merged_json)

    # Criar grupos de features para o mapa
    import_svg = build_svg(import_palette, 'Importações (US$)', edge='#5A5A5A', fill_opacity=0.7)
    export_svg = build_svg(export_palette, 'Exportações (US$)', edge='#5A5A5A', fill_opacity=0.7)
    balance_svg = build_svg(balance_palette, 'Saldo Comercial', edge='#5A5A5A', fill_opacity=0.7)

    # Adicionar camada de importações
    import_group = folium.FeatureGroup(name=import_svg, show=True)
    import_geojson = folium.GeoJson(
        gdf_merged_dict,
        name='Importações',
        style_function=style_import,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['municipio', 'importado_fmt'],
            aliases=['Município:', 'Importação:'],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: white;
                border: 1px solid black;
                border-radius: 3px;
                box-shadow: 3px 3px 3px rgba(0,0,0,0.2);
                font-family: sans-serif;
                padding: 5px;
            """,
            tooltip_sticky=False,
            max_width=300,
            format_numbers=True
        ),
    )
    import_geojson.add_to(import_group)
    import_group.add_to(m)

    # Adicionar camada de exportações
    export_group = folium.FeatureGroup(name=export_svg, show=False)
    export_geojson = folium.GeoJson(
        gdf_merged_dict,
        name='Exportações',
        style_function=style_export,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['municipio', 'exportado_fmt'],
            aliases=['Município:', 'Exportação:'],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: white;
                border: 1px solid black;
                border-radius: 3px;
                box-shadow: 3px 3px 3px rgba(0,0,0,0.2);
                font-family: sans-serif;
                padding: 5px;
            """,
            tooltip_sticky=False,
            max_width=300,
            format_numbers=True
        ),
    )
    export_geojson.add_to(export_group)
    export_group.add_to(m)

    # Adicionar camada de saldo comercial
    balance_group = folium.FeatureGroup(name=balance_svg, show=False)
    balance_geojson = folium.GeoJson(
        gdf_merged_dict,
        name='Saldo Comercial',
        style_function=style_balance,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['municipio', 'saldo_fmt', 'categoria_saldo'],
            aliases=['Município:', 'Saldo:', 'Situação:'],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: white;
                border: 1px solid black;
                border-radius: 3px;
                box-shadow: 3px 3px 3px rgba(0,0,0,0.2);
                font-family: sans-serif;
                padding: 5px;
            """,
            tooltip_sticky=False,
            max_width=300,
            format_numbers=True
        ),
    )
    balance_geojson.add_to(balance_group)
    balance_group.add_to(m)

    with open("custom_style.css", "r", encoding="utf-8") as f:
        m.get_root().header.add_child(folium.Element(f"<style>{f.read()}</style>"))

    with open("logo_overlay.js", "r", encoding="utf-8") as f:
        m.get_root().html.add_child(folium.Element(f"<script>{f.read()}</script>"))

    # Mudar a posição do controle de camadas para o canto superior direito
    folium.LayerControl(
    collapsed=False,
    position='topright',
    exclusive_groups=["Importações", "Exportações", "Saldo Comercial"]
    ).add_to(m)

    return m