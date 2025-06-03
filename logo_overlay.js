// JavaScript para adicionar logo ao controle de camadas e ajustar posições
document.addEventListener('DOMContentLoaded', function() {

  // Função para adicionar a logo ao controle de camadas
  function addLogoToLayerControl() {

    // Aguardar até que o controle de camadas seja criado
    const checkInterval = setInterval(() => {
      const layerControl = document.querySelector('.leaflet-control-layers-list');
      if (layerControl) {
        clearInterval(checkInterval);

        // Criar o link para ComexStat
        const logoLink = document.createElement('a');
        logoLink.href = 'https://comexstat.mdic.gov.br/pt/home';
        logoLink.target = '_blank';
        logoLink.className = 'comexstat-nome';
        logoLink.textContent = 'Comex Stat';

        // Inserir antes do primeiro elemento no controle de camadas
        const controlContainer = document.querySelector('.leaflet-control-layers-base');
        controlContainer.parentNode.insertBefore(logoLink, controlContainer);
      }
    }, 100);
  }

  // Função para adicionar créditos com hyperlinks
  function addCredits() {
    var creditsDiv = document.createElement('div');
    creditsDiv.className = 'credits-box';
    creditsDiv.innerHTML = `
      <p>Fonte de dados: <a href="https://comexstat.mdic.gov.br/pt/home" target="_blank">Comex Stat</a> • Créditos de referência: 
      <a href="https://www.linkedin.com/in/falkzera/" target="_blank">Falkzera</a>, 
      <a href="https://andrewpwheeler.com/2023/04/25/hacking-folium-for-nicer-legends/" target="_blank">Andrew P. Wheeler</a></p>
      <p>Elaborado por: <a href="https://www.linkedin.com/in/arthur-brasill/" target="_blank">Arthur Brasil</a> • 
      <a href="https://github.com/Brasiliinho" target="_blank">Github</a></p>
    `;

    // Adicionar ao mapa
    document.querySelector('.leaflet-container').appendChild(creditsDiv);
  }

  // Adicionar logo ao controle de camadas
  addLogoToLayerControl();

  // Adicionar créditos
  addCredits();

  // Garantir que as camadas respondam corretamente à seleção
  setTimeout(function() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(function(checkbox) {
      checkbox.addEventListener('change', function() {
        window.dispatchEvent(new Event('resize'));
      });
    });
  }, 1000);
});

setTimeout(() => {
    const checkboxes = Array.from(document.querySelectorAll(
        '.leaflet-control-layers-overlays input[type="checkbox"]'
    ));
    checkboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            if (cb.checked) {
                checkboxes.forEach(other => {
                    if (other !== cb && other.checked) {
                        other.click();
                    }
                });
            }
        });
    });
}, 500);