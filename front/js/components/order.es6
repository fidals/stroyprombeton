(() => {
  const DOM = {
    $order: $('.js-order-contain'),
    productCount: '.js-count-input',
    remove: '.js-remove',
    orderForm: {
      name: '#id_name',
      phone: '#id_phone',
      email: '#id_email',
      company: '#id_company',
      address: '#id_address',
      comment: '#id_comment',
    },
  };

  const init = () => {
    setUpListeners();
    fillSavedInputs();
  };

  function setUpListeners() {
    mediator.subscribe('onCartUpdate', renderTable, fillSavedInputs);

    $(DOM.$order).on('keyup', 'input', storeInput);
    $(DOM.$order).on('keyup', 'textarea', storeInput);
    $(DOM.$order).on('input', DOM.productCount, changeProductCount);
    $(DOM.$order).on('click', DOM.remove, removeProduct);
  }

  const getProductId = $target => $target.closest('.js-product-row').data('product-id');

  /**
   * Fill inputs, which have saved to localstorage value.
   * Runs on page load, and on every cart's update.
   */
  function fillSavedInputs() {
    const getFieldByName = name => $(`#id_${name}`);

    for (const fieldName in DOM.orderForm) {
      if ({}.hasOwnProperty.call(DOM.orderForm, fieldName)) {
        const $field = getFieldByName(fieldName);
        const savedValue = localStorage.getItem(fieldName);

        if ($field && savedValue) {
          $field.val(savedValue);
        }
      }
    }
  }

  /**
   * Change Product's count in Cart with delay for better UX.
   */
  function changeProductCount(event) {
    helpers.delay(() => {
      const $target = $(event.target);
      const productID = getProductId($target);
      const newCount = $target.closest('.js-product-row').find(DOM.productCount).val();

      server.changeInCart(productID, newCount)
        .then(data => mediator.publish('onCartUpdate', { html: data }));
    }, 300);
  }

  /**
   * Store inputted value into localStorage.
   */
  function storeInput(event) {
    const $target = $(event.target);

    localStorage.setItem($target.attr('name'), $target.val());
  }

  /**
   * Remove product from Cart's table.
   */
  function removeProduct(event) {
    const productID = getProductId($(event.target));

    server.removeFromCart(productID)
      .then((data) => {
        mediator.publish('onCartUpdate', { html: data });
      });
  }

  /**
   * Add order's table and form html into the page.
   */
  function renderTable(_, data) {
    DOM.$order.html(data.html.table);
  }

  init();
})();
