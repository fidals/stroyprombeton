const server = (() => {
  const config = {
    addToCartUrl: '/shop/cart-add/',
    changeCartUrl: '/shop/cart-change/',
    removeFromCartUrl: '/shop/cart-remove/',
    flushCartUrl: '/shop/cart-flush/',
  };

  /**
   * Add product to backend's Cart.
   * @param {number} productId
   * @param {number} quantity
   */
  function addToCart(productId, quantity) {
    return $.post(
      config.addToCartUrl,
      {
        product: productId,
        quantity,
      },
    );
  }

  /**
   * Flush (clear) Cart on backend.
   */
  const flushCart = () => $.post(config.flushCartUrl);

  /**
   * Remove given Product from Cart.
   * @param {string} productId
   */
  const removeFromCart = productId => $.post(config.removeFromCartUrl, { product: productId });

  /**
   * Change Product quantity in Cart.
   * @param {string} productId
   * @param {string} quantity - new quantity of a Product
   */
  function changeInCart(productId, quantity) {
    return $.post(
      config.changeCartUrl,
      {
        product: productId,
        quantity,
      },
    );
  }

  return {
    addToCart,
    flushCart,
    removeFromCart,
    changeInCart,
  };
})();
