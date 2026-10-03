import { createRouter, createWebHashHistory } from "vue-router";
import Cookies from "universal-cookie";

import NotFound from "~/views/404.vue";
import admin from "~/views/home/admin.vue";
import Index from "~/views/home/index.vue";
import login from "~/views/login/login.vue";
import userList from "~/views/users/userList.vue";
import PlatformSettings from "~/views/platform/PlatformSettings.vue";

import ApiProjectList from "~/views/apitest/project/ApiProjectList.vue";
import ApiProjectForm from "~/views/apitest/project/ApiProjectForm.vue";
import ApiProjectFormedit from "~/views/apitest/project/ApiProjectFormedit.vue";
import ApiModuleList from "~/views/apitest/module/ApiModuleList.vue";
import ApiModuleForm from "~/views/apitest/module/ApiModuleForm.vue";
import ApiModuleFormedit from "~/views/apitest/module/ApiModuleFormedit.vue";
import ApiInfoList from "~/views/apitest/apiinfo/ApiInfoList.vue";
import ApiInfoForm from "~/views/apitest/apiinfo/ApiInfoForm.vue";
import ApiInfoFormedit from "~/views/apitest/apiinfo/ApiInfoFormedit.vue";
import ApiCollectionList from "~/views/apitest/collection/ApiCollectionList.vue";
import ApiCollectionForm from "~/views/apitest/collection/ApiCollectionForm.vue";
import Apitimetasklist from "~/views/apitest/timetask/Apitimetasklist.vue";

import WebProjectList from "~/views/webtest/project/WebProjectList.vue";
import WebProjectForm from "~/views/webtest/project/WebProjectForm.vue";
import WebBrowserList from "~/views/webtest/browserRemote/WebBrowserList.vue";
import WebBrowserForm from "~/views/webtest/browserRemote/WebBrowserForm.vue";
import WebKeyWordList from "~/views/webtest/keyword/WebKeyWordList.vue";
import WebKeyWordForm from "~/views/webtest/keyword/WebKeyWordForm.vue";
import WebInfoList from "~/views/webtest/webinfo/WebInfoList.vue";
import WebInfoForm from "~/views/webtest/webinfo/WebInfoForm.vue";
import WebCollectionInfoList from "~/views/webtest/collection/WebCollectionInfoList.vue";
import WebCollectionInfoForm from "~/views/webtest/collection/WebCollectionInfoForm.vue";
import WebTimeTaskList from "~/views/webtest/webtimetask/WebTimeTaskList.vue";
import WebFileList from "~/views/webtest/webfile/WebFileList.vue";
import WebQualityList from "~/views/webtest/quality/WebQualityList.vue";
import WebOperationTypeList from "~/views/webtest/keyword/WebOperationTypeList.vue";
import xy from "~/views/home/xy.vue";

const routes = [
  {
    path: "/",
    component: admin,
    meta: { title: "工作台" },
    children: [
      { path: "/", component: Index, meta: { title: "仪表盘" } },
      { path: "/users", component: userList, meta: { title: "用户管理", requiresAdmin: true } },
      { path: "/platform-settings", component: PlatformSettings, meta: { title: "平台设置", requiresAdmin: true } },
      { path: "/ApiProjectList", component: ApiProjectList, meta: { title: "接口项目" } },
      { path: "/ApiProjectForm", component: ApiProjectForm, meta: { title: "新增接口项目" } },
      { path: "/ApiProjectFormedit", component: ApiProjectFormedit, meta: { title: "编辑接口项目" } },
      { path: "/ApiModuleList", component: ApiModuleList, meta: { title: "接口模块" } },
      { path: "/ApiModuleForm", component: ApiModuleForm, meta: { title: "新增接口模块" } },
      { path: "/ApiModuleFormedit", component: ApiModuleFormedit, meta: { title: "编辑接口模块" } },
      { path: "/ApiInfoList", component: ApiInfoList, meta: { title: "接口用例" } },
      { path: "/ApiInfoForm", component: ApiInfoForm, meta: { title: "新增接口用例" } },
      { path: "/ApiInfoFormedit", component: ApiInfoFormedit, meta: { title: "编辑接口用例" } },
      { path: "/ApiCollectionList", component: ApiCollectionList, meta: { title: "接口集合" } },
      { path: "/ApiCollectionForm", component: ApiCollectionForm, meta: { title: "编辑接口集合" } },
      { path: "/Apitimetasklist", component: Apitimetasklist, meta: { title: "接口定时任务" } },
      { path: "/WebProjectList", component: WebProjectList, meta: { title: "Web项目" } },
      { path: "/WebProjectForm", component: WebProjectForm, meta: { title: "编辑Web项目" } },
      { path: "/WebBrowserList", component: WebBrowserList, meta: { title: "浏览器池" } },
      { path: "/WebBrowserForm", component: WebBrowserForm, meta: { title: "编辑浏览器池" } },
      { path: "/WebKeyWordList", component: WebKeyWordList, meta: { title: "关键字管理" } },
      { path: "/WebKeyWordForm", component: WebKeyWordForm, meta: { title: "编辑关键字" } },
      { path: "/WebInfoList", component: WebInfoList, meta: { title: "Web用例" } },
      { path: "/WebInfoForm", component: WebInfoForm, meta: { title: "编辑Web用例" } },
      { path: "/WebCollectionInfoList", component: WebCollectionInfoList, meta: { title: "Web集合" } },
      { path: "/WebCollectionInfoForm", component: WebCollectionInfoForm, meta: { title: "编辑Web集合" } },
      { path: "/WebTimeTaskList", component: WebTimeTaskList, meta: { title: "Web定时任务" } },
      { path: "/WebFileList", component: WebFileList, meta: { title: "文件中心" } },
      { path: "/WebOperationTypeList", component: WebOperationTypeList, meta: { title: "操作类型" } },
      { path: "/WebQualityList", component: WebQualityList, meta: { title: "质量看板" } },
      { path: "/xy", component: xy, meta: { title: "坐标工具" } },
    ],
  },
  { path: "/login", component: login },
  { path: "/:pathMatch(.*)*", component: NotFound },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach((to, _from, next) => {
  if (!to.meta.requiresAdmin) {
    next();
    return;
  }

  const cookies = new Cookies();
  if (cookies.get("l-role") === "admin") {
    next();
    return;
  }

  next("/");
});

export default router;
