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
        logoLink.textContent = 'ComexStat';

        // Inserir antes do primeiro elemento no controle de camadas
        const controlContainer = document.querySelector('.leaflet-control-layers-base');
        controlContainer.parentNode.insertBefore(logoLink, controlContainer);
      }
    }, 100);
  }

  // Função para adicionar créditos
  function addCredits() {
    var creditsDiv = document.createElement('div');
    creditsDiv.className = 'credits-box';
    creditsDiv.innerHTML = '<p>Fonte: ComexStat - Ministério da Economia</p><p>Elaboração: Arthur Brasil do grupo PET Economia UFAL</p>';

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
        
        // Forçar atualização do mapa quando uma camada é selecionada/deselecionada
        window.dispatchEvent(new Event('resize'));
      });
    });
  }, 1000);
})