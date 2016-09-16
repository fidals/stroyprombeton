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
    $popoverTrigger: $('.js-popover-trigger'),
    popover: '.js-popover',
    $btnScrollTop: $('#btn-scroll-to-top'),
    $tooltip: $('.js-tooltip'),
    bannerClass: 'searchbar-banner',
  };

  const searchbarInitTopValue = parseInt(DOM.$searchBar.css('top'), 10);

  const init = () => {
    setupXHR();
    setUpListeners();
  };

  // TODO: move to config module
  // http://youtrack.stkmail.ru/issue/dev-748
  function setupXHR() {
    const csrfUnsafeMethod = (method) => !(/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));

    $.ajaxSetup({
      beforeSend: (xhr, settings) => {
        if (csrfUnsafeMethod(settings.type)) {
          xhr.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
        }
      },
    });
  }

  function setUpListeners() {
    $(window).scroll(toggleScrollToTopBtn);
    $(window).scroll(moveSearchBar);
    DOM.$btnScrollTop.click(scrollToTop);
    DOM.$btnContactUs.click(showBackcallModal);
    DOM.$modalClose.click(closeBackcallModal);
    DOM.$tooltip.click(event => showTooltip($(event.target).next()));

    DOM.$popoverTrigger
      .hover(function popoverShow() {
        $(this).find(DOM.popover).stop().fadeIn();
      }, function popoverHide() {
        $(this).find(DOM.popover).stop().fadeOut();
      });

    DOM.$reviewsNavItems.click(reviewsSlideTo);
  }

  function showTooltip($item) {
    $item.fadeIn();
    setTimeout(() => $item.fadeOut(), 1000);
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
   * Slide reviews minicarousel.
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
