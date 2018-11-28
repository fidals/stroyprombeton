(() => {
  const DOM = {
    $order: $('.js-order-contain'),
    productCount: '.js-count-input',
    remove: '.js-remove',
    form: '#shop-order-form',
    submitBtn: '.btn-order-form',
    productRow: '.js-product-row',
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onCartUpdate', render);

    $(DOM.$order).on('keyup', 'input', storeInput);
    $(DOM.$order).on('keyup', 'textarea', storeInput);
    $(DOM.$order).on('input', DOM.productCount, helpers.debounce(changeProductCount, 300));
    $(DOM.$order).on('click', DOM.remove, removeProduct);
    $(DOM.submitBtn).on('click', DOM.submit, submitOrder);
  }

  const getProductData = ($el) => {
    const $row = $el.closest(DOM.productRow);
    return {
      id: parseInt($row.data('id'), 10),
      quantity: parseInt($row.find(DOM.productCount).val(), 10),
      name: $.trim($row.find('a').text()),
    };
  };

  const getProductsData = () => $(DOM.productRow)
    .map((_, el) => {
      const $el = $(el);
      let data = getProductData($el);  // Ignore ESLintBear (prefer-const)
      data.price = parseFloat($el.closest(DOM.productRow).data('price'));
      return data;
    })
    .get();

  /**
   * Change Product's count in Cart with delay for better UX.
   */
  function changeProductCount(event) {
    const $target = $(event.target);
    let data = getProductData($target);  // Ignore ESLintBear (prefer-const)
    const { id, quantity } = data;
    const countDiff = quantity - $target.data('last-count');

    server.changeInCart(id, quantity)
      .then((newData) => {
        mediator.publish('onCartUpdate', { html: newData });
        if (countDiff > 0) {
          data.quantity = countDiff;
          mediator.publish('onProductAdd', [data]);
        } else {
          mediator.publish('onProductRemove', [id, Math.abs(countDiff)]);
        }
      });
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
    const $target = $(event.target);
    const { id, quantity } = getProductData($target);
    server.removeFromCart(id)
      .then((data) => {
        mediator.publish('onCartUpdate', { html: data });
        mediator.publish('onProductRemove', [id, quantity]);
      });
  }

  /**
   * Add order's table and form html into the page.
   */
  function render(_, data) {
    const html = data.html || data;
    DOM.$order.html(html.table);
  }

  function submitOrder(event) {
    event.preventDefault();
    mediator.publish('onOrderSend', [getProductsData()]);
    // Set timeout to wait handling of onOrderSend
    setTimeout(() => $(DOM.form).submit(), 100);
  }
  init();
})();
