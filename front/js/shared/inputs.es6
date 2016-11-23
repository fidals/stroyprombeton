{
  const DOM = {
    input: '.js-input-field',
    phone: '.js-masked-phone',
  };

  const init = () => {
    setUpListeners();
    fillSavedInputs();
  };

  function setUpListeners() {
    $(document).on('keyup', DOM.input, storeUserInfo);
    $(document).on('keyup', DOM.input, resetNotValidClass);
    $(document).on('keyup', DOM.phone, validatePhone);
  }

  function storeUserInfo() {
    localStorage.setItem($(this).attr('name'), $(this).val());
  }

  function resetNotValidClass() {
    $(this).parent().removeClass('not-valid');
  }

  function validatePhone() {
    const phoneNumber = $(DOM.phone).val();

    if (!helpers.isPhoneValid(phoneNumber)) {
      $(this).parent()
        .removeClass('valid')
        .addClass('not-valid');

      return;
    }

    $(this).parent()
      .removeClass('not-valid')
      .addClass('valid');
  }

  /**
   * Fill inputs, which have saved localStorage value.
   */
  function fillSavedInputs() {
    $(DOM.input).each((_, item) => {
      const savedValue = localStorage.getItem($(item).attr('name'));

      $(item).val(savedValue);
    });
  }

  init();
}
