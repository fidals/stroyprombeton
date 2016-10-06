(() => {
  const DOM = {
    countInput: '.js-count-input',
    countUp: '.js-count-input-up',
    countDown: '.js-count-input-down',
    $productPrice: $('.js-product-price'),
    $productPriceSum: $('.js-product-sum'),
  };

  const productPrice = parseInt(DOM.$productPrice.text(), 10);

  const init = () => {
    setUpListeners();
  };

  /**
   * Subscribing on events using mediator.
   */
  function setUpListeners() {
    mediator.subscribe('onProductsCountUp', countIncrease, productPriceSum);
    mediator.subscribe('onProductsCountDown', countDecrease, productPriceSum);

    $(document)
      .on('click', DOM.countUp, function countUp() {
        mediator.publish('onProductsCountUp', $(this).siblings(DOM.countInput));
      })
      .on('click', DOM.countDown, function countDown() {
        mediator.publish('onProductsCountDown', $(this).siblings(DOM.countInput));
      });

    $(DOM.countInput).on('input', productPriceSum);
  }

  function countIncrease(_, input) {
    $(input).val((i, val) => ++val);
  }

  function countDecrease(_, input) {
    $(input).val((i, val) => (val > 1) ? --val : val);
  }

  function productPriceSum() {
    $(DOM.$productPriceSum).text(`${productPrice * $(DOM.countInput).val()} руб.`);
  }

  init();
})();
