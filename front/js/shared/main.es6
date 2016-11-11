{
  const DOM = {
    $nav: $('.js-nav'),
    navSubnav: '.js-nav-subnav',
    $application: $('.js-application'),
    $searchBar: $('.js-searchbar'),
    $reviewsItem: $('.js-reviews-item'),
    $reviewsNavItems: $('.js-reviews-nav-item'),
    $btnScrollTop: $('#btn-scroll-to-top'),
    bannerClass: 'searchbar-banner',
  };

  const searchbarInitTopValue = parseInt(DOM.$searchBar.css('top'), 10);

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    $(window).scroll(toggleScrollToTopBtn);
    $(window).scroll(moveSearchBar);
    DOM.$btnScrollTop.click(scrollToTop);
    DOM.$reviewsNavItems.click(reviewsSlideTo);
  }

  /**
   * Toggle scroll-to-top button.
   */
  function toggleScrollToTopBtn() {
    $(window).scrollTop() > 300 ?
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
   * Slide reviews carousel.
   */
  function reviewsSlideTo(event) {
    const reviewID = $(event.target).data('slide-to');

    DOM.$reviewsItem
      .removeClass('active')
      .eq(reviewID).addClass('active');

    DOM.$reviewsNavItems
      .removeClass('active')
      .eq(reviewID).addClass('active');
  }

  /**
   * Move searchbar on index page.
   * Searchbar location on index page is differ from inner pages cause of large banner.
   * After scrolling to the height of the banner, we should to fix Searchbar like on all
   * inner pages.
   */
  function moveSearchBar() {
    if (!DOM.$application.length) return;

    const scrollTop = $(window).scrollTop();
    const offset = DOM.$application.offset().top - DOM.$nav.height();

    DOM.$searchBar.css('top', searchbarInitTopValue - scrollTop);

    if (scrollTop > offset) {
      DOM.$searchBar.removeClass(DOM.bannerClass);
    } else {
      DOM.$searchBar.addClass(DOM.bannerClass);
    }
  }

  init();
}
