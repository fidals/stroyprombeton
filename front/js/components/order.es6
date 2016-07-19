const order = (() => {
  const DOM = {
    $order: $('.js-order-contain'),
    seSubmit: '#btn-send-se',
    productCount: '.js-prod-count',
    remove: '.js-remove',
    orderForm: {
      name: '#id_name',
      phone: '#id_phone',
      email: '#id_email',
      company: '#id_company',
    },
  };

  const init = () => {
    setUpListeners();
    fillSavedInputs();
  };

  /**
   * Fill inputs, which have saved to localstorage value.
   * Runs on page load, and on every cart's update.
   */
  const fillSavedInputs = () => {
    const getFieldByName = (name) => $(`#id_${name}`);

    for (const fieldName in DOM.orderForm) {
      if ({}.hasOwnProperty.call(DOM.orderForm, fieldName)) {
        const $field = getFieldByName(fieldName);
        const savedValue = localStorage.getItem(fieldName);

        if ($field && savedValue) {
          $field.val(savedValue);
        }
      }
    }
  };

  /**
   * Event handler for changing product's count in Cart.
   * We wait at least 100ms every time the user pressed the button.
   */
  const changeProductCount = (event) => {
    const productID = event.target.getAttribute('productId');
    const newCount = event.target.value;

    setTimeout(
      () => server.changeInCart(productID, newCount)
        .then(data => mediator.publish('onCartUpdate', data)),
      100
    );
  };

  const setUpListeners = () => {
    /**
     * Bind events to parent's elements, because we can't bind event to dynamically added element.
     * @param eventName - standard event name
     * @param element - element, which is a child of parent's element (DOM.$order)
     * @param handler - callable which will be dispatched on event
     */
    const subscribeOrderEvent = (eventName, element, handler) => {
      DOM.$order.on(eventName, element, handler);
    };
    const getEventTarget = event => $(event.target);

    subscribeOrderEvent('change', DOM.productCount, event => changeProductCount(event));
    subscribeOrderEvent('click', DOM.remove, event => remove(event.target.getAttribute('productId')));
    subscribeOrderEvent('keyup', 'input', event => storeInput(getEventTarget(event)));

    mediator.subscribe('onCartUpdate', renderTable);
  };

  /**
   * Store inputted value into LocalStorage.
   */
  const storeInput = target => {
    localStorage.setItem(target.attr('name'), target.val());
  };

  /**
   * Remove product from cart's table and dispatches 'onCartUpdate' event.
   */
  const remove = productId => {
    server.removeFromCart(productId).then(data => {
      mediator.publish('onCartUpdate', data);
    });
  };

  /**
   * Render table and form.
   * After that, fill in saved form data.
   */
  const renderTable = (event, data) => {
    DOM.$order.html(data.table);
    fillSavedInputs();
  };

  init();
})();
