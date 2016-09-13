(() => {
  const DOM = {
    $cart: $('.js-nav-chart'),
    clearCartClass: '.js-clear-cart',
    removeFromCart: '.js-remove',
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onCartUpdate', render);

    // Since product's list in cart dropdown is dynamic, we bind events on static parent
    DOM.$cart.on('click', DOM.clearCartClass, () => clearCart());
    DOM.$cart.on('click', DOM.removeFromCart, event => {
      removeCartProduct(event.target.getAttribute('productId'));
    });
  }

  /**
   * Remove product with the given id from cart.
   * Trigger 'onCartUpdate' event afterwards.
   * @param productId
   */
  function removeCartProduct(productId) {
    server.removeFromCart(productId)
      .then(data => mediator.publish('onCartUpdate', data));
  }

  /**
   * Remove everything from cart.
   * Trigger 'onCartUpdate' event afterwards.
   */
  function clearCart() {
    server.flushCart()
      .then(data => mediator.publish('onCartUpdate', data));
  }

  /**
   * Render new cart's html.
   * @param data
   */
  function render(data) {
    DOM.$cart.html(data.header);
  }

  init();
})();
