(() => {
  const DOM = {
    $addToCart: $('.js-buy-product'),
    counter: '.js-count-input',
    $slick: $('.js-slick'),
    slickItem: '.slick-slide',
  };

  const init = () => {
    pluginsInit();
    setUpListeners();
    // @todo #662:30m  Fix on product detail event publishing.
    //  Now it takes option details instead of product ones.

    // publishDetail();
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

  function getProductData($addToCartButton) {
    const id = parseInt($addToCartButton.data('id'), 10);
    const $countInput = $(`tr#option-${id} .table-count-input`);
    return {
      id,
      name: $addToCartButton.data('name'),
      category: $addToCartButton.data('category'),
      quantity: parseInt($countInput.attr('value'), 10),
    };
  }

  function buyProduct() {
    const $addToCartButton = $(this);
    const data = getProductData($addToCartButton);
    const { id, quantity } = data;

    server.addToCart(id, quantity)
      .then((newData) => {
        mediator.publish('onCartUpdate', newData);
        mediator.publish('onProductAdd', [data]);
      });
  }

  // function publishDetail() {
  //  const { id, name, category } = getProductData();
  //  if (id) {
  //    mediator.publish('onProductDetail', [{ id, name, category }]);
  //  }
  // }

  init();
})();
