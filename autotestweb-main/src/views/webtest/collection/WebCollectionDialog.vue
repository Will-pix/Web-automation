<template>
      <el-dialog v-model="props.infoDialogFormVisible" title="添加用例"  @close="handleClose">
            <!-- 弹窗的搜索条件 -->
        <el-form-item label="项目名称：" style="margin-left: 10px; margin-right: 10px">
            <el-select v-model="searchForm.project_id" placeholder="根据项目名称筛选" clearable filterable style="width: 200px">
                <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
            </el-select>
            <el-form-item label="WEB用例名称：" style="margin-left: 10px; margin-right: 10px">
                <el-input v-model="searchForm.case_name" placeholder="根据Web用例名称筛选" clearable />
            </el-form-item>
            <el-button type="primary" @click="loadWebInfos()">查询</el-button>
        </el-form-item>
        <!-- END 弹窗的搜索条件 -->
        <!-- 显示对应的所有数据 -->
        <el-table :data="webInfoList" style="width: 100%">
            <el-table-column prop="id" label="用例编号" style="width: 5%" />
            <el-table-column prop="case_name" label="用例名称" style="width: 30%" :show-overflow-tooltip="true" />
            <el-table-column prop="case_desc" label="用例描述" style="width: 60%" :show-overflow-tooltip="true" />
            <el-table-column fixed="right" label="操作" style="width: 5%">
                <template #default="scope">
                <el-button type="primary" size="small" @click.prevent="addWebInfo(scope.$index)">
                    添加
                </el-button>
                </template>
            </el-table-column>
        </el-table>
    <!-- END显示对应的所有数据 -->
          <!-- 分页 -->
    <div class="mb-4"></div>
    <div class="w-3/4 mx-auto mb-4">
        <el-pagination 
        v-model:current-page= "currentWebInfoPage" 
        v-model:page-size= "webInfoPageSize" 
        :page-sizes="[5, 10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper" 
        :total="webInfoTotal" @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </div>
    <!-- END 分页 -->
      </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, provide,inject } from "vue";
import { ElMessage } from "element-plus";
import { eventBus } from './event-bus.js';
const form = inject('form'); // 通过相同标识符获取表单实例
// 接收的信息
const props = defineProps(["infoDialogFormVisible","webcollection"]); // 接收父组件传递的显示状态
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
    loadWebInfos()
}

// 变更页码
const handleCurrentChange = (val) => {
    console.log("页码变化:" + val)
    currentWebInfoPage.value = val
    loadWebInfos()
}
// 搜索
const searchForm = reactive({ "project_id": '', "case_name": '' })
// 项目的列表
const projectList = ref([])
// 获取项目
import { queryAll as queryAllProject } from "../project/WebProject.js"; // 不同页面不同的接口
function getProjectList() {
  queryAllProject().then((res) => {
    projectList.value = res.data.data;
  });
}
getProjectList();
// 要添加的用例列表
const webInfoList = ref([])
import { queryByPage as queryWebInfoByPage } from "../webinfo/WebInfo.js"; // 不同页面不同的接口
// 查询用例
const loadWebInfos = () =>{
    let searchData = searchForm;
    searchData["page"] = currentWebInfoPage.value;
    searchData["pageSize"] = webInfoPageSize.value;
    queryWebInfoByPage(searchData).then((res)=>{
        webInfoList.value = res.data.data;
        webInfoTotal.value = res.data.total;
    })
}
// -------6-4 添加当前的数据到对应的测试计划当中-------
import {
  queryByPage as queryByPageForDetail,
  insertData as insertDataForDetail,
  updateData as updateDataForDetail,
  deleteData as deleteDataForDetail,
} from "./WebCollectionDetail.js"; // 不同页面不同的接口
// 添加用例
function addWebInfo(index) {
  // console.log("当前点击的CASE",webInfoList.value[index])
  console.log("添加的数据信息", webInfoList.value[index].param_data)
  let InsertData = {
    collection_info_id: props.webcollection.id,
    web_info_id: webInfoList.value[index].id,
    ddt_param_data: JSON.stringify([]),
    // run_order: webInfoList.value[index].run_order,
    run_order: 1,
  };

  insertDataForDetail(InsertData).then((res) => {
      // 添加成功,刷新列表
      if (res.data.code == 200) {
        ElMessage.success("添加成功")
        // emit("loadcase")
        // 重新加载一下前置用例，并且及时刷新页面
        // getWebCaseInfo()
        // loadData(webcollection.id);
        eventBus.value.emit('refreshList');

      }
    }
  );
}
// -------END 6-4 添加当前的数据到对应的测试计划当中-------
</script>