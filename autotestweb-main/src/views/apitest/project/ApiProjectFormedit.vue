<template >
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="relus" label-width="120px" class="demo-rulefForm" status-icon>
        <el-form-item label="项目编号" prop="id">
        <el-input v-model="ruleForm.id" disabled></el-input>
      </el-form-item>
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
  
  <script setup>
  import { ref, reactive } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { queryById, uptateData } from "./ApiProject.js";
  import { ElMessage } from "element-plus";
//   获取传进来的路由参数
const route = useRoute()
// 转发的路由
const router = useRouter();
  // 表单数据
const ruleForm = reactive({
    id: "",
    project_name: "",
    project_desc: ""
  });

  // 获取表单数据
  const getqueryById = () =>{
    const id  = route.query.id
    queryById(id).then((res)=>{
        ruleForm.id = res.data.data.id
        ruleForm.project_name = res.data.data.project_name
        ruleForm.project_desc = res.data.data.project_desc
    })
  }
  //   加载表单数据
getqueryById()
//   提交表单
  const submitForm = () => {
    uptateData(ruleForm).then((res) => {
      ElMessage.success("修改成功");
      const currentPage  = route.query.currentPage
      console.log('收到的是',currentPage)
      closeForm(currentPage);
    }).catch((err) => {
      ElMessage.error("修改失败");
      console.error("编辑失败:", err);
    });
  };
  
//   // 重置表单
  const resetForm = () => {
    ruleForm.project_name = "";
    ruleForm.project_desc = "";
  };
  
//   // 关闭表单
const closeForm = (currentPage) =>{
    console.log('关闭收到的是',currentPage)
    router.push({
        path:"/ApiProjectList",
        query:{currentPage:currentPage}

    })
}


  </script>
  
  <style scoped>
  </style>    