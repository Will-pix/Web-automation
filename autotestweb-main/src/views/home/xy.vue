<template>
  <el-row class="click-highlight-container h-screen" @click="handleClick">
    <slot></slot>
    
    <!-- 高亮圆点 -->
    <div 
      v-if="showDot" 
      class="highlight-dot" 
      :style="{ left: x + 'px', top: y + 'px' }"
    ></div>
  </el-row>
</template>

<script setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus'; // 引入 Message 组件

const showDot = ref(false);
const x = ref(0);
const y = ref(0);

const handleClick = (e) => {
  // 获取相对于容器的坐标
  x.value = e.offsetX;
  y.value = e.offsetY;
  
  // 显示高亮圆点
  showDot.value = true;
  
  // 使用 Element UI 的 Message 显示坐标
  ElMessage({
    message: `点击坐标：X=${x.value}, Y=${y.value}`,
    type: 'info',
    duration: 3000, // 3秒后自动消失
  });

  // 3秒后隐藏圆点
  setTimeout(() => {
    showDot.value = false;
  }, 3000);
};
</script>

<style scoped>
.click-highlight-container {
  @apply relative m-0 p-0 overflow-hidden;
}

.highlight-dot {
  @apply absolute w-4 h-4 bg-red-500 rounded-full transform -translate-x-1/2 -translate-y-1/2 
         shadow-[0_0_10px_2px_rgba(255,0,0,0.8)] pointer-events-none z-50;
}
</style>