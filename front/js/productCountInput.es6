(() => {
  const DOM = {
    countInput: '.js-count-input',
    countUp: '.js-count-input-up',
    countDown: '.js-count-input-down',
    price: '.js-option-price',
    sum: '.js-option-sum',
  };

  const init = () => {
    setUpListeners();
  };

  /**
   * Subscribing on events using mediator.
   */
  function setUpListeners() {
    mediator.subscribe('onProductsCountUp', countIncrease, changeSum);
    mediator.subscribe('onProductsCountDown', countDecrease, changeSum);

    $(document)
      .on('click', DOM.countUp, function countUp() {
        mediator.publish('onProductsCountUp', $(this).siblings(DOM.countInput));
      })
      .on('click', DOM.countDown, function countDown() {
        mediator.publish('onProductsCountDown', $(this).siblings(DOM.countInput));
      });

    $(DOM.countInput).on('input', event => changeSum(event, event.target));
  }

  function countIncrease(_, input) {
    $(input).val((i, val) => ++val);  // Ignore ESLintBear (no-param-reassign)
  }

  function countDecrease(_, input) {
    $(input).val((i, val) => ((val > 1) ? --val : val));  // Ignore ESLintBear (no-param-reassign)
  }

  function changeSum(_, input) {
    const $input = $(input);
    const $option = $input.parents('tr');
    const productPrice = parseInt($option.find(DOM.price).text(), 10);
    const $sum = $input.parents('tr').find(DOM.sum);
    $sum.text(`${productPrice * $input.val()} руб`);
  }

  init();
})();
