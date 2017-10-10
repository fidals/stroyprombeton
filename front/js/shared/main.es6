(() => {
  const DOM = {
    $nav: $('.js-nav'),
    navSubnav: '.js-nav-subnav',
    $application: $('.js-application'),
    $search: $('#search'),
    $searchbar: $('.js-searchbar'),
    $searchField: $('.js-search-field'),
    $btnScrollTop: $('#btn-scroll-to-top'),
    bannerClass: 'searchbar-banner',
    $searchbarWrap: $('.searchbar-wrap'),
    $searchbarContactsWrap: $('.searchbar-contacts-wrap'),
    searchbarClasses: 'col-md-4',
    searchbarIndexClasses: 'col-md-11 col-lg-10',
    searchbarContactsClasses: 'col-xs-12 col-md-8 col-lg-6',
  };

  const searchbarInitTopValue = parseInt(DOM.$searchbar.css('top'), 10);

  const init = () => {
    // Wait until body is rendered due to bugs with FOUC
    if ($('body').is(':visible')) {
      moveSearchBar();
      setUpListeners();
    } else {
      setTimeout(init, 100);
    };
  };

  function setUpListeners() {
    $(window).scroll(toggleScrollToTopBtn);
    $(window).scroll(moveSearchBar);
    $(window).resize(moveSearchBar);
    DOM.$search.submit(preventEmptySearch);
    DOM.$btnScrollTop.click(scrollToTop);
  }

  /**
   * Toggle scroll-to-top button.
   */
  function toggleScrollToTopBtn() {
    return $(window).scrollTop() > 300 ?
      DOM.$btnScrollTop.addClass('active') :
      DOM.$btnScrollTop.removeClass('active');
  }

  /**
   * Animate page scrolling to top.
   */
  function scrollToTop() {
    $('html, body').animate({ scrollTop: 0 }, 300);
  }

  /**
   * Move Searchbar on Index page only.
   * Searchbar location on Index page is differ from other pages cause of banner.
   * After scrolling passes banner - we should to fix Searchbar to top.
   */
  function moveSearchBar() {
    if (!DOM.$application.length) return;

    if (DOM.$searchbar.hasClass('searchbar-banner')) {
      DOM.$searchbarContactsWrap.hide();
    } else {
      DOM.$searchbarContactsWrap.show();
    }

    const scrollTop = $(window).scrollTop();
    const offset = DOM.$application.offset().top - DOM.$nav.height();

    DOM.$searchbar.css('top', searchbarInitTopValue - scrollTop);

    if (scrollTop > offset) {
      DOM.$searchbar.removeClass(DOM.bannerClass);
      DOM.$searchbarWrap.removeClass(DOM.searchbarIndexClasses);
      DOM.$searchbarWrap.addClass(DOM.searchbarClasses);
      DOM.$searchbarContactsWrap.addClass(DOM.searchbarContactsClasses);
    } else {
      DOM.$searchbar.addClass(DOM.bannerClass);
      DOM.$searchbarContactsWrap.removeClass(DOM.searchbarContactsClasses);
      DOM.$searchbarWrap.removeClass(DOM.searchbarClasses);
      DOM.$searchbarWrap.addClass(DOM.searchbarIndexClasses);
    }
  }

  function preventEmptySearch(event) {
    if (!DOM.$searchField.val()) event.preventDefault();
  }

  init();
})();
