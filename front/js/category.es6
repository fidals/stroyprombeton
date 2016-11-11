{
  const DOM = {
    addToCart: 'js-category-buy',
    $cart: $('.js-cart'),
    $showMoreLink: $('#load-more-products'),
    $productsTable: $('#products-wrapper'),
    $searchFilter: $('#search-filter'),
  };

  const config = {
    fetchProductsUrl: '/fetch-products/',
    productsToFetch: 30,
    totalProductsCount: parseInt($('.js-total-products').first().text(), 10),
  };

  const init = () => {
    setLoadMoreLinkState();
    setUpListeners();
  };

  /**
   * Subscribing on events using mediator.
   */
  function setUpListeners() {
    mediator.subscribe('onCartUpdate', showTooltip);
    mediator.subscribe('onProductsFilter', updateLoadMoreLink, refreshProductsList);
    mediator.subscribe('onProductsLoad', updateLoadMoreLink, appendToProductsList);

    $(DOM.$productsTable).on('click', buyProduct);
    DOM.$showMoreLink.click(loadProducts);
    DOM.$searchFilter.keyup(filterProducts);
  }

  function setLoadMoreLinkState() {
    if ($('.table-tr').size() < config.productsToFetch) {
      DOM.$showMoreLink.addClass('disabled');
    }
  }

  /**
   * Get product quantity & id from DOM.
   */
  const getProductInfo = (event) => {
    const $product = $(event.target);
    const productCount = $product.closest('td').prev().find('.js-count-input').val();
    const productId = $product.closest('tr').attr('id');

    return {
      count: parseInt(productCount, 10),
      id: parseInt(productId, 10),
    };
  };

  /**
   * Add product to Cart and update it.
   */
  function buyProduct(event) {
    if (!$(event.target).hasClass(DOM.addToCart)) return;

    const { id, count } = getProductInfo(event);

    server.addToCart(id, count)
      .then(data => mediator.publish('onCartUpdate', { html: data, target: event.target }));
  }

  /**
   * Show tooltip after adding Product to the Cart.
   */
  function showTooltip(_, data) {
    const $target = $(data.target).closest('.table-td').find('.js-popover');

    $target.fadeIn();
    setTimeout(() => $target.fadeOut(), 1000);
  }

  /**
   * Get already loaded products count.
   */
  const getLoadedProducts = () => parseInt(DOM.$showMoreLink.attr('data-load-count'), 10);

  const getFilterTerm = () => DOM.$searchFilter.val();

  const getCategoryId = () => DOM.$searchFilter.attr('data-category');

  /**
   * Update products to load data attribute counter.
   * Add 'disabled' attribute to button if there are no more products to load.
   *
   * @param {string} products - HTML string of fetched products
   */
  function updateLoadMoreLink(_, products) {
    const oldCount = getLoadedProducts();
    const newCount = oldCount + config.productsToFetch;
    const productsLoaded = countWord(products, 'table-tr');

    DOM.$showMoreLink.attr('data-load-count', newCount);

    if (productsLoaded < config.productsToFetch) {
      DOM.$showMoreLink.addClass('disabled');
    }
  }

  /**
   * Update Products list in DOM via appending HTML-list of loaded products to wrapper.
   *
   * @param {string} products - HTML string of fetched product's list
   */
  function appendToProductsList(_, products) {
    DOM.$productsTable.append(products);
  }

  /**
   * Insert filtered Products list.
   *
   * @param {string} products - HTML string of fetched product's list
   */
  function refreshProductsList(_, products) {
    DOM.$productsTable.html(products);
  }

  /**
   * Count word occurrence in string.
   *
   * @param {string} source - string to search occurrence in
   * @param {string} word - searched word in whole string
   * @return {number} count - word occurrence count in source string
   */
  function countWord(source, word) {
    let count = 0;
    let index = 0;

    while ((index = source.indexOf(word)) >= 0) {
      source = source.substring(index + word.length);
      count += 1;
    }

    return count;
  }

  /**
   * Load more products from back-end with/without filtering.
   * After products successfully loaded - publishes 'onProductLoad' event.
   */
  function loadProducts() {
    if (DOM.$showMoreLink.hasClass('disabled')) return;

    const fetchData = {
      categoryId: getCategoryId(),
      offset: getLoadedProducts(),
      filterValue: getFilterTerm(),
      filtered: getFilterTerm().length > 0,
    };

    fetchProducts(fetchData)
      .then(
        (products) => {
          mediator.publish('onProductsLoad', products);
        },
        response => console.warn(response)
      );
  }

  /**
   * Load filtered products from back-end by filter term on typing in filter field.
   * After products successfully loaded - publishes 'onProductsFilter' event.
   * Number `3` is minimal length for search term.
   */
  function filterProducts() {
    helpers.delay(() => {
      const filterValue = getFilterTerm();
      if (filterValue.length > 0 && filterValue.length < 3) return;

      const fetchData = {
        categoryId: getCategoryId(),
        filterValue,
        filtered: filterValue.length >= 3,
      };

      fetchProducts(fetchData)
        .then(
          (products) => {
            mediator.publish('onProductsFilter', products);
            DOM.$showMoreLink.attr('data-load-count', config.productsToFetch);
          },
          response => console.warn(response)
        );
    }, 300);
  }

  /**
   * Load products from back-end by passed data.
   */
  function fetchProducts(fetchData) {
    return $.post(config.fetchProductsUrl, {
      categoryId: fetchData.categoryId,
      term: fetchData.filterValue,
      offset: fetchData.offset,
      filtered: fetchData.filtered,
    });
  }

  init();
}
