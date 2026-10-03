import copy, os, yaml
from yamlinclude import YamlIncludeConstructor   #这是1.3版本的处理方式

def yaml_case_parser_alone(config_path):
    case_infos = []
    case_names = []
    YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader) #这是1.3版本的处理方式

    # 读取指定文件夹下的yaml文件
    for yfile in os.listdir(config_path):
        # 如果不是以test开头，yaml文件后缀，则不处理该文件
        if not yfile.startswith("test") or not yfile.endswith("yaml"):
            continue

        # 每个文件里面描述一个业务场景 - 一个场景可能由多组数据测试组成多个测试用例
        rfile = open(os.path.join(config_path, yfile), "r", encoding='utf-8')
        caseinfo = yaml.full_load(rfile)
        rfile.close()
        # 读取DDT节点 --- 生成多组测试用例，交个pytest去执行
        ddts = caseinfo.get("ddts", [])
        if len(ddts) > 0:
            caseinfo.pop("ddts")

        if len(ddts) == 0:
            case_infos.append(caseinfo)
            case_names.append(caseinfo.get("desc", yfile))
        else:
            # 循环生成多个用例执行对象，保存起来。
            for ddt in ddts:
                new_case = copy.deepcopy(caseinfo)
                # 将数据读取后更新到 context 里面
                context = new_case.get("context", {})
                ddt.update(context)
                new_case.update({"context": ddt})
                case_infos.append(new_case)
                case_names.append(ddt["desc"])

    return {
        "case_infos": case_infos,
        "case_names": case_names
    }