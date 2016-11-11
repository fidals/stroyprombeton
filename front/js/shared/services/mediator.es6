/**
 * We implements mediator pattern via jQuery's global events
 * on empty object (it could be a window or a document also).
 */
const mediator = {
  // Inner object, which used to bind and trigger events on it.
  M: {},

  /**
   * Subscribe given collection of handlers to an event with a given name.
   *
   * @param {string} eventName
   * @param handlers
   */
  subscribe: (eventName, ...handlers) => {
    for (const handler of handlers) {
      $(mediator.M).bind(eventName, handler);
    }
  },

  /**
   * Publish event with a given name, pass context to it's subscribers.
   *
   * @param eventName
   * @param context
   */
  publish: (eventName, context) => {
    $(mediator.M).trigger(eventName, context);
  },
};
