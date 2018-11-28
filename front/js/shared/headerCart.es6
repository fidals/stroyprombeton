(() => {
  const DOM = {
    $cartWrapper: $('.js-cart-wrapper'),
    $orderTable: $('.js-order-contain'),
    flushCart: '.js-flush-cart',
    removeFromCart: '.js-remove',
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onCartUpdate', render, showCart);

    // Bind events on static parent cause of dynamic product list in Cart.
    DOM.$cartWrapper.on('click', DOM.flushCart, flushCart);
    DOM.$cartWrapper.on('click', DOM.removeFromCart, removeFromCart);
  }

  /**
   * Get id and count of a removed product.
   * @param {object}
   */
  function getRemovedProductData(removed) {
    return {
      id: parseInt(removed.data('id'), 10),
      quantity: parseInt(removed.data('quantity'), 10),
    };
  }

  /**
   * Remove Product from Cart by given id.
   * @param {object} event
   */
  function removeFromCart(event) {
    const { id, quantity } = getRemovedProductData($(event.target));
    server.removeFromCart(id)
      .then((data) => {
        mediator.publish('onCartUpdate', data);
        mediator.publish('onProductRemove', [id, quantity]);
      });
  }

  /**
   * Remove all Products from Cart.
   */
  function flushCart() {
    const productsData = $(DOM.removeFromCart)
      .map((_, el) => getRemovedProductData($(el)))
      .get();
    server.flushCart()
      .then((data) => {
        mediator.publish('onCartUpdate', data);
        mediator.publish('onCartClear', [productsData]);
      });
  }

  /**
   * Render new Cart's html.
   * @param {string} data - html from server
   */
  function render(_, data) {
    const html = data.html || data;
    DOM.$cartWrapper.html(html.header);
  }

  /**
   * Perform header Cart dropdown animation for every page, except order page.
   */
  function showCart() {
    if (DOM.$orderTable.size() > 0) return;

    const $cartProductsList = DOM.$cartWrapper.find('.js-cart');
    $cartProductsList.addClass('active');

    setTimeout(() => {
      $cartProductsList.removeClass('active');
    }, 1500);
  }

  init();
})();
