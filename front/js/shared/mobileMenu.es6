(() => {
  const DOM = {
    $mobMenuToggler: $('.js-mobile-menu-toggler'),
  };

  const mmenuApi = configs.$menu.data('mmenu');

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    DOM.$mobMenuToggler.click(toggleMenuIcon);
    mmenuApi.bind('closing', toggleMenuIcon);
  }

  function toggleMenuIcon() {
    DOM.$mobMenuToggler.toggleClass('open');
  }

  init();
})();
