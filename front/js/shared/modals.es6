const modals = (() => {
  const DOM = {
    $btnOpenModal: $('.js-open-modal'),
    $modal: $('.js-modal'),
    $modalClose: $('.js-modal-close'),
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    DOM.$btnOpenModal.click(showModal);
    $(document).on('keyup', closeModal);
    DOM.$modalClose.click(closeModal);
  }

  function showModal(event) {
    const modalId = $(event.target).data('modal-id');

    $(`#${modalId}`).fadeIn();
  }

  function closeModal(event) {
    // We able to close modal by Esc key.
    if (event && event.type === 'keyup' && event.keyCode !== 27) return;

    DOM.$modal.fadeOut();
  }

  init();

  return {
    closeModal,
  };
})();
