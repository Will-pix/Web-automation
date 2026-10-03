<template>
    <!-- 用例维护:row-key标识行id，从实际数据拿哪里作为行唯一标识，这里使用了id -->
    <el-table :data="tableDataCaseInfo"  style="width: 100%" @expand-change="handleExpandChange"  :row-key="(row) => row.id" :expand-row-keys="expandedRowKeys" :row-class-name="tableRowClassName">
        <el-table-column fixed="right" label="操作" width="180">
                <template #default="scope">
                    <el-button link type="primary" size="small" @click.prevent="editCaseParamData(scope.$index)">确认修改</el-button>
                    <el-button link type="primary" size="small" @click.prevent="deleteApiCases(scope.$index)">删除</el-button>
                </template>
        </el-table-column>
        <el-table-column prop="run_order" label="顺序" width="130" >
                <template #default="scope">
                  <el-input-number style="width: 100px" v-model="scope.row.run_order" placeholder="顺序-数字类型" :min="1"></el-input-number>
                </template>
        </el-table-column>
        <el-table-column prop="case_name" label="用例名称" :show-overflow-tooltip="true" />
        <el-table-column prop="param_data" label="变量依赖说明" :show-overflow-tooltip="true" />
        <el-table-column prop="ddt_param_data" label="DDT数据驱动" type="expand" width="120">
            <template #default="case_scope">
                <!-- 位置1 : 输入描述名称,添加数据 -->
                <el-input v-model="temp_desc" placeholder="desc参数-测试数据组标题" style="width: 40%;margin-left: 10px;" />
                <el-button style="width: 15%;margin-left: 10px;" @click="onAddDdtParamsGroup(case_scope.$index)">添加一组数据</el-button>
                <!-- 折叠面板 -->
                 <el-collapse style="margin-top: 10px;" accordion>
                    <el-collapse-item v-for="(ddt_data, ddt_data_index) in case_scope.row.ddt_param_data" :key="ddt_data_index" :name="ddt_data_index">
                        <template #title>
                            <!-- case_scope.row.id, ddt_data_index  哪个行id的哪个索引（折叠面板） -->
                            <div  style="display: flex; align-items: center; width: 100%; cursor: pointer; vertical-align: middle;"> 
                                <!-- stop是为了阻止向上div发送传递 -->
                                <el-button  style="margin-left: 10px; " @click.stop="onDeleteDdtParamsGroup(case_scope.$index, ddt_data_index)">删除</el-button>
                                <span style="margin-left: 10px; "> 第 {{ddt_data_index + 1}} 组 : {{ ddt_data[0].value }} ↓展开编辑</span>
                            </div>
                        </template>
                        <el-table :data="ddt_data">
                            <el-table-column prop="key" label="变量名" style="width: 40%">
                                <template #default="ddt_data_scope">
                                    <el-input v-model="ddt_data_scope.row.key" placeholder="变量名称"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column prop="value" label="变量值" style="width: 40%">
                                <template #default="ddt_data_scope">
                                    <el-input v-model="ddt_data_scope.row.value" placeholder="变量值"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column fixed="right" label="删除" style="width: 15%">
                                <template #default="ddt_data_scope">
                                    <el-button link type="primary" size="small" @click.prevent="deleteDdtParams(case_scope.$index,ddt_data_index, ddt_data_scope.$index)">删除
                                    </el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="input-group">
                        <el-input v-model="temp_ddt_params.key" placeholder="变量名" style="width: 35%" />
                        <el-input v-model="temp_ddt_params.value" placeholder="变量值" style="width: 35%" />
                        <el-button style="width: 15%" @click="onAddDdtParams(case_scope.$index,ddt_data_index)">添加</el-button>
                      </div>
                    </el-collapse-item>

                 </el-collapse>
            </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
            <template #default="{ row }">
                <el-tag :type="getStatusType(row)">{{ getStatusText(row) }}
                </el-tag>
            </template>
</el-table-column>
    </el-table>
    <!-- 添加用例位置 -->
    <el-button type="primary" link @click="shoWebInfosDialog" style="margin-top: 20px;"> + 添加用例</el-button>
    <!-- 弹窗抽离 -->
    <WebCollectionDialog :infoDialogFormVisible="infoDialogFormVisible" @close="infoDialogFormVisible = false" :webcollection="props.webcollection" @refreshEvent="getWebCaseInfo"></WebCollectionDialog>

</template>

<script setup>
import { ref, reactive, onMounted, provide,onUnmounted } from "vue";
import WebCollectionDialog from "./WebCollectionDialog.vue";
import { ElMessage } from "element-plus";
import { eventBus } from './event-bus.js';
const props = defineProps(["webcollection"]); // 接收父组件数据
// const form = inject('form'); // 通过相同标识符获取表单实例
const emit = defineEmits(['webcollection']);

// 表单的数据
const tableDataCaseInfo = ref([]);
// 添加用例-触发子组件弹窗
const shoWebInfosDialog = () =>{
    if(props.webcollection.id > 0){
        infoDialogFormVisible.value = true
    }else{
        ElMessage.error("需要先保存当前测试计划才能添加用例")
    }
}
// 子组件弹窗的状态
const infoDialogFormVisible = ref(false)
// 获取列表数据
import {
  queryByPage as queryByPageForDetail,
  insertData as insertDataForDetail,
  updateData as updateDataForDetail,
  deleteData as deleteDataForDetail,
} from "./WebCollectionDetail.js"; // 不同页面不同的接口
const getWebCaseInfo = () =>{
    let searchForm = {}
    let searchData = searchForm;
    searchData["page"] = 1;
    searchData["pageSize"] = 9999;
    searchData["collection_info_id"] = props.webcollection.id;
    queryByPageForDetail(searchData).then((res)=>{
        tableDataCaseInfo.value = res.data.data;
        tableDataCaseInfo.value.forEach((item) => {
            console.log('转换前:', typeof item.ddt_param_data); // 输出 "string"
            item["ddt_param_data"] = JSON.parse(item["ddt_param_data"]);
            console.log('转换后:', typeof item.ddt_param_data); // 输出 "object"
        });
})}
onMounted(()=>{
    if(props.webcollection.id > 0){getWebCaseInfo()}
    eventBus.value.on('refreshList', getWebCaseInfo);
})
// 取消订阅（避免内存泄漏）
onUnmounted(() => {
  eventBus.value.off('refreshList');
});
// 2. 保存一组数据
const temp_desc = ref("") // 临时存储 数据描述
// 添加ddt数据
const onAddDdtParamsGroup = (case_index) => {
    // 判断当前用例是否需要ddt-如果用例没有变量就不允许添加ddt
    let is_param_data = JSON.parse(tableDataCaseInfo.value[case_index].param_data)
    // let is_ddt_param_data = tableDataCaseInfo.value[index].ddt_param_data
    if(is_param_data.length===0){
        ElMessage.error("此用例无变量依赖，如果需要请去用例管理添加变量定义")
        return
    }
    // 判断填写的是否为空
    if(!temp_desc.value){
    ElMessage.error("参数标题必须填写")
    return
    }
    // 获取用例需要的参数-字符串转为js对象
    let case_param_data = JSON.parse(tableDataCaseInfo.value[case_index].param_data)
    // 插入元素到指定位置-标题
    case_param_data.splice(0, 0, {
        "key": "desc",
        "value": temp_desc.value
    })
    console.log("当前的参数为：",case_param_data)
    // 插入到 测试计划的指定用例中
    tableDataCaseInfo.value[case_index].ddt_param_data.push(reactive(case_param_data))
    // 清空 desc 内容
    temp_desc.value=""
    console.log("当前的所有数据为",tableDataCaseInfo.value)
    // 所以我们就可以通过下标获取对应的数据
    console.log(tableDataCaseInfo.value[0]["ddt_param_data"])
}
// 删除
const deleteApiCases = (index) => {
  deleteDataForDetail(tableDataCaseInfo.value[index]["id"]).then((res) => {
    getWebCaseInfo() // 重新加载列表
  })
};
// 3. 删除一组数据
const onDeleteDdtParamsGroup =(case_scope_index, ddt_data_index) => {
  // case_scope_index 哪一条用例 ddt_data_index 第几组 
  tableDataCaseInfo.value[case_scope_index].ddt_param_data.splice(ddt_data_index, 1);
}
// 4.删除某个变量
const deleteDdtParams = (case_scope_index, ddt_data_index, row) => {
    console.log("tableDataCaseInfo的值",tableDataCaseInfo.value)
    console.log("case_scope_index的值",case_scope_index)
    console.log("ddt_data_index的值",ddt_data_index)
    console.log("row的值",row)
    // 判断删除的是不是desc-如果是则禁止删除
    let del_key = tableDataCaseInfo.value[case_scope_index].ddt_param_data[ddt_data_index][row].key
    console.log("删除的数据key是:",tableDataCaseInfo.value[case_scope_index].ddt_param_data[ddt_data_index][row].key)
    if(del_key==="desc"){
        ElMessage.error("用例标题不可删除!,如需删除请删除整组数据")
        return
    }
    // case_scope_index 哪一条用例 ddt_data_index 第几组  row 第几个变量
    tableDataCaseInfo.value[case_scope_index].ddt_param_data[ddt_data_index].splice(row, 1);
};
// 1. 临时存储 数据变量
const temp_ddt_params = reactive([]); 
// 5.添加某个变量
const onAddDdtParams = (case_scope_index, ddt_data_index) => {
    // case_scope_index 哪一条用例 ddt_data_index 第几组 
    // 保存起来
    tableDataCaseInfo.value[case_scope_index].ddt_param_data[ddt_data_index].push({
        key: temp_ddt_params.key,
        value: temp_ddt_params.value,
    });
    // 置空
    temp_ddt_params.key = "";
    temp_ddt_params.value = "";
};
// 修改用例
import { updateData as updateWebCaseCol } from "./WebCollectionDetail.js"; // 不同页面不同的接口
const editCaseParamData = (index) => {
    console.log("ddt的值",tableDataCaseInfo.value[index].ddt_param_data)
    console.log("需要的值",JSON.parse(tableDataCaseInfo.value[index].param_data))
    console.log("需改的用例是",tableDataCaseInfo.value[index].param_data)
    let is_param_data = JSON.parse(tableDataCaseInfo.value[index].param_data)
    let is_ddt_param_data = tableDataCaseInfo.value[index].ddt_param_data
    // 判断当前用例是否需要添加ddt-如果需要则效验为空判断-提示
    if(is_param_data.length>0){
        console.log("有值")
        if(is_ddt_param_data.length===0){
            ElMessage.warning("当前用例存在变量依赖,但没有填写,请注意是否需要填写")
            // return
        }
    }

    // 修改运行参数与执行顺序
    updateWebCaseCol({
        "id": tableDataCaseInfo.value[index].id,
        "ddt_param_data": JSON.stringify(tableDataCaseInfo.value[index].ddt_param_data),
        "run_order": tableDataCaseInfo.value[index].run_order
    }).then((res) => {
        if (res.data.code == 200) {
        console.log("用例执行信息修改成功")
        ElMessage.success(`修改成功：${tableDataCaseInfo.value[index].case_name}`)
        getWebCaseInfo()
        }
    })
    };
// 当前展开的行索引（新增）
const expandedRowKeys = ref([]); // 存储展开行的id（关键修正）
// 监听展开/折叠事件-点击哪个就展示哪个，相同就关闭
const handleExpandChange = (row) => {
    temp_desc.value = ''
    if(row.id===expandedRowKeys.value[0]){
        expandedRowKeys.value = [];   
    }else{
        expandedRowKeys.value = [row.id];  
    }
};
// table的颜色警告-如果用例存在变量定义但是没有添加ddt
const tableRowClassName = (row) => {
    console.log("row-ddt_param_data",row.row.ddt_param_data)
    console.log("row-param_data",JSON.parse(row.row.param_data))
    let ddt_param_data = row.row.ddt_param_data
    let param_data = JSON.parse(row.row.param_data)
    // 如果没有变量依赖且没有ddt则通过样式
    if(param_data.length===0 && ddt_param_data.length===0){
        console.log("颜色生效")
        return 'success-row'
    }
    // 如果有变量依赖且没有ddt则警告
    if(param_data.length>0 && ddt_param_data.length===0){
        console.log("颜色生效")
        return 'warning-row'
    }
    // 如果没有变量依赖但是有ddt则错误
    if(param_data.length===0 && ddt_param_data.length>0){
        console.log("颜色生效")
        return 'error-row'
    }
    // 如果有变量依赖且有ddt则通过
    if(param_data.length>0 && ddt_param_data.length>0){
        console.log("颜色生效")
        return 'success-row'
    }
}
// 获取标签类型
const getStatusType = (row) => {
  const paramData = JSON.parse(row.param_data);
  const ddtParamData = row.ddt_param_data;

  if (paramData.length === 0 && ddtParamData.length === 0) {
    return 'success'; // 无依赖且无DDT，视为正常（绿色）
  } else if (paramData.length > 0 && ddtParamData.length === 0) {
    return 'warning'; // 有依赖但无DDT，警告（黄色）
  } else if (paramData.length === 0 && ddtParamData.length > 0) {
    return 'error'; // 无依赖但有DDT，错误（红色）
  } else {
    return 'success'; // 有依赖且有DDT，正常（绿色）
  }
};
// 获取标签文案
const getStatusText = (row) => {
  const paramData = JSON.parse(row.param_data);
  const ddtParamData = row.ddt_param_data;

  if (paramData.length === 0 && ddtParamData.length === 0) {
    return '正常';
  } else if (paramData.length > 0 && ddtParamData.length === 0) {
    return '缺少DDT';
  } else if (paramData.length === 0 && ddtParamData.length > 0) {
    return '无效DDT';
  } else {
    return '已配置';
  }
};
</script>
<style>
.el-table .warning-row {
  --el-table-tr-bg-color: var(--el-color-warning-light-9);
}
.el-table .success-row {
  --el-table-tr-bg-color: var(--el-color-success-light-9);
}
.el-table .error-row {
  --el-table-tr-bg-color: var(--el-color-error-light-9);
}
</style>