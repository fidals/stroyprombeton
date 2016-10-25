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
    DOM.$cartWrapper.on('click', DOM.flushCart, () => flushCart());
    DOM.$cartWrapper.on('click', DOM.removeFromCart, (event) => {
      removeFromCart(event.target.getAttribute('data-product-id'));
    });
  }

  /**
   * Remove Product from Cart by given id.
   * @param {string} productId
   */
  function removeFromCart(productId) {
    server.removeFromCart(productId)
      .then(data => mediator.publish('onCartUpdate', { html: data }));
  }

  /**
   * Remove all Products from Cart.
   */
  function flushCart() {
    server.flushCart()
      .then(data => mediator.publish('onCartUpdate', { html: data }));
  }

  /**
   * Render new Cart's html.
   * @param {string} data - html form server
   */
  function render(_, data) {
    DOM.$cartWrapper.html(data.html.header);
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
    }, 3000);
  }

  init();
})();
