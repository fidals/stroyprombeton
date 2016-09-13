(() => {
  const DOM = {
    $categoriesItem: $('.js-series-categories-item'),
  };

  const init = () => {
    setUpListeners();
  };

  const setUpListeners = () => {
    DOM.$categoriesItem.click(toggleCategoriesSection);
  };

  const toggleCategoriesSection = () => {
    DOM.$categoriesItem.removeClass('active');
    $(event.target).addClass('active');
  };

  init();
})();
