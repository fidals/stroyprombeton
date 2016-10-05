(() => {
  const DOM = {
    $gbiMap: $('.gbi-map'),
    $gbiTooltip: $('.gbi-tooltip'),
  };

  const init = () => {
    pluginsInit();
    pasteSearchTerm();
  };

  function pluginsInit() {
    DOM.$gbiMap.maphilight();
    DOM.$gbiTooltip.tooltipster({
      maxWidth: 300,
      interactive: true,
    });
  }

  /**
   * Paste entered user search term in search field.
   */
  function pasteSearchTerm() {
    if (location.pathname !== '/search/') return;

    const searchTerm = decodeURI(location.href).split('?term=')[1];
    $('.js-search-field').val(searchTerm);
  }

  init();
})();
