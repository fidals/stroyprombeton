/**
 * Category Page module defines logic, operations and DOM for CategoryPage.
 */
(() => {
  const DOM = {
    $filterItem: $('.js-category-filter-item'),
    $filterCheckAll: $('.js-category-filter-item-all'),
    $filterClear: $('.js-category-filter-clear'),
    tableColCountInput: '.js-category-table-col-count-input',
    tableColCountUp: '.js-category-table-col-count-up',
    tableColCountDown: '.js-category-table-col-count-down',
    filterItemIco: '.category-filter-item-ico',
    $filterItemIco: $('.category-filter-item-ico'),
    // old ones:
    $addToCart: $('.js-category-buy'),
    productRow: '.js-product-row',
    counter: '.js-product-count',
  };

  const init = () => {
    setUpListeners();
  };

  /**
   * Subscribing on events using mediator.
   */
  const setUpListeners = () => {
    DOM.$addToCart.click((event) => buyProduct(event));

    $(document)
      .on('click', DOM.tableColCountUp, function () {
        countIncrease($(this).siblings(DOM.tableColCountInput));
      })
      .on('click', DOM.tableColCountDown, function () {
        countDecrease($(this).siblings(DOM.tableColCountInput));
      });

    DOM.$filterItem.click(function () {
      filterItemToggle($(this).find(DOM.filterItemIco));
    });

    DOM.$filterCheckAll.click(filterCheckAll);

    DOM.$filterClear.click(filterClear);
  };

  const buyProduct = event => {
    const buyInfo = () => {
      const product = $(event.target);
      const count = product.closest(DOM.productRow).find(DOM.counter).val();
      return {
        count: parseInt(count),
        id: parseInt(product.attr('productId')),
      };
    };

    const { id, count } = buyInfo(event);
    server.addToCart(id, count).then(data => mediator.publish('onCartUpdate', data));
  };

  const countIncrease = $input => {
    $input.val((i, val) => ++val);
  };

  const countDecrease = $input => {
    $input.val((i, val) => (val > 1) ? --val : val);
  };

  const filterItemToggle = $ico => {
    $ico.toggleClass('fa-square-o fa-check-square-o');
    DOM.$filterCheckAll.find(DOM.filterItemIco)
      .addClass('fa-square-o')
      .removeClass('fa-check-square-o');
  };

  const filterCheckAll = () => {
    DOM.$filterItemIco
      .addClass('fa-check-square-o')
      .removeClass('fa-square-o');
  };

  const filterClear = () => {
    DOM.$filterItemIco
      .addClass('fa-square-o')
      .removeClass('fa-check-square-o');
  };

  init();
})();
