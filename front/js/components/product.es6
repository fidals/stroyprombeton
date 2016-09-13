const product = (() => {
  const DOM = {
    $category: $('.js-catalog-category-title'),
    categoryUL: '.js-catalog-category-ul',
    $subcategory: $('.js-catalog-subcategory'),
    subcategoryUL: '.js-catalog-subcategory-ul',

    // old ones:
    $addToCart: $('.js-add-basket'),
    $counter: $('.js-product-count'),
  };

  const productId = () => DOM.$addToCart.attr('product-id');

  const init = () => {
    setUpListeners();
  };

  const setUpListeners = () => {
    DOM.$addToCart.click(buyProduct);

    DOM.$category
      .click(function () {
        toggleCategory($(this));
      });

    DOM.$subcategory
      .click(function () {
        toggleSubcategory($(this));
      });
  };

  const toggleCategory = $category => {
    $category
      .toggleClass('catalog-category-title-active')
      .next(DOM.categoryUL)
      .stop()
      .slideToggle();
  };

  const toggleSubcategory = $subcategory => {
    $subcategory
      .find('.catalog-subcategory-ico')
      .toggleClass('fa-minus')
      .toggleClass('fa-plus')
      .end()
      .toggleClass('catalog-subcategory-active')
      .next(DOM.subcategoryUL)
      .stop()
      .slideToggle();
  };

  const buyProduct = () => {
    const { id, count } = {
      id: productId(),
      count: DOM.$counter.val(),
    };

    server.addToCart(id, count).then(data => mediator.publish('onCartUpdate', data));
  };

  init();
})();
