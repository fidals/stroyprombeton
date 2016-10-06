(() => {
  const DOM = {
    $addToCart: $('.js-add-basket'),
    $counter: $('.js-product-count'),
    $sliderContent: $('.js-slider-content'),
    $sliderNavLeft: $('.js-slider-nav-left'),
    $sliderNavRight: $('.js-slider-nav-right'),
    $sliderItem: $('.js-slider-item'),
  };

  const slider = {
    itemsToSlide: 3,
    position: 0,
    animationSpeed: 600,
    disabledClass: 'slider-nav-disable',
    itemsCount: DOM.$sliderItem.length,
    itemsWidth: DOM.$sliderItem.eq(0).outerWidth(true),
  };

  const productId = () => DOM.$addToCart.attr('product-id');

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    DOM.$addToCart.click(buyProduct);
    DOM.$sliderNavLeft.click(slideLeft);
    DOM.$sliderNavRight.click(slideRight);
  }

  function buyProduct() {
    const { id, count } = {
      id: productId(),
      count: DOM.$counter.val(),
    };

    server.addToCart(id, count)
      .then(data => mediator.publish('onCartUpdate', data));
  }

  const isDisabled = $sliderBtn => $sliderBtn.hasClass(slider.disabledClass);

  function slideLeft() {
    if (isDisabled(DOM.$sliderNavLeft)) return;

    if (slider.position <= slider.itemsToSlide) {
      slider.position = 0;
      DOM.$sliderNavLeft.addClass(slider.disabledClass);
    } else {
      slider.position -= slider.itemsToSlide;
    }

    sliderMove();
    DOM.$sliderNavRight.removeClass(slider.disabledClass);
  }

  function slideRight() {
    if (isDisabled(DOM.$sliderNavRight)) return;

    let imagesRightSide = slider.itemsCount - slider.position - slider.itemsToSlide;

    if (imagesRightSide > slider.itemsToSlide) {
      imagesRightSide = slider.itemsToSlide;
    } else {
      DOM.$sliderNavRight.addClass(slider.disabledClass);
    }

    slider.position += imagesRightSide;
    sliderMove();
    DOM.$sliderNavLeft.removeClass(slider.disabledClass);
  }

  function sliderMove() {
    const left = slider.position * -slider.itemsWidth;

    DOM.$sliderContent.stop().animate({ left }, slider.animationSpeed);
  }

  init();
})();
