<template>
    <!-- 弹窗 - 弹窗加载执行配置 -->
    <el-dialog v-model="props.visible" title="执行配置"  @close="handleClose" >
        <el-form-item label="浏览器集群选择：">
            <el-select v-model="browserIndex" placeholder="选择需集群浏览器" clearable filterable>
                <el-option v-for="browser in browserList" :key="browser.id" :label="browser.name" :value="browser.id" />
            </el-select>
        </el-form-item>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="handleClose">取消</el-button>
                <el-button type="primary" @click="okExecuteTest" :loading="loading">开始执行</el-button>
                <el-button type="primary" @click="okExecuteTest_index" :loading="loading">开始执行并跳转监控中心</el-button>
            </span>
        </template>
  </el-dialog>
</template>

<script setup>
import {ref,reactive, watch} from 'vue'
import { ElMessage } from "element-plus";
import { apiBaseURL } from '../../../../config.js';
import {useRouter,useRoute} from "vue-router"
// 要发送的
const router = useRouter()
// 接收的信息
const props = defineProps(["visible","project_id","webinfo_id"]); // 接收父组件传递的显示状态
// 发送的信息
const emit = defineEmits(["close"]);
// 关闭-发送
const handleClose = () => {
  emit("close");  // 通知父组件关闭弹窗
};
// 下拉框的数据
import { queryByPage as queryByPageAllbrowser } from "../browserRemote/WebBrowser.js"; // 不同页面不同的接口
const browserList = ref([{
  id: 0,
  name: "",
  enName: "",
  project_id: "",
  remote_url: "",
  browser_debug: "",
  is_enabled: "",
}]);
// 获取下拉框数据-index是项目的id
function getbrowserList() {
  console.log("当前的项目ID 是：",props.project_id)
  let searchData = {
    "page": 1,
    "pageSize": 999,
    "project_id":props.project_id // 只显示当前项目的浏览器数据
  }
  queryByPageAllbrowser(searchData).then((res) => {
    browserList.value = res.data.data;
  });
}
// 监听有打开弹窗就执行
watch(()=> props.visible, (newVal) =>{
    if(newVal){
        getbrowserList()
    }
})
// 浏览器id
const browserIndex = ref()
// 执行
import {debugTest} from './WebInfo.js'
const okExecuteTest = () =>{
    if(browserIndex.value){
        loading.value = true
        let searchData = reactive({})
        searchData["id"] = props.webinfo_id
        searchData["browser_id"] = browserIndex.value
        debugTest(searchData).then((res)=>{
            if(res.data.code===200){
                ElMessage.success("自动化执行成功，等待报告生成")
                console.log(res.data.data.report_id)
                window.open(apiBaseURL+"/WebReportViewer/" + res.data.data.report_id + "/index.html", '_blank');
                // window.open("http://127.0.0.1:5000/api/WebReportViewer/" + res.data.data.report_id + "/index.html", '_blank');
            }else{
                ElMessage.error("执行失败")
            }
        }).finally(()=>{
            loading.value = false
        })
    }else{
        ElMessage.error("请选择浏览器")
    }
}
// loading状态
const loading = ref(false)
// 开始执行并跳转到首页大盘
const okExecuteTest_index = () =>{
    if(browserIndex.value){
        loading.value = true
        let searchData = reactive({})
        searchData["id"] = props.webinfo_id
        searchData["browser_id"] = browserIndex.value
        router.push({
            path:"/",
        })
        debugTest(searchData).then((res)=>{
            if(res.data.code===200){
                ElMessage.success("自动化执行成功，等待报告生成")
                console.log(res.data.data.report_id)
                window.open(apiBaseURL+"/WebReportViewer/" + res.data.data.report_id + "/index.html", '_blank');
                // window.open("http://127.0.0.1:5000/api/WebReportViewer/" + res.data.data.report_id + "/index.html", '_blank');
            }else{
                ElMessage.error("执行失败")
            }
        }).finally(()=>{
                router.push({
                    path:"/WebInfoForm",
                    query: { id: props.webinfo_id } 
                    })
            loading.value = false
        })
    }else{
        ElMessage.error("请选择浏览器")
    }
}
</script>