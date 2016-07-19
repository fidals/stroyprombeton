const server = (() => {
  const CONFIG = {
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
      CONFIG.addToCartUrl,
      {
        product: productId,
        quantity,
      }
    );
  };

   /**
   * Flush (clear) the cart on backend.
   */
  const flushCart = () => $.post(CONFIG.flushCartUrl);

  /**
   * Remove given product from Cart.
   * @param productId
   */
  const removeFromCart = productId => $.post(CONFIG.removeFromCartUrl, { product: productId });

  /**
   * Return $.post request, which changes quantity of a given Product in Cart.
   * @param productId
   * @param quantity - new quantity of a product
   */
  const changeInCart = (productId, quantity) => {
    return $.post(
      CONFIG.changeCartUrl,
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
