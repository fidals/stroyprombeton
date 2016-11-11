{
  const init = () => {
    pasteSearchTerm();
  };

  /**
   * Paste entered user search term in search field.
   */
  function pasteSearchTerm() {
    if (location.pathname !== '/search/') return;

    const searchTerm = decodeURI(location.href).split('?term=')[1];
    $('.js-search-field').val(searchTerm);
  }

  init();
}
