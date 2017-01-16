class StbBackcall extends Backcall {
  constructor(sendBtnClass) {
    super(sendBtnClass);

    this.DOM = {
      $btnOpenModal: $('.js-open-modal'),
      $modal: $('.js-modal'),
      $modalClose: $('.js-modal-close'),
    };

    this.setUpListeners();
  }

  setUpListeners() {
    $(document).on('keyup', event => this.closeModal(event));
    this.DOM.$modal.on('click', event => this.closeModalOnOuterClick(event));
    this.DOM.$modalClose.click(event => this.closeModal(event));
    this.DOM.$btnOpenModal.click(this.showModal);
  }

  showModal() {
    const modalId = $(this).data('modal-id');
    $(`#${modalId}`).fadeIn();
  }

  closeModal(event) {
    // We able to close modal by Esc key.
    if (event && event.type === 'keyup' && event.keyCode !== 27) return;
    this.DOM.$modal.fadeOut();
  }

  closeModalOnOuterClick(event) {
    const isOuterClick = $(event.target).closest('.modal-call').length;
    if (!isOuterClick) this.DOM.$modal.fadeOut();
  }

  sendOrderCallback() {
    this.closeModal();
  }

  isValid() {
    const phoneNumber = $(this.DOM.$modal).find('#id_phone').val();
    return helpers.isPhoneValid(phoneNumber);
  }
}

const backcall = new StbBackcall('js-send-backcall');
