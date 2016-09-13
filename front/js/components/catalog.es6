(() => {
  const DOM = {
    $category: $('.js-catalog-category-title'),
    categoryUL: '.js-catalog-category-ul',
    $subcategory: $('.js-catalog-subcategory'),
    subcategoryUL: '.js-catalog-subcategory-ul',
  };

  const init = () => {
    setUpListeners();
  };

  const setUpListeners = () => {
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

  init();
})();
