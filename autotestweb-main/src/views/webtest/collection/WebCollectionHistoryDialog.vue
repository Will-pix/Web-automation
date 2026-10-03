<template>
        <!-- 弹窗 - 弹窗加载执行记录 -->
        <el-dialog v-model="props.webHistoryDialogFormVisible" title="执行记录" @close="handleClose">
        <el-form-item>
            <el-table :data="webHistoryList" style="width: 100">
                <el-table-column prop="id" label="报告编号" min-width="20%"/>
                <el-table-column prop="create_time" label="执行时间" min-width="30%" show-overflow-tooltip="true" />
                <el-table-column prop="history_desc" label="执行情况简述" min-width="30%" show-overflow-tooltip="true" />
                <el-table-column fixed="right" label="操作" min-width="20%">
                    <template #default="scope">
                        <el-button type="primary" size="small" @click.prevent="showWebHistory(scope.$index)">
                            查看测试报告
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-form-item>

        <el-form-item>
            <div class="w-3/4 mx-auto">
                <el-pagination 
                    v-model:current-page= "currentWebInfoPage" 
                    v-model:page-size= "webInfoPageSize" 
                    :page-sizes="[5, 10, 20, 30, 50]"
                    layout="total, sizes, prev, pager, next, jumper" 
                    :total="webInfoTotal" @size-change="handleSizeChange"
                    @current-change="handleCurrentChange" />
            </div>
        </el-form-item>
    </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, provide,inject,watch } from "vue";
import { ElMessage } from "element-plus";
// import { eventBus } from './event-bus.js';
import { queryByPage as queryWebHistoryByPage } from "./WebHistory.js"; // 不同页面不同的接口
import { apiBaseURL } from '../../../../config.js';

// 接收的信息
const props = defineProps(["webHistoryDialogFormVisible","tableDataid"]); // 接收父组件传递的显示状态
// 发送的信息
const emit = defineEmits(["close"]);
// 关闭-发送
const handleClose = () => {
  emit("close");  // 通知父组件关闭弹窗
};
// -------6-2 分页相关的-----
const webInfoPageSize = ref(10); // 每页大小
const webInfoTotal = ref(0);  // 总数
const currentWebInfoPage = ref(1) // 页码
// 变更页大小
const handleSizeChange = (val) => {
    console.log("页大小变化:" + val)
    webInfoPageSize.value = val
    loadWebHistorys()
}
// 变更页码
const handleCurrentChange = (val) => {
    console.log("页码变化:" + val)
    currentWebInfoPage.value = val
    loadWebHistorys()
}
// 根据集合id加载报告信息
function loadWebHistorys() {
    let searchData = {}
    searchData["collection_info_id"] = props.tableDataid
    searchData["page"] = currentWebInfoPage.value
    searchData["pageSize"] = webInfoPageSize.value
    queryWebHistoryByPage(searchData).then((res) => {
        console.log(res.data.data)
        webHistoryList.value = res.data.data
        webInfoTotal.value = res.data.total
    })
}
// 表格数据
const webHistoryList = ref([]) // 关联的接口
// 查看报告
const showWebHistory = (index) =>{
    // 注意： 这个地方的测试报告服务器地址，是需要根据后端服务器修改的，这里写死了，后面要改成配置文件
    var report_id = webHistoryList.value[index]["history_detail"]
    // window.open("http://127.0.0.1:5000/api/WebHistory/"+report_id+"/index.html", '_blank');
    window.open(apiBaseURL+"/WebHistory/"+report_id+"/index.html", '_blank');
    
}
// 监听id请求
watch(()=> props.tableDataid, (newId) =>{
    console.log("id变化",newId)
    if(newId>0){
        loadWebHistorys()
    }
})

</script>