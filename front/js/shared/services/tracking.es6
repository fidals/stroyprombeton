(() => {
  const DOM = {
    $order: $('.js-order-contain'),
    productCount: '.js-count-input',
    remove: '.js-remove',
  };

  // @todo #269 Implement tracking of certain actions on front-end for YA and GA.
  //  Actions: clear cart, changing products count on the order page.
  //  See the parent issue for a detail and se#434, that solves the same.

  window.dataLayer = window.dataLayer || [];
  // Load ecommerce plugin for gaTracker
  try {
    ga('require', 'ecommerce');
  } catch (e) {
    var ga = console.error;
    console.error(`GaTracker failed to load. Traceback: ${e}`);
  }
  let yaTracker = new YATracker(window.dataLayer, 'RUB');
  let gaTracker = new GATracker(ga, 'ecommerce');

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onOrderSend', (_, products) => {
      // Use a dummy order's id, because we do not wait complete processing of
      // purchase request.
      let orderData = {id: 'DummyId'};
      yaTracker.purchase(products, orderData);
      gaTracker.purchase(products, orderData);
    });
    // We receive an onProductAdd event from a category and a product pages
    mediator.subscribe('onProductAdd', (_, id, count) => {
      yaTracker.add([{id, quantity: count}]);
    });
    mediator.subscribe('onProductRemove', (_, id, count) => {
      yaTracker.remove([{id, quantity: count}]);
    });
    mediator.subscribe('onProductDetail', (_, id) => yaTracker.detail([{id}]));
  }

  init();
})();
