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
    publishDetail();
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

  function getProductData() {
    return {
      id: parseInt(DOM.$addToCart.data('id'), 10),
      name: DOM.$addToCart.data('name'),
      category: DOM.$addToCart.data('category'),
      quantity: parseInt(DOM.$counter.val(), 10),
    };
  }

  function buyProduct() {
    const data = getProductData();
    const { id, quantity } = data;

    server.addToCart(id, quantity)
      .then((newData) => {
        mediator.publish('onCartUpdate', newData);
        mediator.publish('onProductAdd', [data]);
      });
  }

  function publishDetail() {
    const { id, name, category } = getProductData();
    if (id) {
      mediator.publish('onProductDetail', [{ id, name, category }]);
    }
  }

  init();
})();
