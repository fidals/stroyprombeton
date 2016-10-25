(() => {
  const DOM = {
    $nav: $('.js-nav'),
    navSubnav: '.js-nav-subnav',
    $application: $('.js-application'),
    $searchBar: $('.js-searchbar'),
    $btnContactUs: $('.js-btn-contact-us'),
    $modal: $('.js-modal'),
    $modalClose: $('.js-modal-close'),
    $reviewsItem: $('.js-reviews-item'),
    $reviewsNavItems: $('.js-reviews-nav-item'),
    $btnScrollTop: $('#btn-scroll-to-top'),
    bannerClass: 'searchbar-banner',
    $gbiTooltip: $('.js-object-tooltip.active'),
  };

  const searchbarInitTopValue = parseInt(DOM.$searchBar.css('top'), 10);

  const init = () => {
    setUpListeners();
    pluginsInit();
  };

  function setUpListeners() {
    $(window).scroll(toggleScrollToTopBtn);
    $(window).scroll(moveSearchBar);
    DOM.$btnScrollTop.click(scrollToTop);
    DOM.$btnContactUs.click(showBackcallModal);
    DOM.$modalClose.click(closeBackcallModal);
    DOM.$reviewsNavItems.click(reviewsSlideTo);
  }

  function pluginsInit() {
    DOM.$gbiTooltip.tooltipster({
      anchor: 'bottom-center',
      contentAsHTML: true,
      interactive: true,
      maxWidth: 300,
      offset: [0, 20],
      trigger: 'custom',
      // close tooltip when element is clicked again, tapped or when the mouse leaves it
      triggerClose: {
        click: true,
        // ensuring that scrolling mobile is not tapping
        scroll: false,
        tap: true,
        mouseleave: true,
      },
      // open tooltip when element is clicked, tapped (mobile) or hovered
      triggerOpen: {
        click: true,
        tap: true,
        mouseenter: true,
      },
    });
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

  function showBackcallModal() {
    DOM.$modal.fadeIn();
  }

  function closeBackcallModal() {
    DOM.$modal.fadeOut();
  }

  init();
})();
