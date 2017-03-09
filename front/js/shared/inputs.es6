(() => {
  const DOM = {
    input: '.js-input-field',
  };

  const init = () => {
    setUpListeners();
    fillSavedInputs();
  };

  function setUpListeners() {
    $(document).on('input', DOM.input, storeUserInfo);
  }

  function storeUserInfo() {
    localStorage.setItem($(this).attr('name'), $(this).val());
  }

  /**
   * Fill inputs, which have saved localStorage value.
   * Trigger `keyup` to simulate field update.
   */
  function fillSavedInputs() {
    $(DOM.input).each((_, item) => {
      const savedValue = localStorage.getItem($(item).attr('name'));

      $(item).val(savedValue).trigger('keyup');
    });
  }

  init();
})();
