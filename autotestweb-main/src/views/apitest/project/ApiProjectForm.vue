<template >
  <el-form ref="ruleFormRef" :model="ruleForm" :rules="relus" label-width="120px" class="demo-rulefForm" status-icon>
    <el-form-item label="项目名称" prop="project_name">
      <el-input v-model="ruleForm.project_name"></el-input>
    </el-form-item>
    <el-form-item label="项目描述" prop="project_desc">
      <el-input v-model="ruleForm.project_desc"></el-input>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="submitForm()"
        >提交</el-button>
      <el-button @click="resetForm">清空</el-button>
      <el-button @click="closeForm">关闭</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { queryById, insertData, uptateData } from "./ApiProject.js";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
// 定义router实例
const router = useRouter()
// 表单数据
const ruleForm = reactive({
  project_name: "",
  project_desc: ""
});
// 提交表单
const submitForm = () =>{
    // 调用新增api
    insertData(ruleForm).then((res)=>{
        ElMessage.success("新增成功");
        // 关闭表单
        closeForm()
    }).catch((err)=>{
        ElMessage.error("新增失败");
        console.error("新增失败",err)
    })
}
// 关闭表单
const closeForm = () =>{
    router.push({
        path:"/ApiProjectList"
    })
}
// 清空表单
const resetForm = () =>{
    ruleForm.project_name = "",
    ruleForm.project_desc = ""
}

</script>