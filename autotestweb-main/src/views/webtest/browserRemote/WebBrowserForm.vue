<template>
    <el-form :model="ruleForm" ref="ruleFormRef" :rules="rules" label-width="120px" >
        <el-form-item label="编号" prop="id">
            <el-input v-model="ruleForm.id" disabled></el-input>
        </el-form-item>
        <el-form-item label="浏览器名称" prop="name">
            <el-input v-model="ruleForm.name" placeholder="请输入浏览器名称"></el-input>
        </el-form-item>
        <el-form-item label="浏览器类型" prop="enName">
            <el-input v-model="ruleForm.enName" placeholder="请输入浏览器类型"></el-input>
        </el-form-item>
        <el-form-item label="所属项目" prop="project_id">
            <el-select  v-model="ruleForm.project_id" placeholder="选择所属项目" clearable  filterable >
                <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"/>
            </el-select>
        </el-form-item>
        <el-form-item label="远程地址" prop="remote_url">
            <el-input v-model="ruleForm.remote_url" placeholder="请输入Grid地址"></el-input>
        </el-form-item>
        <el-form-item label="驱动地址" prop="driver_path">
            <el-input v-model="ruleForm.driver_path" placeholder="请输入浏览器驱动地址"></el-input>
        </el-form-item>
        <el-form-item label="浏览器调试参数" prop="browser_debug">
            <el-input v-model="ruleForm.browser_debug" placeholder='浏览器配置参数，格式如下：(按需配置)&#10;{&#10;# 谷歌配置&#10;"goog:chromeOptions": {
		"args": [
			"--headless", # 无头隐藏模式
			"--user-data-dir=d:\\tttt" # 浏览器数据保存位置
		]
	},
  # 火狐配置
	"moz:firefoxOptions": {
		"args": [
			"--headless" # 无头隐藏模式
		]
	}
}' :rows="8" type="textarea"></el-input>
        </el-form-item>
        <el-form-item label="是否启动" prop="is_enabled">
            <el-radio-group v-model="ruleForm.is_enabled" class="ml-4">
                <el-radio value="1" xize=";arge">启动</el-radio>
                <el-radio value="0" xize=";arge">不启动</el-radio>
            </el-radio-group>
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
import {queryAll} from '~/views/webtest/project/WebProject.js'
import {queryById,uptateData,insertData} from '~/views/webtest/browserRemote/WebBrowser.js'

// 要接收的
const route = useRoute()
// 编辑加载数据
const loadData = () =>{
    const id = route.query.id
    queryById(id).then((res)=>{
        ruleForm.id = res.data.data.id
        ruleForm.name = res.data.data.name
        ruleForm.enName = res.data.data.enName
        ruleForm.project_id = res.data.data.project_id
        ruleForm.remote_url = res.data.data.remote_url
        ruleForm.driver_path = res.data.data.driver_path
        ruleForm.browser_debug = res.data.data.browser_debug
        ruleForm.is_enabled = res.data.data.is_enabled
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
    name:'',
    enName:'',
    project_id:'',
    remote_url:'',
    driver_path:'',
    browser_debug:'',
    is_enabled:'',
})
// 项目的列表
const projectList = ref()
// 获取项目列表
const getprojectList = () =>{
    queryAll().then((res)=>{
        console.log("获取的列表为",res.data.data)
        projectList.value = res.data.data
    })
}
getprojectList()
// 表单实例
const ruleFormRef = ref()
// 表单验证规则
const rules = reactive({
    name:[
        {required:true, message:'必填项', trigger:'blur'}
    ],
    enName:[
        {required:true, message:'必填项', trigger:'blur'}
    ],
    project_id:[
        {required:true, message:'必填项', trigger:'blur'}
    ],
    is_enabled:[
        {required:true, message:'必填项', trigger:'blur'}
    ]
})
// 清空表单数据
const reserForm = () =>{
    ruleForm.name = '',
    ruleForm.enName ='',
    ruleForm.project_id ='',
    ruleForm.remote_url ='',
    ruleForm.driver_path ='',
    ruleForm.browser_debug ='',
    ruleForm.is_enabled =''
}
// 关闭
const closeForm = () =>{
    router.push({
        path:'/WebBrowserList'
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
                              path:'/WebBrowserList'
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
                              path:'/WebBrowserList'
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