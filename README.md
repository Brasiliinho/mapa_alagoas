# Mapa de Comércio Exterior de Alagoas

Este projeto oferece uma **visualização interativa** das movimentações de exportação e importação dos municípios de Alagoas, utilizando dados públicos do **ComexStat**. A aplicação foi desenvolvida com **Streamlit** e utiliza a biblioteca **Folium** para gerar mapas geográficos interativos.

---

## Funcionalidades

- **Seleção de intervalo de anos**: Permite analisar dados de **1997 a 2024**.
- **Visualização geográfica**: Exibe o total **importado**, **exportado** e o **saldo comercial** por município.
- **Camadas separadas**: Mapas distintos para **importação**, **exportação** e **saldo comercial**.
- **Classificação por faixas de valor**: Agrupamento automático dos dados em **intervalos de valores**.
- **Download do mapa**: Exportação do mapa em **formato HTML** com estilos e scripts personalizados.
- **Download de dados**: Exportação dos dados processados em **formato CSV**.

---

## Customizações de Estilo e Script

A interface visual do mapa gerado pelo Folium foi personalizada com os seguintes arquivos:

- `custom_style.css`: Modifica elementos visuais como cores, fontes e bordas.
- `logo_overlay.js`: Insere um logotipo ou marca personalizada sobre o mapa.

Esses arquivos são injetados no HTML do mapa utilizando o método `folium.Element`, conforme o trecho de código abaixo:

```python
with open("custom_style.css", "r") as f:
    m.get_root().header.add_child(folium.Element(f"<style>{f.read()}</style>"))

with open("logo_overlay.js", "r") as f:
    m.get_root().html.add_child(folium.Element(f"<script>{f.read()}</script>"))
```

Essa abordagem injeta **CSS** no `<head>` e **JavaScript** no `<body>` do HTML gerado pelo Folium.

- O CSS altera visualmente o mapa: cores, fontes, bordas e layout.
- O JavaScript adiciona interações e elementos personalizados, como logotipo ou scripts extras.

Tudo é embutido diretamente no HTML final exportado.

---

## Limitação do Streamlit

O **Streamlit impõe restrições de segurança** que impedem a renderização completa de HTML contendo **JavaScript** ou elementos injetados com `folium.Element`. Como resultado:

> As personalizações de estilo e JavaScript aplicadas ao mapa **não são visíveis diretamente** no ambiente Streamlit.

## Solução Alternativa

Para contornar essa limitação, a aplicação inclui um **botão de download** do mapa em formato **HTML**.  
O arquivo baixado contém **todas as modificações de estilo e script aplicadas**, permitindo que o usuário visualize o **resultado final completo** ao abrir o arquivo em um navegador.
