class StbBackcall extends Backcall {
  constructor(sendBtnClass) {
    super(sendBtnClass);

    this.modal = $('#backcall-modal');
  }

  sendOrderCallback() {
    modals.closeModal();
  }

  isValid() {
    const phoneNumber = $(this.modal).find('#id_phone').val();

    return helpers.isPhoneValid(phoneNumber);
  }
}

const backcall = new StbBackcall();
