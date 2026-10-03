// event-bus.js
import { ref } from 'vue';

export const eventBus = ref({
  listeners: {},
  on(event, callback) {
    this.listeners[event] = this.listeners[event] || [];
    this.listeners[event].push(callback);
  },
  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  },
  off(event) {
    delete this.listeners[event];
  }
});