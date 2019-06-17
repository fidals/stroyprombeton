(() => {
  const DOM = {
    $addToCart: $('.js-buy-product'),
    counter: '.js-count-input',
    $productInfo: $('.js-product-info'),
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
    DOM.$addToCart.click(buy);
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
      id: parseInt(DOM.$productInfo.data('id'), 10),
      name: DOM.$productInfo.data('name'),
      category: DOM.$productInfo.data('category'),
    };
  }

  function getOptionData($addToCartButton) {
    const $countInput = $addToCartButton.parents('tr').find('.table-count-input');
    return {
      id: parseInt($addToCartButton.data('id'), 10),
      quantity: parseInt($countInput.val(), 10),
    };
  }

  function buy() {
    const $addToCartButton = $(this);
    const option = getOptionData($addToCartButton);
    const { id, quantity } = option;

    server.addToCart(id, quantity)
      .then((cart) => {
        mediator.publish('onCartUpdate', cart);
        mediator.publish('onProductAdd', [option]);
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
