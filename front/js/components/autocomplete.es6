const autocomplete = (() => {
  const CONFIG = {
    url: '/search/autocomplete/',
    searchInput: '.search-input',
    minChars: 2,
    itemsTypes: ['see_all', 'category', 'product'],
  };

  const init = () => {
    new autoComplete(constructorArgs);
  };

  /**
   * Highlight term in search results
   * Behind the scenes JavaScript autoComplete lib use this highlight code
   * Proof link: https://goodies.pixabay.com/javascript/auto-complete/demo.html
   *
   * @param name
   * @param search
   * @returns string
   */
  const highlight = (name, search) => {
    const preparedSearch = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    const regexp = new RegExp(`(${preparedSearch.split(' ').join('|')})`, 'gi');
    return name.replace(regexp, '<b>$1</b>');
  };

  const renderItem = (item, term) => {
    const context = {
      url: item.url,
      name: `<span class="item-name">${highlight(item.name, term)}</span>`,
      price: item.price ? `<span class="item-price">${item.price} руб.</span>` : '',
      mark: item.mark ? `<span class="item-mark">${item.mark}</span>` : '',
      specification: item.specification ? `<span class="item-specification">${item.specification}</span>` : '',
      itemName: item.name,
    };

    return `
      <div class="autocomplete-suggestion" data-val="${context.itemName}">
        <a href="${context.url}" class="item-link">${context.specification}${context.name}${context.mark}${context.price}</a>
      </div>
    `;
  };

  const renderLastItem = item => {
    return `
      <div class="autocomplete-suggestion autocomplete-last-item">
        <a href="${item.url}" class="item-link">${item.name}</a>
      </div>
    `;
  };

  /**
   * Constructor args for autocomplete lib
   * https://goodies.pixabay.com/javascript/auto-complete/demo.html
   */

  const isInclude = value => -1 !== ['category', 'product'].indexOf(value)

  const constructorArgs = {
    selector: CONFIG.searchInput,
    minChars: CONFIG.minChars,
    source: (term, response) => {
      $.getJSON(CONFIG.url, {
        q: term,
      }, namesArray => {
        response(namesArray);
      });
    },
    renderItem: (item, term) => {

      if (isInclude(item.type)) {
        return renderItem(item, term);
      }
      if (item.type === 'see_all') {
        return renderLastItem(item);
      }
    },
    onSelect: (event, term, item) => {
      const isRightClick = event => event.button === 2 || event.which === 3;
      if (isRightClick(event)) return false;
      window.location = $(item).find('a').attr('href');
    },
  };

  init();
})();
