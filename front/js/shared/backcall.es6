class StbBackcall extends Backcall {
  sendOrderCallback() {
    modals.closeModal();
  }

  isValid() {
    // TODO: Validation required.
    return true;
  }
}

const backcall = new StbBackcall();
