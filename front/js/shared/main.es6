{
  const DOM = {
    $nav: $('.js-nav'),
    navSubnav: '.js-nav-subnav',
    $application: $('.js-application'),
    $search: $('#search'),
    $searchbar: $('.js-searchbar'),
    $searchField: $('.js-search-field'),
    $btnScrollTop: $('#btn-scroll-to-top'),
    $reviews: $('#reviews-wrapper'),
    reviewItem: '.js-reviews-item',
    $moreReviews: $('.js-more-reviews'),
    bannerClass: 'searchbar-banner',
  };

  const config = {
    fetchReviewsUrl: '/fetch-reviews/',
    reviewsToShow: 3,
  };

  const searchbarInitTopValue = parseInt(DOM.$searchbar.css('top'), 10);

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onReviewsFetched',
      appendAndHideReviews,
      overflowReviews,
      addScrollEvent,
    );

    $(window).scroll(toggleScrollToTopBtn);
    $(window).scroll(moveSearchBar);
    DOM.$search.submit(preventEmptySearch);
    DOM.$btnScrollTop.click(scrollToTop);
    DOM.$moreReviews.click(getReviews);
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
   * Move searchbar on index page.
   * Searchbar location on index page is differ from inner pages cause of large banner.
   * After scrolling to the height of the banner, we should to fix Searchbar like on all
   * inner pages.
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

  function getReviews() {
    $.post(config.fetchReviewsUrl)
      .then(
        (reviews) => {
          $(this).fadeOut(500);
          mediator.publish('onReviewsFetched', reviews);
        },
        response => console.warn(response),
      );
  }

  function appendAndHideReviews(_, reviews) {
    DOM.$reviews.append(reviews);
    const reviewsToHide = $(DOM.reviewItem)
      .filter(index => index > 5);

    $.each(reviewsToHide, (_, item) => $(item).hide());
  }

  function overflowReviews() {
    const height = $(DOM.reviewItem).height();
    DOM.$reviews.addClass('overflowed').css('height', height * 2);
  }

  function addScrollEvent() {
    DOM.$reviews.scroll(function() {
      if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
        showReviews();
      }
    });
  }

  function showReviews() {
    $(DOM.reviewItem).filter(':hidden').slice(0, config.reviewsToShow).fadeIn(500);
  }

  init();
}
