const server = (() => {
  const config = {
    addToCartUrl: '/shop/cart-add/',
    changeCartUrl: '/shop/cart-change/',
    removeFromCartUrl: '/shop/cart-remove/',
    flushCartUrl: '/shop/cart-flush/',
  };

  /**
   * Add product to backend's Cart.
   * @param productId
   * @param quantity
   */
  const addToCart = (productId, quantity) => {
    return $.post(
      config.addToCartUrl,
      {
        product: productId,
        quantity,
      }
    );
  };

  /**
   * Flush (clear) the cart on backend.
   */
  const flushCart = () => $.post(config.flushCartUrl);

  /**
   * Remove given product from Cart.
   * @param productId
   */
  const removeFromCart = productId => $.post(config.removeFromCartUrl, { product: productId });

  /**
   * Return $.post request, which changes quantity of a given Product in Cart.
   * @param productId
   * @param quantity - new quantity of a product
   */
  const changeInCart = (productId, quantity) => {
    return $.post(
      config.changeCartUrl,
      {
        product: productId,
        quantity,
      }
    );
  };

  return {
    addToCart,
    flushCart,
    removeFromCart,
    changeInCart,
  };
})();
