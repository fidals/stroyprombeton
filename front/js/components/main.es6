(() => {
  const DOM = {
    $nav: $('.js-nav'),
    navSubnav: '.js-nav-subnav',
    $navNavChart: $('.js-nav-chart'),
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
  };

  const init = () => {
    setupXHR();
    setUpListeners();
  };

  // TODO: move to config module
  // http://youtrack.stkmail.ru/issue/dev-748
  const setupXHR = () => {
    const csrfUnsafeMethod = (method) => !(/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    const token = Cookies.get('csrftoken');

    $.ajaxSetup({
      beforeSend: (xhr, settings) => {
        if (csrfUnsafeMethod(settings.type)) {
          xhr.setRequestHeader('X-CSRFToken', token);
        }
      },
    });
  };

  const setUpListeners = () => {
    $(window).scroll(toggleToTopBtn);
    $(window).scroll(toggleSearchBar);
    DOM.$btnScrollTop.click(scrollToTop);
    DOM.$btnContactUs.click(showContactUs);
    DOM.$modalClose.click(closeModal);
    DOM.$tooltip.click(event => showTooltip($(event.target).next()));

    DOM.$popoverTrigger
      .hover(function () {
        $(this).find(DOM.popover).stop().fadeIn();
      }, function () {
        $(this).find(DOM.popover).stop().fadeOut();
      });

    DOM.$reviewsNavItems.click(reviewsSlideTo);
  };

  const scrollToTop = () => {
    $('html, body').animate({ scrollTop: 0 }, 300);
  };

  const enableScrollToTop = () => {
    DOM.$btnScrollTop.addClass('active');
  };

  const disableScrollToTop = () => {
    DOM.$btnScrollTop.removeClass('active');
  };

  const showTooltip = $item => {
    $item.fadeIn();
    setTimeout(() => $item.fadeOut(), 1000);
  };

  /**
   * Toggles to top button.
   */
  const toggleToTopBtn = () => {
    ($(window).scrollTop() > 300) ? enableScrollToTop() : disableScrollToTop();
  };

  const showContactUs = event => {
    event.preventDefault();
    DOM.$modal.fadeIn();
  };

  const reviewsSlideTo = event => {
    const reviewID = $(event.target).data('slide-to');

    DOM.$reviewsItem
      .removeClass('active')
      .eq(reviewID).addClass('active');

    DOM.$reviewsNavItems
      .removeClass('active')
      .eq(reviewID).addClass('active');
  };

  function toggleSearchBar() {
    if (!DOM.$searchBar.length) return;
    const scrollTop = $(window).scrollTop();
    const offset = DOM.$application.offset().top - DOM.$nav.height();

    if (scrollTop > offset) {
      DOM.$searchBar.addClass('active');
    } else {
      DOM.$searchBar.removeClass('active');
    }
  }

  const closeModal = () => {
    DOM.$modal.fadeOut();
  };

  init();
})();
