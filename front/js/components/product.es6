(() => {
  const DOM = {
    $addToCart: $('.js-add-basket'),
    $counter: $('.js-product-count'),
  };

  const productId = () => DOM.$addToCart.attr('product-id');

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    DOM.$addToCart.click(buyProduct);
  }

  function buyProduct() {
    const { id, count } = {
      id: productId(),
      count: DOM.$counter.val(),
    };

    server.addToCart(id, count)
      .then(data => mediator.publish('onCartUpdate', data));
  }

  init();
})();
