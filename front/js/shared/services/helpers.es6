const helpers = (() => {  // Ignore ESLintBear (no-unused-vars)
  const config = {
    regexpPhone: /(\+\d\s|\+\d)\(?\d{3}(\)|\)\s)?-?\d{1}-?\d{1}-?(\d{1}|\d{1}\s)-?\d{1}-?(\d{1}|\d{1}\s)-?\d{1}-?\d{1}/g,
    regexpEmail: /^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,}$/,
  };

  /**
   * Return boolean result of phone number validation.
   * Phone number should consist of 11 numbers. Number could have whitespaces.
   *
   * @param {string} data
   */
  const isPhoneValid = data => data && !!data.match(config.regexpPhone);

  /**
   * Return boolean result of email validation.
   *
   * @param {string} data
   */
  const isEmailValid = data => !!data.toLowerCase().match(config.regexpEmail);

  /**
   * Delays `fn` execution for better UI and AJAX request performance.
   *
   * @param {function} fn
   * @param {number} delay
   */
  function debounce(fn, delay) {
    let timerId;
    return function delayed(...args) {
      clearTimeout(timerId);
      timerId = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  return {
    debounce,
    isPhoneValid,
    isEmailValid,
  };
})();
