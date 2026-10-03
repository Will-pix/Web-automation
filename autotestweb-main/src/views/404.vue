<template>
      <el-result
        icon="warning"
        title="404页面"
        sub-title="页面不见了"
      >
        <template #extra>
          <el-button type="primary" @click="$router.push('/')">回到首页</el-button>
        </template>
      </el-result>
</template>