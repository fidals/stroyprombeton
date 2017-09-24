const autocomplete = (() => {  // Ignore ESLintBear (no-unused-vars)
  const config = {
    url: '/search/autocomplete/',
    searchInput: '.js-search-field',
    minChars: 2,
    itemsTypes: ['see_all', 'category', 'product'],
  };

  /**
   * Configs for autoComplete library.
   * @link http://goo.gl/haZzhv
   */
  const isInclude = value => ['category', 'product'].includes(value);

  const autoCompleteConfig = {
    selector: config.searchInput,
    minChars: config.minChars,
    source(term, response) {
      $.getJSON(config.url, { term }, (namesArray) => {
        response(namesArray);
      });
    },
    renderItem(item, term) {
      return isInclude(item.type) ? renderItem(item, term) : renderShowMoreItem(item);
    },
    onSelect(event, _, item) {
      const isRightClick = () => event.button === 2 || event.which === 3;
      if (isRightClick(event)) return;

      window.location = $(item).find('a').attr('href');
    },
  };

  const init = () => {
    new autoComplete(autoCompleteConfig);  // Ignore ESLintBear (new-cap)
  };

  /**
   * Highlight term in autocompleted search results.
   *
   * @link http://goo.gl/WPpCVj
   * @param name
   * @param search
   * @return string
   */
  const highlight = (name, search) => {
    const preparedSearch = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');  // Ignore ESLintBear (no-useless-escape)
    const regexp = new RegExp(`(${preparedSearch.split(' ').join('|')})`, 'gi');

    return name.replace(regexp, '<b>$1</b>');
  };

  function renderItem(item, term) {
    const context = {
      url: item.url,
      name: `<span class="search-item-text">${highlight(item.name, term)}</span>`,
      mark: item.mark ?
        `<span class="search-item-mark">${highlight(item.mark, term)}</span>` : '',
      specification: item.specification ?
        `<span class="search-item-spec">${highlight(item.specification, term)}</span>` : '',
      itemName: item.name,
    };

    // Do not change string template here cause of issue.
    // https://github.com/Pixabay/JavaScript-autoComplete/issues/39
    return `<div class="autocomplete-suggestion search-item" data-val="${context.itemName}">
      <a href="${context.url}" class="search-item-link">
        ${context.name}${context.mark} ${context.specification}
      </a>
    </div>`;
  }

  function renderShowMoreItem(item) {
    // Do not change string template here cause of issue.
    // https://github.com/Pixabay/JavaScript-autoComplete/issues/39
    return `<div class="search-item">
      <a href="${item.url}" class="search-more-link more-link">
        ${item.name}
        <i class="fa fa-arrow-right more-link-arrow" aria-hidden="true"></i>
      </a>
    </div>`;
  }

  init();

  return {
    init,
  };
})();
