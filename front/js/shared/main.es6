{
  const DOM = {
    $nav: $('.js-nav'),
    navSubnav: '.js-nav-subnav',
    $application: $('.js-application'),
    $search: $('#search'),
    $searchbar: $('.js-searchbar'),
    $searchField: $('.js-search-field'),
    $btnScrollTop: $('#btn-scroll-to-top'),
    bannerClass: 'searchbar-banner',
  };

  const searchbarInitTopValue = parseInt(DOM.$searchbar.css('top'), 10);

  const init = () => {
    moveSearchBar();
    setUpListeners();
  };

  function setUpListeners() {
    $(window).scroll(toggleScrollToTopBtn);
    $(window).scroll(moveSearchBar);
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

    const scrollTop = $(window).scrollTop();
    const offset = DOM.$application.offset().top - DOM.$nav.height();

    DOM.$searchbar.css('top', searchbarInitTopValue - scrollTop);

    if (scrollTop > offset) {
      DOM.$searchbar.removeClass(DOM.bannerClass);
    } else {
      DOM.$searchbar.addClass(DOM.bannerClass);
    }
  }

  function preventEmptySearch(event) {
    if (!DOM.$searchField.val()) event.preventDefault();
  }

  init();
}
