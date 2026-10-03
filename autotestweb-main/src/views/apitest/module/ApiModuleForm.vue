<template>
    <el-form ref="ruleFormRef" :model="ruleForm"  label-width="120px" class="demo-ruleForm"
    status-icon>
    <el-form-item label="所属项目ID" prop="project_id">
    <el-select  v-model="ruleForm.project_id" placeholder="Select" >
      <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"/>     
    </el-select>
  </el-form-item>
    <el-form-item label="模块名称" prop="module_name">
      <el-input v-model="ruleForm.module_name" />
    </el-form-item>
    <el-form-item label="模块介绍" prop="module_desc">
      <el-input v-model="ruleForm.module_desc" />
    </el-form-item>
    <!-- END 表单字段 -->
    <!-- 表单操作 -->
    <el-form-item>
      <el-button type="primary" @click="submitForm">
        提交
      </el-button>
      <el-button @click="resetForm">清空</el-button>
      <el-button @click="closeForm">关闭</el-button>
    </el-form-item>
    </el-form>
</template>
<script setup>
import{ref,reactive} from "vue"
import { queryAll } from "../project/ApiProject.js"
import { insertData } from "../module/ApiModule.js"
import { ElMessage } from "element-plus";
import {useRouter,useRoute} from "vue-router"
// 定义router实例-转出
const router = useRouter()
// 表单的数据
const ruleForm = reactive({
    project_id:'',
    module_name:'',
    module_desc:''
})
// 下拉框筛选的展示数据
const projectList = ref([])
// 请求获取下拉框这哪是的数据
function getProjectList(){
    queryAll().then((res)=>{
        console.log(res.data)
        projectList.value = res.data.data
    })
}
// 每次进入页面获取项目列表
getProjectList()
// 点击提交的保存
const submitForm = () =>{
    insertData(ruleForm).then((res)=>{
      if(res.data.code===200){
        ElMessage.success("新增成功");
    // 关闭表单
    closeForm()
      }else{
        ElMessage.error(res.data.msg);

      }
    }).catch((err)=>{
    ElMessage.error("新增失败");
    console.error("新增失败",err)
    })
}
// 关闭表单
const closeForm = () =>{
    router.push({
        path:"/ApiModuleList"
    })
}
// 清空表单
const resetForm = () =>{
    ruleForm.project_id = "",
    ruleForm.module_name = "",
    ruleForm.module_desc = ""
}

</script>