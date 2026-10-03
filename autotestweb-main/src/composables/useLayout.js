import { ref } from "vue";

const isCollapse = ref(false);

export function useLayout() {
  const toggleCollapse = () => {
    isCollapse.value = !isCollapse.value;
  };

  return {
    isCollapse,
    toggleCollapse,
  };
}
