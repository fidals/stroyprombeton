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
   * Remove Product from Cart by given id.
   * @param {object} event
   */
  function removeFromCart(event) {
    const productId = event.target.getAttribute('data-product-id');
    const productCount = event.target.getAttribute('data-product-count');
    server.removeFromCart(productId)
      .then((data) => {
        mediator.publish('onCartUpdate', data);
        mediator.publish('onProductRemove', [productId, productCount]);
      });
  }

  /**
   * Remove all Products from Cart.
   */
  function flushCart() {
    server.flushCart()
      .then(data => mediator.publish('onCartUpdate', data));
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
