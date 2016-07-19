/**
 * Category Page module defines logic, operations and DOM for CategoryPage.
 */
const category = (() => {
  const DOM = {
    $addToCart: $('.js-category-buy'),
    productRow: '.js-product-row',
    counter: '.js-product-count',
  };

  const init = () => {
    setUpListeners();
  };

  /**
   * Subscribing on events using mediator.
   */
  const setUpListeners = () => {
    DOM.$addToCart.click((event) => buyProduct(event));
  };

  const buyProduct = (event) => {

    const buyInfo = () => {
      const product = $(event.target);
      const count = product.closest(DOM.productRow).find(DOM.counter).val();
      return {
        count: parseInt(count),
        id: parseInt(product.attr('productId')),
      };
    };

    const { id, count } = buyInfo(event);
    server.addToCart(id, count).then((data) => mediator.publish('onCartUpdate', data));
  };

  init();
})();
