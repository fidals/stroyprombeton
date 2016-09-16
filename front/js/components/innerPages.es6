(() => {
  const DOM = {
    $gbiMap: $('.gbi-map'),
    $gbiTooltip: $('.gbi-tooltip'),
  };

  const init = () => {
    pluginsInit();
  };

  const pluginsInit = () => {
    DOM.$gbiMap.maphilight();
    DOM.$gbiTooltip.tooltipster({
      maxWidth: 300,
      interactive: true,
    });
  };

  init();
})();
