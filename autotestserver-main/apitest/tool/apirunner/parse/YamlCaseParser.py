# -*- coding: utf-8 -*-
import copy, os, yaml
import re

from yamlinclude import YamlIncludeConstructor

from apitest.tool.apirunner.core.globalContext import g_context


# 获取以context开头 .yaml结尾的内容，并放入到公共参数中去!
# 公共参数处理逻辑


def load_context_from_yaml(folder_path):
    """"
    这个方法是要拿出文件夹里的context变量参数，并添加进全局上下文中
    """
    try:
        # 这时folder_path仍是绝对路径的文件夹，并且+了context.yaml，文件夹里的文件，其中一个就是context.yaml，所以他才用绝对路径拼接，相当于取出这个文件了
        yaml_file_path = os.path.join(folder_path, 'context.yaml')
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            #yaml.load(file, Loader=yaml.FullLoader)：这行代码使用 PyYAML 库的 load 函数将文件内容解析为 Python 对象。参数解释如下：
            """
            file：是前面打开的文件对象，
            load 函数会从该文件对象中读取内容。
            Loader=yaml.FullLoader：使用 PyYAML 库的 load 函数将文件内容解析为 Python 对象，存储在 data 中。
            """
            data = yaml.load(file, Loader=yaml.FullLoader)
            print("加载环境变量context.yaml文件内容:", data)
            #如果解析结果 data 不为空，则调用 g_context() 函数返回的对象的 set_by_dict 方法
            # g_context().set_by_dict其作用是把传入的字典 dic 里的键值对更新到全局上下文的字典 _dic 中
            if data: g_context().set_by_dict(data)
    except Exception as e:
        print(f"装载yaml文件错误: {str(e)}")
        return False


def load_yaml_files(config_path):
    yaml_caseInfos = []
    # 扫描 文件夹下的yaml-    suite_folder = os.path.join(config_path)其实没干什么因为没有明确要拼接的内容
    suite_folder = os.path.join(config_path)
    # 带着文件夹绝对路径进入-处理context变量参数
    load_context_from_yaml(suite_folder)
    #这段代码会遍历 suite_folder 文件夹下的所有文件，筛选出文件名以 .yaml 结尾，并且文件名以数字开头且由下划线 _ 分隔的文件，
    # 然后将这些文件的数字前缀转换为整数，并与文件名组成元组，最终返回一个包含这些元组的列表。
    #最后提取的应该是数字开头_的文件，这个文件夹所有会以数字开头（用例文件），
    # ，我理解这里其实要顺序的取出数据，
    # 如果文件夹有多个数字开头的文件，那么他会取出多个并标记顺序头，并且此时file_names是一个列表套元祖[(1, '1_test.yaml'), (2, '2_example.yaml')]
    file_names = [(int(f.split("_")[0]), f) for f in os.listdir(suite_folder) if
                  f.endswith(".yaml") and f.split("_")[0].isdigit()]
    #这句是将列表进行排序，由数字从小到大排序
    file_names.sort()
    #所以这句话是将排序后的数字前缀删除掉，已经排好顺序就不需要这个前缀了，此时变成了['1_test.yaml', '2_example.yaml']
    file_names = [f[-1] for f in file_names]
    # 获取 suite 文件夹下的所有 YAML 文件，并按文件名排序
    #遍历处理后的文件，并且将所有文件进行了加上一句处理的文件文件夹绝对路径+文件，这样就知道了每一个文件的具体绝对路径地址
    for file_name in file_names:
        file_path = os.path.join(suite_folder, file_name)
        with open(file_path, "r", encoding='utf-8') as rfile:
            #使用 yaml.full_load() 函数将打开的文件内容解析为 Python 对象。由于这些文件是 YAML 格式的，
            # 该函数会将 YAML 文本转换为对应的 Python 数据结构（如字典、列表等），存储在 caseinfo 变量中
            caseinfo = yaml.full_load(rfile)
            # 解析完成后加入到列表并返回处理后的文件
            yaml_caseInfos.append(caseinfo)

    return yaml_caseInfos

# 此方法接收一个文件夹的绝对路径 config_path 作为参数，
# 然后扫描该路径下所有符合条件的 YAML 文件，对每个文件中的测试用例信息进行处理，
# 最终生成测试用例列表和对应的用例名称列表。
def yaml_case_parser(config_path):
    #这段代码的主要目的是处理测试用例的参数化数据（ddts），
    # 并将其与测试用例的上下文（context）合并，
    # 最终生成多个独立的测试用例-返回的数据case_infos里是没有ddts了。他们都在context中
    case_infos = []  #测试用例信息
    case_names = []  #测试用例名称

    # 获取符合条件的 YAML 文件列表-带着文件夹绝对路径进入-这里将文件夹的context文件加到了全局上下文，并将用例文件处理了顺序+绝对路径并返回
    yaml_caseInfos = load_yaml_files(config_path)

    for caseinfo in yaml_caseInfos:
        # 读取 DDTS 节点 --- 生成多组测试用例-读取用例yml结构里的ddtskey
        ddts = caseinfo.get("ddts", [])
        #若 ddts 列表不为空，就把 caseinfo 字典里的 ddts 键移除。
        if len(ddts) > 0:
            caseinfo.pop("ddts")
        #当 ddts 列表为空时，直接把 caseinfo 添加到 case_infos 列表里，
        # 并且把 caseinfo 的 desc 键的值（或者文件名 yfile）添加到 case_names 列表中
        if len(ddts) == 0:
            case_infos.append(caseinfo)
            case_names.append(caseinfo.get("desc", caseinfo))
        # 当有ddts时执行
        else:
            # 循环生成多个用例执行对象，保存起来。
            for ddt in ddts:
                print("此时的caseinfo=", caseinfo['desc'])
                match = re.search(r'_(\d+)$', caseinfo['desc'])
                match = match.group(1)
                print("此时的match=", match)
                #使用 copy.deepcopy() 函数对原始的测试用例信息 caseinfo 进行深拷贝，
                # 生成一个新的测试用例对象 new_case。
                # 深拷贝的作用是确保新的测试用例对象和原始对象相互独立，对新对象的修改不会影响到原始对象。
                #此时new_case是一个新的单独的用例结构对象
                new_case = copy.deepcopy(caseinfo)
                # 将数据读取后更新到 context 里面-每个用例都可能有自己的context，这是用例的上下文变量
                context = new_case.get("context", {})
                # 将获取的context加进ddt中，如果相同就修改，没有就新增
                ddt.update(context)
                # 将修改后ddt再次放回用例的context中，此时context是聚合了context原来的值与ddt的值
                new_case.update({"context": ddt})
                # 将新用例加到case_infos列表中
                case_infos.append(new_case)
                # 将新用例的名称加入到case_names中
                case_names.append(ddt["desc"]+'_'+match)
#我再补充一下，ddts就是实际的变量值，
    # 用例结构里有{{}}这种变量，他们要取的就是ddts，
    # 用例有多少个，与ddts数量相同，但是用例想取，就需要通过context（上下文取）
    # 所以将每个ddts的元素放进每个用例的context中
    return {
        "case_infos": case_infos,
        "case_names": case_names
    }
