<template>
  <!-- case添加前置的弹窗 -->
  <el-dialog v-model="props.visible" title="添加前置用例" width="60%" @close="handleClose">
        <!-- 弹窗的搜索条件 -->
        <!-- <el-form :model="searchForm" inline style="margin-left: 10px; margin-right: 10px"> -->
        <el-form-item label="项目名称：" style="margin-left: 10px; margin-right: 10px">
            <el-select v-model="searchForm.project_id" placeholder="根据项目名称筛选" clearable filterable style="width: 200px">
                <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
            </el-select>
            <el-form-item label="WEB用例名称：" style="margin-left: 10px; margin-right: 10px">
                <el-input v-model="searchForm.case_name" placeholder="根据Web用例名称筛选" clearable />
            </el-form-item>
            <el-button type="primary" @click="loadWebInfos()">查询</el-button>
        </el-form-item>
        <!-- </el-form> -->
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
import { ref, reactive } from 'vue'
import { ElMessage } from "element-plus";

// 接收父组件传递的显示状态
const props = defineProps(["visible","webinfo_id"])

// 发送的信息
const emit = defineEmits(["close", "refresh"])

// 关闭-发送
const handleClose = () => {
  emit("close")  // 通知父组件关闭弹窗
}

// 分页
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

import { queryByPage as queryWebInfoByPage } from "../webinfo/WebInfo.js"; // 不同页面不同的接口
// 查询用例
const loadWebInfos = () =>{
    let searchData = searchForm;
    searchData["page"] = currentWebInfoPage.value;
    searchData["pageSize"] = webInfoPageSize.value;
    searchData["is_pre"] = '1'
    queryWebInfoByPage(searchData).then((res)=>{
        webInfoList.value = res.data.data;
        webInfoTotal.value = res.data.total;
    })
}
// 要添加的用例列表
const webInfoList = ref([])

import { insertData } from "./WebInfoFormPre.js"; 
// 添加用例 - 接收点击的那一行的索引
const addWebInfo = (index) =>{
    // 当前用例id（当前正在编辑的用例）
    console.log("当前用例ID:", props.webinfo_id)
    // 查询到的复用用例的信息（点击添加按钮的那一行）
    const selectedWebInfo = webInfoList.value[index]
    console.log("选中的复用用例ID:", selectedWebInfo.id)
    console.log("选中的复用用例名称:", selectedWebInfo.case_name)
    console.log("选中的复用用例完整信息:", selectedWebInfo)
    // 构造数据
    let data = {
        web_info_id:props.webinfo_id,
        pre_info_id:selectedWebInfo.id
    }
    // 在这里处理添加前置用例的逻辑
    insertData(data).then((res)=>{
        if(res.data.code==200){
            ElMessage.success("添加成功")
            // 通知父组件刷新数据
            emit("refresh")
        } else {
            ElMessage.error("添加失败：" + (res.data.msg || "服务器异常"))
        }
    })
}

</script>