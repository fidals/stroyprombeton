(() => {
  const DOM = {
    countInput: '.js-count-input',
    countUp: '.js-count-input-up',
    countDown: '.js-count-input-down',
    $productPrice: $('.js-option-price'),
    $productPriceSum: $('.js-option-sum'),
  };

  const productPrice = parseInt(DOM.$productPrice.text(), 10);

  const init = () => {
    setUpListeners();
  };

  /**
   * Subscribing on events using mediator.
   */
  function setUpListeners() {
    mediator.subscribe('onProductsCountUp', countIncrease, triggerInputChange);
    mediator.subscribe('onProductsCountDown', countDecrease, triggerInputChange);

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
    $(input).val((i, val) => ++val);  // Ignore ESLintBear (no-param-reassign)
  }

  function countDecrease(_, input) {
    $(input).val((i, val) => ((val > 1) ? --val : val));  // Ignore ESLintBear (no-param-reassign)
  }

  function productPriceSum() {
    if (isNaN(productPrice)) return;  // Ignore ESLintBear (no-restricted-globals)
    DOM.$productPriceSum.text(`${productPrice * $(DOM.countInput).val()} руб.`);
  }

  function triggerInputChange(_, target) {
    $(target).trigger('input');
  }

  init();
})();
