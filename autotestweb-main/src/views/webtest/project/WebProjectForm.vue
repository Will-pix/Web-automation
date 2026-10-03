<template>
    <el-form :model="ruleForm" ref="ruleFormRef" :rules="rules" label-width="120px" >
        <el-form-item label="项目编号" prop="id">
            <el-input v-model="ruleForm.id" disabled></el-input>
        </el-form-item>
        <el-form-item label="项目名称" prop="project_name">
            <el-input v-model="ruleForm.project_name" placeholder="请输入项目名称"></el-input>
        </el-form-item>
        <el-form-item label="项目描述" prop="project_desc">
            <el-input v-model="ruleForm.project_desc" placeholder="请输入项目描述"></el-input>
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="submitForm()">提交</el-button>
            <el-button @click="reserForm">清空</el-button>
            <el-button @click="closeForm">关闭</el-button>
        </el-form-item>
    </el-form>
</template>

<script setup>
import {ref, reactive} from 'vue'
import { ElMessage } from "element-plus";
import {useRouter,useRoute} from "vue-router"
import {queryById,uptateData,insertData} from '~/views/webtest/project/WebProject.js'

// 要接收的
const route = useRoute()
// 编辑加载数据
const loadData = () =>{
    const id = route.query.id
    queryById(id).then((res)=>{
        ruleForm.id = res.data.data.id
        ruleForm.project_name = res.data.data.project_name
        ruleForm.project_desc = res.data.data.project_desc
    })
}
const query_id = route.query.id
if(query_id>0){
    loadData()
}
// 要发送的
const router = useRouter()
// 表单数据
const ruleForm = reactive({
    id:0,
    project_name:'',
    project_desc:''
})
// 表单实例
const ruleFormRef = ref()
// 表单验证规则
const rules = reactive({
    project_name:[
        {required:true, message:'必填项', trigger:'blur'}
    ],
    project_desc:[
        {required:true, message:'必填项', trigger:'blur'}
    ]
})
// 清空表单数据
const reserForm = () =>{
    ruleForm.project_name = '',
    ruleForm.project_desc =''
}
// 关闭
const closeForm = () =>{
    router.push({
        path:'/WebProjectList'
    })
}
// 提交
const submitForm=()=>{
    if(ruleFormRef.value){
        ruleFormRef.value.validate((valid)=>{
            if(valid){
                if(ruleForm.id>0){
                    // 编辑
                    uptateData(ruleForm).then((res)=>{
                        if(res.data.code===200){
                            ElMessage.success("修改成功")
                            router.push({
                              path:'/WebProjectList'
                            })
                        }else{
                            ElMessage.error("修改失败")
                        }
                    })
                }else{
                    // 新增
                    insertData(ruleForm).then((res)=>{
                        if(res.data.code==200){
                            ElMessage.success("创建成功")
                            router.push({
                              path:'/WebProjectList'
                            })
                        }else{
                            ElMessage.error("创建失败")
                        }
                    })
                }
            }
        })
    }
}
</script>