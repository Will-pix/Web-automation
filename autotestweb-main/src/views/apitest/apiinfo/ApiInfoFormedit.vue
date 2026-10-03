<template>
    <!-- :inline="false"不进行行内布局，竖项布局el-col为横向布局 -->
    <el-form ref="searchFormRef" :inline="false" :model="ApiInfo" class="demo-for-inline" >
        <!-- 这部分是接口名称，项目及模块 -->
        <el-form-item>
            <el-col :span="18">
                <el-input v-model="ApiInfo.api_name" placeholder="输入接口名称" prop="api_name"></el-input>
            </el-col>
            <el-col :span="3">
                <!-- clearable是清空功能 -->
                <el-select v-model="ApiInfo.project_id" placeholder="选择项目" @change="projectChange" clearable>
                    <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"></el-option>
                </el-select>
            </el-col>
            <el-col :span="3">
                <el-select v-model="ApiInfo.module_id" placeholder="选择模块" clearable>
                    <el-option  v-for="module_info in moduleList" :key="module_info.id" :label="module_info.module_name" :value="module_info.id"></el-option>
                </el-select>
            </el-col>
        </el-form-item>
        <!-- 这部分内饰是请求方式 url 调试按钮-->
        <el-form-item>
            <el-col :span="3">
                <el-select v-model="ApiInfo.request_method" placeholder="请求方式" clearable style="width:115px;">
                    <el-option label="GET" value="GET"></el-option>
                    <el-option label="POST" value="POST"></el-option>
                    <el-option label="PUT" value="PUT"></el-option>
                    <el-option label="DELETE" value="DELETE"></el-option>
                </el-select>
            </el-col>
            <el-col :span="17">
                <el-input v-model="ApiInfo.request_url" placeholder="输入接口URL"></el-input>
            </el-col>
            <el-col :span="1"></el-col>
            <el-col :span="3">
                <el-button type="primary" @click="debugRequest">请求(调试)</el-button>
            </el-col>
        </el-form-item>
        <!-- 这部分是请求分片配置 -->
        <el-form-item>
            <!-- 这部分是总表单-tabs是选项卡容器，tab-pane是选项卡的内容 -->
            <el-tabs class="demo-tabs" v-model="tabActiveName">
                <!-- 这部分是第一个子表单 key value部分-->
                <el-tab-pane label="URL参数" name="URL参数">
                    <el-table :data="ApiInfo.request_params" style="width:100%" max-height="250">
                        <el-table-column prop="key" label="参数名" style="width:40%"></el-table-column>
                        <el-table-column prop="value" label="参数值" style="width:40%"></el-table-column>
                        <el-table-column prop="right" label="删除" style="width:20%">
                            <template #default="scope">
                            <el-button link type="primary" size="small" @click.prevent="deleteParams(scope.$index)">删除</el-button>
                        </template>
                        </el-table-column>
                    </el-table>
                    <el-input v-model="requestparams.key" placeholder="输入参数名" style="width:35%"></el-input>
                    <el-input v-model="requestparams.value" placeholder="输入参数值" style="width:35%"></el-input>
                    <el-button style="width: 30%;" @click="onAddParams">添加</el-button>
                </el-tab-pane>
                <!-- 这部分是第二个子表单 请求头部分 -->
                <el-tab-pane label="请求头header" name="请求头header">
                    <el-table :data="ApiInfo.request_headers" style="width:100%" max-height="250">
                        <el-table-column prop="key" label="请求头名称" style="width:40%"></el-table-column>
                        <el-table-column prop="value" label="请求头内容" style="width:40%"></el-table-column>
                        <el-table-column prop="right" label="删除" style="width:20%">
                            <template #default="scope">
                                <el-button link type="primary" size="small" @click.prevent="deleteHeaders(scope.$index)">删除</el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                    <el-input v-model="requestheaders.key" placeholder="输入请求头参数名" style="width:35%"></el-input>
                    <el-input v-model="requestheaders.value" placeholder="输入请求头参数值" style="width:35%"></el-input>
                    <el-button style="width: 30%;" @click="onAddHeaders">添加</el-button>
                </el-tab-pane>
                <!-- 这部分是第三个子表单 请求体部分 -->
                <el-tab-pane label="请求body" name="请求body">
                    <el-tabs class="demo-tabs" model-value="form-data">
                        <!-- 这是form-data -->
                        <el-tab-pane label="form-data" name="form-data">
                            <!-- 这是form-data的数据表显示的 -->
                            <el-table :data="ApiInfo.request_form_datas" style="width: 100%" max-height="250">
                                <!-- 表单参数名 -->
                                <el-table-column prop="key" label="表单参数名" style="width: 40%;">
                                </el-table-column>
                                 <!-- 表单参数值 -->
                                <el-table-column prop="value" label="表单参数值" style="width: 40%;">
                                </el-table-column>
                                <!-- 删除部分 -->
                                <el-table-column fixed="right" label="删除" style="width: 20%">
                                    <template #default="scope">
                                        <el-button link type="primary" size="small" @click.prevent="deleteBodyFormDatas(scope.$index)">删除</el-button>
                                    </template>
                                </el-table-column>
                            </el-table>
                            <!-- 这是form-data的数据表输入的 -->
                             <el-input v-model="requestBodyFormDatas.key" placeholder="输入表单参数名" style="width: 35%;"></el-input>
                             <el-input  v-model="requestBodyFormDatas.value" placeholder="输入表单参数值" style="width: 35%;"></el-input>
                             <el-button style="width: 30%;" @click="onAddBodyFormDatas">添加</el-button>
                        </el-tab-pane>
                        <!-- 这是x-www-form-data -->
                        <el-tab-pane label="x-www-form-data" name="x-www-form-data">
                            <!-- 这是x-www-form-data的数据表显示的 -->
                            <el-table :data="ApiInfo.request_www_form_datas" style="width: 100%" max-height="250">
                                <!-- 表单参数名 -->
                                <el-table-column prop="key" label="表单参数名" style="width: 40%;">
                                </el-table-column>
                                 <!-- 表单参数值 -->
                                <el-table-column prop="value" label="表单参数名" style="width: 40%;">
                                </el-table-column>
                                <!-- 删除部分 -->
                                <el-table-column fixed="right" label="删除" style="width: 20%">
                                    <template #default="scope">
                                        <el-button link type="primary" size="small" @click.prevent="deleteBodyWwwFormDatas(scope.$index)">删除</el-button>
                                    </template>
                                </el-table-column>
                            </el-table>
                            <!-- 这是form-data的数据表输入的 -->
                            <el-input v-model="requestBodyWwwFormDatas.key" placeholder="输入表单参数名" style="width: 35%;"></el-input>
                            <el-input  v-model="requestBodyWwwFormDatas.value" placeholder="输入表单参数值" style="width: 35%;"></el-input>
                            <el-button style="width: 30%;" @click="onAddBodyWwwFormDatas">添加</el-button>
                        </el-tab-pane>
                        <!-- 这是json -->
                        <el-tab-pane label="json" name="json">
                            <el-input v-model="ApiInfo.requests_json_data" type="textarea" :rows="10" placeholder="请输入json内容"></el-input>
                        </el-tab-pane>
                    </el-tabs>
                </el-tab-pane>
                <!-- 这部分是第四个子表单 执行前事件部分 -->
                <el-tab-pane label="执行前事件(pre)" name="执行前事件(pre)">
                    <el-row rows="15">
                        <el-col :span="17">
                            <el-input v-model="ApiInfo.pre_request" type="textarea" :rows="15" placeholder="执行前事件(数据加密，数据库查询)"></el-input>
                        </el-col>
                        <el-col :span="1"></el-col>
                        <el-col :span="6">
                            <!-- target新标签页打开， -->
                            <el-link href="https://www.baidu.com" target="_blank" type="danger" style="width: 100%;">脚本使用说明书</el-link>
                            <el-link type="success" style="width: 100%;" @click="code_pre_sql">数据库操作</el-link>
                        </el-col>
                    </el-row>
                </el-tab-pane>
                <!-- 这部分是第五个子表单 执行后事件部分 -->
                <el-tab-pane label="执行后事件(post)" name="执行后事件(post)">
                    <el-row rows="15">
                        <el-col :span="17">
                            <el-input v-model="ApiInfo.post_request" type="textarea" :rows=15  placeholder="执行后事件(断言，数据提取等)"></el-input>
                        </el-col>
                        <el-col :span="1"></el-col>
                        <el-col :span="6">
                            <!-- target新标签页打开， -->
                            <el-link href="https://www.baidu.com" target="_blank" type="danger" style="width: 100%;">脚本使用说明书</el-link>
                            <el-link type="success" style="width: 100%" @click="code_post_sql">数据库操作</el-link>
                            <el-link type="success" style="width: 100%" @click="code_jsonAssert">json数据断言</el-link>
                            <el-link type="success" style="width: 100%" @click="code_statusCodeAssert">响应状态码断言</el-link>
                            <el-link type="success" style="width: 100%" @click="code_headerAssert">响应头断言</el-link>
                            <el-link type="success" style="width: 100%" @click="code_json_vars">json数据提取</el-link>
                        </el-col>
                    </el-row>
                </el-tab-pane>
                <!-- 这部分是第六个子表单 DEBUG变量定义部分 -->
                <el-tab-pane label="DEBUG变量定义" name="DEBUG变量定义">
                    <el-table :data="ApiInfo.debug_vars" style="width:100%" max-height="250">
                        <el-table-column prop="key" label="变量名" style="width:40%"></el-table-column>
                        <el-table-column prop="value" label="变量值" style="width:40%"></el-table-column>
                        <el-table-column prop="right" label="删除" style="width:20%">
                            <template #default="scope">
                            <el-button link type="primary" size="small" @click.prevent="deleteVars(scope.$index)">删除</el-button>
                        </template>
                        </el-table-column>
                    </el-table>
                    <el-input v-model="debugVars.key" placeholder="输入变量名" style="width:35%"></el-input>
                    <el-input v-model="debugVars.value" placeholder="输入变量值" style="width:35%"></el-input>
                    <el-button style="width: 30%;" @click="onAddVars">添加</el-button>
                </el-tab-pane>
                <!-- 这部分是第七个子表单 调试输出内容部分 -->
                <el-tab-pane label="调试输出内容" name="调试输出内容">
                    <el-input v-model="debugArea" type="textarea" :rows="25" placeholder="接口调用输出内容" disabled></el-input>
                </el-tab-pane>
            </el-tabs>
        </el-form-item>
        <!-- 这是保存取消 -->
         <el-form-item>
            <el-button type="primary" @click="onSubmit">保存</el-button>
            <el-button type="primary" @click="onCancel">取消</el-button>
         </el-form-item>
    </el-form>
</template>

<script setup>
import{ref,reactive} from "vue"
import { queryAll } from "../project/ApiProject.js"
import {queryByPage as apiModuleQuery} from "~/views/apitest/module/ApiModule.js"
import { ElMessage } from "element-plus";
import {insertData,queryById,updateData,doDebugRequest} from "~/views/apitest/apiinfo/ApiInfo.js"
import {useRouter,useRoute} from "vue-router"
// 要发送的路由
const router = useRouter()
// 要获取的路由
const route = useRoute()
// 表单总的数据
const ApiInfo = reactive({
    id:0,
    api_name:'',
    request_method:'',
    request_url:'',
    project_id:'',
    module_id:'',
    request_params:[],
    request_headers:[],
    pre_request:'',
    post_request:'',
    debug_vars: [],
    request_form_datas:[],
    request_www_form_datas:[],
    requests_json_data:''
})
// 表单的总保存
const onSubmit = ()=>{
    // 将数组修改为json字符串--JSON.stringify()
    let data = {
        id:ApiInfo.id,
        api_name:ApiInfo.api_name,
        request_method:ApiInfo.request_method,
        request_url:ApiInfo.request_url,
        project_id:ApiInfo.project_id,
        module_id:ApiInfo.module_id,
        request_params:JSON.stringify(ApiInfo.request_params),
        request_headers:JSON.stringify(ApiInfo.request_headers),
        pre_request:ApiInfo.pre_request,
        post_request:ApiInfo.post_request,
        debug_vars: JSON.stringify(ApiInfo.debug_vars),
        request_form_datas:JSON.stringify(ApiInfo.request_form_datas),
        request_www_form_datas:JSON.stringify(ApiInfo.request_www_form_datas),
        requests_json_data:ApiInfo.requests_json_data
    }
    // 新建请求
    updateData(data).then((res)=>{
        if (res.data.code == 200) {
            router.push('/ApiInfoList') // 跳转回列表页面 - 不同的页面，不同的路径
            ElMessage.success("修改成功")
        }else{
            ElMessage.error("修改失败")
        }
        // 返回主页面
    }).catch((err)=>{
        ElMessage.error("修改失败")
        console.error("修改失败",err)
    })
}
// 表单的总取消
const onCancel = ()=>{
    router.push('/ApiInfoList')
}
// 项目下拉框筛选的展示数据
const projectList = ref([])
// 请求获取下拉框筛选的数据
function getProjectList(){
    queryAll().then((res)=>{
        projectList.value = res.data.data
    })
}
// 初始化获取项目所需的列表数据
getProjectList()
// 项目筛选的监听-执行获取模块的方法
const projectChange = () =>{
        // 多做一步，每次执行时先清空模块双向绑定已选的数据，防止不一致
    ApiInfo.module_id = ''
    // 直接调取获取模块的方法，不需要传值，因为值在searchForm的双向绑定里
    getmodulelist()
}
// 模块的列表
const moduleList = ref([])
// 模块列表的请求-根据项目触发调用，需要携带项目的id
function getmodulelist(){
    // 需要传复用请求的请求体项目的id，页码，每页数据
    apiModuleQuery({
        "project_id":ApiInfo.project_id,
        "page":1,
        "pageSize":9999999
    }).then((res)=>{
        // 赋值给模块需要的下拉列表数据
        moduleList.value = res.data.data
        console.log("模块的数据为",moduleList.value)
    })
}
// 请求的调试方法
const debugRequest = ()=>{
    tabActiveName.value = "调试输出内容";
    doDebugRequest(ApiInfo).then((res)=>{
        if (res.data.code === 200) {
            if (res.data.data.output.includes('FAILED')) {
                ElMessage.error("请求成功，但接口测试未通过");
        } else if (res.data.data.output.includes('PASSED')) {
            ElMessage.success("请求成功，接口测试通过");
        } else {
        ElMessage.error("未检测到明确的测试结果，请手动查看");
        }
        } else {
            ElMessage.error("请求失败");
        }
// 处理 Unicode 编码
const decodedOutput = res.data.data.output.replace(/\\u([0-9a-fA-F]{4})/g, (match, p1) => {
            return String.fromCharCode(parseInt(p1, 16));
        });
        debugArea.value = decodedOutput;
  })
}
// 表单的主数据
const tabActiveName = ref([])
// 删除参数的keyvalue-index后是deleteCount的默认参数，标识删除几个
const deleteParams = (index)=>{
    ApiInfo.request_params.splice(index,1)
}
// 添加的请求参数keyvalue-保存进apiinfo里
const onAddParams = ()=>{
    ApiInfo.request_params.push({
        key:requestparams.key,
        value:requestparams.value
    })
    // push进主表单后清空填写
    requestparams.key='',
    requestparams.value=''
}
// 请求参数keyvalue的预存
const requestparams = reactive({
    key:'',
    value:''
})
// 请求头参数keyvalue的预存
const requestheaders = reactive({
    key:'',
    value:''
})
// 添加的请求头参数keyvalue
const onAddHeaders = ()=>{
    ApiInfo.request_headers.push({
        key:requestheaders.key,
        value:requestheaders.value
    })
    // push进主表单后清空填写
    requestheaders.key='',
    requestheaders.value=''
}
// 删除请求头的keyvalue
const deleteHeaders = (index)=>{
    ApiInfo.request_headers.splice(index,1)
}
// debugVars变量定义的keyvalue的预存
const debugVars = reactive({
  key: "",
  value: "",
})
// 添加debugVars变量定义的keyvalue
const onAddVars = ()=>{
    ApiInfo.debug_vars.push({
        key:debugVars.key,
        value:debugVars.value
    })
    // push进主表单后清空填写
    debugVars.key='',
    debugVars.value=''
}
// 删除debug变量定义的keyvalue
const deleteVars = (index)=>{
    ApiInfo.debug_vars.splice(index,1)
}
// 调试输出的返回部分
const debugArea = ref(null)
// 删除请求体formdata的keyvalue
const deleteBodyFormDatas = (index)=>{
    ApiInfo.request_form_datas.splice(index,1)
}
// 添加请求体formdata的keyvalue的预存
const requestBodyFormDatas= reactive({
    key: '',
    value: ''
})
// 添加请求体formdata的keyvalue
const onAddBodyFormDatas = ()=>{
    ApiInfo.request_form_datas.push({
        key:requestBodyFormDatas.key,
        value:requestBodyFormDatas.value
    })
    // push进主表单后清空填写
    requestBodyFormDatas.key='',
    requestBodyFormDatas.value=''
}
// 删除请求体wwwwformdata的keyvalue
const deleteBodyWwwFormDatas= (index)=>{
    ApiInfo.request_www_form_datas.splice(index,1)
}
// 添加请求体wwwwformdata的keyvalue的预存
const requestBodyWwwFormDatas= reactive({
    key: "",
    value: ""
})
// 添加请求体wwwwformdata的keyvalue
const onAddBodyWwwFormDatas = ()=>{
    ApiInfo.request_www_form_datas.push({
        key:requestBodyWwwFormDatas.key,
        value:requestBodyWwwFormDatas.value
    })
    // push进主表单后清空填写
    requestBodyWwwFormDatas.key='',
    requestBodyWwwFormDatas.value=''
}
// 编辑进入表单页根据id请求数据-并回填数据-parse将获取json字符串转回对象
const loaddata = ()=>{
    let id = route.query.id
    queryById(id).then((res)=>{
        ApiInfo.id = res.data.data.id
        ApiInfo.project_id = res.data.data.project_id
        ApiInfo.module_id = res.data.data.module_id
        ApiInfo.api_name = res.data.data.api_name
        ApiInfo.request_method = res.data.data.request_method
        ApiInfo.request_url = res.data.data.request_url
        ApiInfo.request_params = JSON.parse(res.data.data.request_params) //将json对象转换为json字符串，传给后端,
        ApiInfo.request_headers = JSON.parse(res.data.data.request_headers)
        ApiInfo.debug_vars = JSON.parse(res.data.data.debug_vars)
        ApiInfo.request_form_datas = JSON.parse(res.data.data.request_form_datas) // 请求中的 form-data
        ApiInfo.request_www_form_datas = JSON.parse(res.data.data.request_www_form_datas) // 请求中的 x-www-form-data
        ApiInfo.requests_json_data = res.data.data.requests_json_data // 请求中的 json 数据
        ApiInfo.pre_request = res.data.data.pre_request // 执行前事件
        ApiInfo.post_request = res.data.data.post_request // 执行后事件
        getmodulelist()
    })
}
// 初始化数据
loaddata()
// 执行前事件的点击
const code_pre_sql = ()=>{
    let code = `
    result = sql_exec('mysql',{
        'host': 'shop-xo.hctestedu.com',
        'user': 'api_test',
        'password': 'Aa9999!',
        'db': 'shopxo_hctested'
    },"SELECT * FROM \`sxo_user\` where username='{{accounts}}'")`;
    ApiInfo.pre_request += code;
}
// 执行后事件的点击
const code_post_sql = ()=>{
    let code = `
    result = sql_exec('mysql',{
        'host': 'shop-xo.hctestedu.com',
        'user': 'api_test',
        'password': 'Aa9999!',
        'db': 'shopxo_hctested'
    },"SELECT * FROM \`sxo_user\` where username='{{accounts}}'")`;
    ApiInfo.post_request += code;
}
// 代码段 - json断言
const code_jsonAssert = () => {
  console.log("jsonAssert!");
  let code = `\nassert step['response'].json()['你要判断的数据'] == '断言值', '断言提示语句'`;
  ApiInfo.post_request += code;
}
// 代码段 - 响应状态码断言
const code_statusCodeAssert = () => {
  let code = "\nassert step['response'].status_code == '断言值', '断言提示语句'";
  ApiInfo.post_request += code;
};
// 代码段 - 响应头断言
const code_headerAssert = () => {
  let code =
    "\nassert step['response'].headers['你要判断的头名称'] == '断言值', '断言提示语句'";
    ApiInfo.post_request += code;
};
// 代码段 - json数据提取
const code_json_vars = () => {
  console.log("jsonPath!");
  let code = `\ncontext.update({'你要提取的变量名': step['response'].json()['你要提取的数据']})`;
  ApiInfo.post_request += code;
};
</script>




<style>
.demo-tabs > .el-tabs__content {
  padding: 5px;
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
}
</style>