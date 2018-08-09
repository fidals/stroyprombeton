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

  const getProductId = $target => $target.closest(DOM.productRow).data('product-id');
  const getProductCount = $target => $target.closest(DOM.productRow).find(DOM.productCount).val();
  const getProductName = $target => $.trim($target.find('a').text());

  const getProductsData = () => $(DOM.productRow).map((_, el) => {
    const $el = $(el);
    return {
      id: getProductId($el),
      name: getProductName($el),
      quantity: getProductCount($el),
    };
  }).get();

  /**
   * Change Product's count in Cart with delay for better UX.
   */
  function changeProductCount(event) {
    const $target = $(event.target);
    const productId = getProductId($target);
    const newCount = getProductCount($target);
    const countDiff = newCount - $target.attr('data-last-count');

    server.changeInCart(productId, newCount)
      .then((data) => {
        mediator.publish('onCartUpdate', { html: data });
        if (countDiff > 0) {
          mediator.publish('onProductAdd', [productId, countDiff]);
        } else {
          mediator.publish('onProductRemove', [productId, Math.abs(countDiff)]);
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
    const productId = getProductId($target);
    const productCount = getProductCount($target);
    server.removeFromCart(productId)
      .then((data) => {
        mediator.publish('onCartUpdate', { html: data });
        mediator.publish('onProductRemove', [productId, productCount]);
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
