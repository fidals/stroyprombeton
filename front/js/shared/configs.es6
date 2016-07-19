/**
 * There are all common configs for all common plugins.
 * This module is an entry point for plugins initialization.
 */
const configs = (() => {
  const DOM = {
    $phoneInputs: $('.js-masked-phone'),
  };

  const LABELS = {
    phone: 'phone',
  };

  const init = () => {
    pluginsInit();
  };

  const pluginsInit = () => {
    DOM.$phoneInputs
      .attr('placeholder', '+7 (999) 000 00 00')
      .mask('+9 (999) 999 99 99')
      .on('keyup', (event) => {
        localStorage.setItem(LABELS.phone, $(event.target).val());
      });
  };

  init();

  return { LABELS };
})();
