(() => {
  const DOM = {
    $order: $('.js-order-contain'),
    productCount: '.js-count-input',
    remove: '.js-remove',
  };

  window.dataLayer = window.dataLayer || [];
  // Load ecommerce plugin for gaTracker
  try {
    ga('require', 'ecommerce');  // Ignore ESLintBear (no-use-before-define)
  } catch (e) {
    var ga = console.error;  // Ignore ESLintBear (no-unused-vars)
    console.error(`GaTracker failed to load. Traceback: ${e}`);
  }
  const yaTracker = new YATracker(window.dataLayer, 'RUB');  // Ignore ESLintBear (no-undef)
  const gaTracker = new GATracker(ga, 'ecommerce');  // Ignore ESLintBear (no-undef)

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onOrderSend', (_, products) => {
      // Use a dummy order's id, because we do not wait complete processing of
      // purchase request.
      const orderData = { id: 'DummyId' };
      yaTracker.purchase(products, orderData);
      gaTracker.purchase(products, orderData);
    });
    mediator.subscribe('onCartClear', (_, products) => {
      yaTracker.remove(products);
    });
    // We receive an onProductAdd event from a category and a product pages
    mediator.subscribe('onProductAdd', (_, id, quantity) => {
      yaTracker.add([{ id, quantity }]);
    });
    mediator.subscribe('onProductRemove', (_, id, quantity) => {
      yaTracker.remove([{ id, quantity }]);
    });
    mediator.subscribe('onProductDetail', (_, id) => yaTracker.detail([{ id }]));
  }

  init();
})();
