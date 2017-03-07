(() => {
  const DOM = {
    $mobileCart: $('.js-mobile-cart'),
    cartQuantity: '.js-cart-size',
    cartPrice: '.js-mobile-cart-price',
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onCartUpdate', toggleCart, updateMobileCart);
  }

  function toggleCart(_, data) {
    const html = data.html || data;
    if (html.total_quantity > 0) {
      DOM.$mobileCart.removeClass('hidden');
    } else {
      DOM.$mobileCart.addClass('hidden');
    }
  }

  /**
   * Update quantity and price.
   */
  function updateMobileCart(_, data) {
    const html = data.html || data;
    $(DOM.cartQuantity).html(html.total_quantity);
    $(DOM.cartPrice).html(html.total_price);
  }

  init();
})();
