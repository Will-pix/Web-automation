<template>
    <!-- 输入的表单 -->
    <el-form ref = "ruleFormRef" :model="apicollection" class="demo-ruleForm" :rules="rules" label-width="120px">
        <el-form-item label="所属项目" prop="id">
            <el-select v-model="apicollection.project_id" placeholder="选择所属项目">
                <el-option v-for="project in projectlist" :key="project.id" :label="project.project_name" :value="project.id"></el-option>
            </el-select>
        </el-form-item>
        <el-form-item label="集合名称" prop="collection_name">
            <el-input v-model="apicollection.collection_name" placeholder="输入集合名称"></el-input>
        </el-form-item>
        <el-form-item label="集合描述" prop="collection_desc">
            <el-input v-model="apicollection.collection_desc" placeholder="输入集合描述"></el-input>
        </el-form-item>
        <el-form-item label="运行环境数据" prop="collection_env">
            <el-input v-model="apicollection.collection_env" :rows="2" type="textarea" placeholder='输入环境变量json格式{"key1":"value1","key2":"value2"}'></el-input>
        </el-form-item>
        <el-form-item label="参数化运行" prop="collection_params">
            <el-input v-model="apicollection.collection_params" :rows="2" type="textarea" placeholder='输入ddt参数化json格式[{"key1":"value1","key2":"value2"}]'></el-input>
        </el-form-item>
        <!-- 用例关联 -->
         <el-form-item label="用例关联">
            <!-- 表格 -->
             <el-table :data="apiCaseList" style="width:100%">
                <el-table-column prop="run_order" label="顺序" style="width: 5%;"></el-table-column>
                <el-table-column prop="api_name" label="接口名称" style="width: 40%;" show-overflow-tooltip="true"></el-table-column>
                <el-table-column prop="request_url" label="请求地址" style="width: 40%;"show-overflow-tooltip="true"></el-table-column>
                <el-table-column prop="debug_vars" label="变量依赖" style="width: 40%;"show-overflow-tooltip="true"></el-table-column>
                <el-table-column fixed="right" label="操作" style="width: 15%;">
                    <template #default="scope">
                        <el-button link type="primary" size="small" @click.prevent="editCaseParamData(scope.$index)">运行参数配置</el-button>
                        <el-button link type="primary" size="small" @click.prevent="deleteApiCases(scope.$index)">删除</el-button>
                    </template>
                </el-table-column>

             </el-table>
             <!-- 分页 -->
             <el-pagination style="width: 70%;" small background layout="prev, pager, next, total" :page-size="apiCasePageSize"
             :total="apiCaseTotal" class="mt-4" v-model:current-page="currentApiCasePage"
             @current-change="handleApiCaseCurrentChange">
            </el-pagination>
            <!-- 底部按钮 -->
            <el-button @click="showApiInfosDialog">添加用例</el-button>
            <el-button type="primary" @click="submitForm(ruleFormRef)">保存退出</el-button>
            <el-button @click="closeForm()">关闭</el-button>
         </el-form-item>
    </el-form>
    <!-- 运行配置弹窗 -->
     <el-dialog v-model="paramDialogVisble" title="运行参数配置">
        <el-form-item label="运行顺序" prop="caseRunOrder">
            <el-input v-model="caseRunOrder"></el-input>
        </el-form-item>
        <el-form-item label="运行参数" prop="caseParamData">
            <el-input v-model="caseParamData" :rows="20" type="textarea" placeholder='输入运行参数化json格式,当使用参数化时不会执行单接口的后置处理[
    {
        "desc": "测试用例 1 的描述",
        "id": "1",
        "assertions":[{
                    "type": "断言类型(equals,contains,exists)",
                    "target": "断言路径(status_code,headers.Content-Type,$.data.field1)",
                    "expected": "预期值"
                }]
        "extractions"[{"var_name":"提取到全局变量的名称", "target": "$.data.提取路径"}]
    },
    {
        "desc": "测试用例 2 的描述",
        "id": "3"
    }
]'></el-input>
        </el-form-item>
            <!-- #footer 可以规范添加的按钮布局和样式，说白了就是加了就是样式效果 -->
            <template #footer>
                <span class="dialog-footer">
                    <el-button type="primary" @click="addddt">增加一组参数</el-button>
                    <el-button @click="paramDialogVisble=false">取消</el-button>
                    <el-button type="primary" @click="handlerCaseParamDataChange">确定</el-button>

                </span>
            </template>
     </el-dialog>
     <!-- 添加用例弹窗 -->
    <el-dialog v-model="infoDialogFormVisble" title="添加接口">
        <el-form-item>
            <!-- 用例搜索部分 -->
            <el-row class="mb-4" type="flex" justify="end">
                <el-select style="width: 240px; margin-right: 10px" v-model="searchForm.project_id" placeholder="项目" @change="projectChange" clearable>
                    <el-option v-for="project in projectlist" :key="project.id" :label="project.project_name" :value="project.id"></el-option>
                </el-select>
                <el-select style="width: 240px; margin-right: 10px" v-model="searchForm.module_id" placeholder="模块" clearable>
                    <el-option v-for="module_info in moduleList" :key="module_info.id" :label="module_info.module_name" :value="module_info.id"></el-option>
                </el-select>
                <el-button type="primary" @click="loadApiInfos()">查询</el-button>
            </el-row>
            <!-- 用例表格数据 -->
             <el-table :data="apiInfoList" style="width: 100%;">
                <el-table-column prop="id" label="用例编号" style="width: 5%;"></el-table-column>
                <el-table-column prop="api_name" label="接口名称" style="width: 30%;"show-overflow-tooltip="true"></el-table-column>
                <el-table-column prop="request_url" label="接口url" style="width: 60%;"show-overflow-tooltip="true"></el-table-column>
                <el-table-column fixed="right" label="操作" style="width: 5%;">
                    <template #default="scope">
                        <el-button type="primary" size="small" @click.prevent="addApiInfo(scope.$index)">添加</el-button>
                    </template>
                </el-table-column>
             </el-table>
        </el-form-item>
        <!-- 添加用例的分页 -->
        <el-pagination  :page-size="apiInfoPageSize"
             :total="apiInfoTotal" :current-page="currentApiInfoPage"
             @current-change="handleApiInfoCurrentChange">
            </el-pagination>
    </el-dialog>
</template>



<script setup>
import {ref,reactive} from "vue"
import {useRouter,useRoute} from "vue-router"
import { ElMessage } from "element-plus";
import { queryAll } from "../project/ApiProject.js"
import {insertData,queryById,updateData} from "~/views/apitest/collection/ApiCollection.js"
import {queryByPage,deleteData} from "./ApiCase.js"
import { watch } from 'vue';
// 要获取的路由
const route = useRoute()
// 要发送的路由
const router = useRouter()
// ==============↓新建编辑的表单js
// 表单总数据
const apicollection  = reactive({
    id:0,
    project_id:'',
    collection_name:'',
    collection_desc:'',
    collection_env:'',
    collection_params:''
})
// 表单实例
const ruleFormRef = ref()
// 表单的验证规则
const rules = reactive({
    project_id:[{required:true, message:"必填项",trigger:"blur"}],
    collection_name:[{required:true,message:"必填项",trigger:"blur"}],
    collection_desc:[{required:true,message:"必填项",trigger:"blur"}]
})
// 提交保存页面数据-不包含用例
const submitForm = ()=>{
    // 效验表单-?防止挂载失败情况
    ruleFormRef.value?.validate((valid)=>{
        if(!valid){
            // ElMessage.success("新增成功");
            ElMessage.error("新增失败");
            return false
        }
        // 判断是新增还是修改
        if(apicollection.id>0){
            updateData(apicollection).then((res)=>{
                ElMessage.success("修改成功");
                closeForm()
            }).catch((err)=>{
                ElMessage.error("修改失败");
                console.error("修改失败",err)
            })
        }else{
            insertData(apicollection).then((res)=>{
                ElMessage.success("新增成功");
                closeForm()
            }).catch((err)=>{
                ElMessage.error("新增失败");
                console.error("新增失败",err)
            })
        }
    })
}
// 项目的列表数据
const projectlist = ref([])
// 请求获取项目下拉框筛选的数据
function getProjectList(){
    queryAll().then((res)=>{
        projectlist.value = res.data.data
    })
}
// 初始化获取项目所需的列表数据
getProjectList()
// --------------一以下为编辑时加载数据
// 加载表单数据-编辑执行
const loadData = () =>{
    const id = route.query.id
    console.log("接收到的是",id)
    queryById(id).then((res)=>{
        apicollection.id = res.data.data.id,
        apicollection.project_id = res.data.data.project_id,
        apicollection.collection_name = res.data.data.collection_name,
        apicollection.collection_desc = res.data.data.collection_desc,
        apicollection.collection_env = res.data.data.collection_env,
        apicollection.collection_params = res.data.data.collection_params
    })}
// 初始化数据-如果是编辑则执行
console.log("新增还是修改,有值则修改",route.query.id)
const queryid = route.query.id
if (queryid > 0){
    loadData()
}
// 用例关联数据-用例关联区域
const apiCaseList = ref([])
// 加载用例区域数据
const loadApiCases = () => {
    // 构造请求参数-测试集id+分页数据，回显分页总数和用例区域数据
    let searchData = {
        "collection_id":apicollection.id,
        "page":currentApiCasePage.value,
        "PageSize":apiInfoPageSize.value
    }
    queryByPage(searchData).then((res)=>{
        apiCaseList.value = res.data.data;
        apiCaseList.value.sort((a, b) => a.run_order - b.run_order);
        console.log("此时的apiCaseList的数据为:",apiCaseList.value)
        apiCaseTotal.value = res.data.total
        console.log("此时的apiCaseToal的数据为:",apiCaseTotal.value)

    })
}
// 初始化用例数据-监听测试集id发生变动后执行
watch(()=> apicollection.id, (newId) =>{
    if (newId > 0){
        console.log("执行初始化用例数据")
        loadApiCases()
    }
}) 
// 关闭新建/编辑表单
const closeForm = () =>{
    router.push({
        path:"/ApiCollectionList"
    })
}
// 添加用例弹窗变量
const infoDialogFormVisble = ref(false)
// 打开添加用例方法弹窗-点击时判断此测试集是否保存
const showApiInfosDialog = () =>{
    // 调用获取弹窗用例的方法
    if (apicollection.id == 0){
        ElMessage.warning('当前为新建集合，需先保存后才能关联用例');
    }else{
        infoDialogFormVisble.value = true
    }
}
// 删除用例
const deleteApiCases = (index) =>{
    deleteData(apiCaseList.value[index].id).then((res)=>{
        ElMessage.success("删除成功");
        loadApiCases()
    })
}
// 打开运行参数的方法弹窗-并赋值-同步获取当前打开的索引值保存
const editCaseParamData = (index) =>{
    currentApiCaseIndex.value = index
    caseRunOrder.value = apiCaseList.value[index].run_order
    caseParamData.value = apiCaseList.value[index].param_data
    paramDialogVisble.value = true
}
// 外层-分页数据
const apiCasePageSize = ref(5)   //每页的数据
const apiCaseTotal = ref(0)   //总数
const currentApiCasePage  = ref(1) //页码
// 翻页
const handleApiCaseCurrentChange = (val) => {
    currentApiCasePage.value = val
    loadApiCases()
}
// ==============↑新建编辑的表单js
// ==============↓用例弹窗的内容
// 接口弹窗的主数据
const apiInfoList = ref([])
// 项目筛选的监听方法
const projectChange = (value) => {
    // 清空模块
    searchForm.module_id = ''
    // 获取模块
    getmodulelist()
}
// 模块的数据列表
const moduleList = ref([])
// 获取模块数据
import {queryByPage as apiModuleQuery} from "~/views/apitest/module/ApiModule.js"
const getmodulelist = () => {
    apiModuleQuery({
        "project_id":searchForm.project_id,
        "page":1,
        "pageSize":9999999
    }).then((res)=>{
        moduleList.value = res.data.data
        console.log("获取的模块列表为",moduleList.value )
    })
}
// 加载接口用例数据
import {queryByPage as queryApiInfoByPage} from "~/views/apitest/apiinfo/ApiInfo.js"
// 根据筛选内容查找接口数据
const loadApiInfos = () =>{
    let searchData = searchForm
    searchData["page"] = currentApiInfoPage.value,
    searchData["pageSize"] = apiInfoPageSize.value,
    queryApiInfoByPage(searchData).then((res)=>{
        apiInfoList.value = res.data.data
        apiInfoTotal.value = res.data.total
    })
}
import {insertData as insertApiCase} from "./ApiCase.js"
//接口数据添加进测试集
const addApiInfo = (index) =>{
    console.log("添加测试的index",index)
    // 构造插入参数
    let casedata = {
        "collection_id":apicollection.id,
        "api_info_id":apiInfoList.value[index].id,
        "run_order":0
    }
    insertApiCase(casedata).then((res)=>{
        if (res.data.code==200){
            ElMessage.success("添加成功");
            loadApiCases()
        }else{
            ElMessage.error("添加失败");
        }
    })
}
// 弹窗-筛选的双向绑定数据
const searchForm = reactive({
    project_id: '',
    module_id: ''
});
// 分页数据
const currentApiInfoPage = ref(1) // 页码
const apiInfoPageSize = ref(10) //每页数据数量
const apiInfoTotal = ref(0)   //总数据
// 翻页
const handleApiInfoCurrentChange = (val) =>{
    currentApiInfoPage.value = val
    loadApiInfos()
}
// ==============↑用例弹窗的内容
// ==============↓运行参数弹窗的内容
import {updateData as updateApiCasecol} from "~/views/apitest/collection/ApiCase.js"
// 运行配置参数的索引定位
const currentApiCaseIndex =ref(-1)
// 运行配置参数控制弹窗
const paramDialogVisble = ref(false)
// 顺序
const caseRunOrder = ref(0)
// 运行参数的提交-修改-通过传递中间表id，参数配置，顺序保存
const handlerCaseParamDataChange = () =>{
    // 构造请求参数-通过打开弹窗的索引值，获取对应的中间表id
    updateApiCasecol({
        "id":apiCaseList.value[currentApiCaseIndex.value].id,
        "param_data": caseParamData.value,
        "run_order":caseRunOrder.value
    }).then((res)=>{
        if(res.data.code==200){
            // 更新apicaselist的值-通过打开弹窗的索引获取apilist对应的数据
            // apiCaseList.value[currentApiCaseIndex.value].param_data = caseParamData.value
            // apiCaseList.value[currentApiCaseIndex.value].run_order = caseRunOrder.value
            loadApiCases()
            ElMessage.success("修改成功");
            paramDialogVisble.value = false
        }
    })
}
// 参数
const caseParamData = ref('[]')
// 增加参数
const addddt = () => {
    let code = `{
        "desc": "",
        "assertions": [{"type": "", "target": "", "expected": ""}],
        "extractions": [{"var_name": "", "target": ""}]
    }`;
    if (caseParamData.value === null || caseParamData.value === undefined) {
        caseParamData.value = '[]';
    }
    let currentData = caseParamData.value.slice(1, -1);
    if (currentData.trim() === '') {
        caseParamData.value = `[${code}]`;
    } else {
        caseParamData.value = `[${currentData}, ${code}]`;
    }
};
// ==============↑运行参数弹窗的内容
</script>