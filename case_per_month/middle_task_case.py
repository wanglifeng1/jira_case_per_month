import os
import datetime

from atlassian import Confluence
from jinja2 import Environment, FileSystemLoader

from case_per_month.jiratool import jiratool


# 当前文件路径
CUR_DIR = os.path.dirname(os.path.abspath(__file__))


def get_mon(issue):
    try:
        month = issue.fields.resolutiondate[5:7]
    except Exception as e:
        print(e)
        month = ''
    return month


def create_ecsdesk_data(issues):
    """
    构造从ecsdesk issue获取的数据
    :param issues: ecsdesck project的所有issue
    :return: 返回列表，里边是一个个字典
    """
    data = []
    for issue in issues:
        # print(issue.raw['fields'])
        ecsdesk_dict = {}
        ecsdesk_dict['ecsdesk_key'] = issue.key
        ecsdesk_dict['month'] = get_mon(issue)
        ecsdesk_dict['summary'] = issue.fields.summary
        ecsdesk_dict['components'] = jiratool.get_components(issue)
        ecsdesk_dict['status'] = issue.fields.status.name
        ecsdesk_dict['assignee'] = issue.fields.assignee.displayName
        ecsdesk_dict['reporter'] = issue.fields.reporter.displayName
        ecsdesk_dict['epic_link'] = jiratool.get_epic_link(issue)
        ecsdesk_dict['cse_num'] = issue.fields.customfield_10007
        ecsdesk_dict['cse'] = jiratool.make_cse_env_num(ecsdesk_dict['cse_num'])
        ecsdesk_dict['category'] = jiratool.get_result(issue)
        ecsdesk_dict['created_time'] = issue.fields.created[0:19]

        data.append(ecsdesk_dict)

    return data


def get_data(l1, l2):
    """
    将escdesk和cse列表合并成一个
    :return:
    """
    l = []
    for i in l1:
        cse = i['cse']
        for j in l2:
            cse_nu = j['cse']
            if cse_nu == cse:
                data = dict(i, **j)
                l.append(data)
    return l


def get_body(l1, l2, template):
    """
    根据获取的数据，填充模板，生成html文件
    :param issues:
    :param tag:
    :return:
    """
    env = Environment(loader=FileSystemLoader(searchpath=CUR_DIR))
    template = env.get_template(template)
    output_data = get_data(l1, l2)
    content = template.render(data=output_data)
    return content


def get_issues(jql):
    # 获取所有issue对象 列表
    issues_ecsdesk = jiratool.search_all_issue(jql)
    return issues_ecsdesk


def confluence(wiki_server, username, password):
    conflu = Confluence(wiki_server, username, password)
    return conflu


