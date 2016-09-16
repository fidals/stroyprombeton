(() => {
  const DOM = {
    $catalogLink: $('.js-catalog-title'),
    categoryList: '.js-catalog-ul',
    listWrapper: 'catalog-ul-wrapper',
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    DOM.$catalogLink.click(event => toggleFirstLevelList(event));
  }


  function toggleFirstLevelList(event) {
    event.preventDefault();

    $(event.target)
      .toggleClass('active')
      .next(DOM.categoryList)
      .stop()
      .slideToggle()
      .find('ul')
      .stop()
      .slideToggle();
  }

  init();
})();
