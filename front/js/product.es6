(() => {
  const DOM = {
    $addToCart: $('#buy-product'),
    $counter: $('.js-count-input'),
    $slick: $('.js-slick'),
    slickItem: '.slick-slide',
  };

  const init = () => {
    pluginsInit();
    setUpListeners();
  };

  function pluginsInit() {
    initSlickSlider();
  }

  function setUpListeners() {
    DOM.$addToCart.click(buyProduct);
  }

  function initSlickSlider() {
    DOM.$slick.slick({
      infinite: false,
      lazyLoad: 'ondemand',
      slidesToShow: 3,
      slidesToScroll: 3,
      responsive: [
        {
          breakpoint: 768,
          settings: {
            slidesToShow: 2,
            slidesToScroll: 2,
          },
        },
        {
          breakpoint: 600,
          settings: {
            slidesToShow: 1,
            slidesToScroll: 1,
          },
        },
      ],
    });

    // Recalculate height on window resize:
    $(window).resize(() => DOM.$slick.slick('setPosition'));

    // Equal height for slides
    DOM.$slick.on('setPosition', function slickRecalculate() {
      $(this).find(DOM.slickItem).height('auto');
      const slickTrack = $(this).find('.slick-track');
      $(this).find(DOM.slickItem).css('height', `${$(slickTrack).height()}px`);
    });
  }

  function buyProduct() {
    const { id, count } = {
      id: DOM.$addToCart.attr('data-product-id'),
      count: DOM.$counter.val(),
    };

    server.addToCart(id, count)
      .then(data => mediator.publish('onCartUpdate', data));
  }

  init();
})();
