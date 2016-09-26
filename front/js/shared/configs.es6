/**
 * There are all common configs for all common plugins.
 * This module is an entry point for plugins initialization.
 */
const configs = (() => {
  const DOM = {
    $phoneInputs: $('.js-masked-phone'),
  };

  const labels = {
    phone: 'phone',
  };

  const init = () => {
    pluginsInit();
    setupXHR();
  };

  function pluginsInit() {
    DOM.$phoneInputs
      .attr('placeholder', '+7 (999) 000 00 00')
      .mask('+9 (999) 999 99 99')
      .on('keyup', event => {
        localStorage.setItem(labels.phone, $(event.target).val());
      });
  }

  /**
   * Set all unsafe ajax requests with csrftoken.
   */
  function setupXHR() {
    const csrfUnsafeMethod = method => !(/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));

    $.ajaxSetup({
      beforeSend: (xhr, settings) => {
        if (csrfUnsafeMethod(settings.type)) {
          xhr.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
        }
      },
    });
  }

  init();

  return { labels };
})();
