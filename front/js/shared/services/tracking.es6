(() => {
  // @todo #303:60m Send `purchase` event to YA and GA after a success purchase.
  //  This will allow us to send order's id. Currently we send the event after
  //  submitting of the purchase button with the dummy order's id.
  //  See the parent issue for a detail.

  // @todo #303:60m Send info about product's brand to YA and GA.

  // @todo #759:60m Create tests for eCommerce tracking.
  //  Test all events, that perform tracking operations.

  window.dataLayer = window.dataLayer || [];
  const loadedGa = loadGaTransport('gtm_loaded');  // Ignore ESLintBear (no-undef)
  const yaTracker = new YATracker(window.dataLayer, 'RUB');  // Ignore ESLintBear (no-undef)
  const gaTracker = new GATracker(loadedGa, 'ecommerce');  // Ignore ESLintBear (no-undef)

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
    mediator.subscribe('onProductAdd', (_, data) => {
      yaTracker.add([data]);
    });
    mediator.subscribe('onProductRemove', (_, id, quantity) => {
      yaTracker.remove([{ id, quantity }]);
    });
    mediator.subscribe('onProductDetail', (_, data) => yaTracker.detail([data]));
  }

  init();
})();
