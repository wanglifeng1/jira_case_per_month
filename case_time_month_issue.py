#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jira import JIRA
import re
import json
from jinja2 import Environment, FileSystemLoader
from atlassian import Confluence
import datetime
import os
import configparser

cf = configparser.ConfigParser()
cf.read("config")
server = "https://easystack.atlassian.net"
jira_username = cf.get("JIRA", "username")
jira_password = cf.get("JIRA", "password")
wiki_username = cf.get("WIKI", "username")
wiki_password = cf.get("WIKI", "password")
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
# jira连接对象
jc = JIRA(server=server, basic_auth=(jira_username, jira_password))
day = "-" + str(int(datetime.datetime.now().strftime('%d'))) + "d"
year = datetime.datetime.now().strftime('%Y')
month = datetime.datetime.now().strftime('%m')

jql_ecsdesk = "project = ECSDESK  AND " \
              "issuetype in (Incident, Problem, 'Service Request') AND " \
              "created >= 2021-01-14 AND created <= 2021-01-15 AND " \
              "status in (Closed, Completed, Done, Resolved, Canceled)"
jql_cse = "project = CSE AND issuetype = 环境详细信息"


def search_all_issue(client, search_str):
    block_size = 100
    block_num = 0
    issues = []
    while True:
        start_idx = block_num * block_size
        part_issues = client.search_issues(search_str, start_idx, block_size)
        if len(part_issues) == 0:
            break
        block_num += 1
        issues.extend(part_issues)
    return issues


def delete_blank(value):
    """
    删除空行
    :param value:
    :return:
    """
    a = ''
    try:
        a = "".join(value.split())
    except Exception:
        a = ''
    return a


def get_component(issue):
    """
    获取 组件 字段    如 ceph/network/等
    :param issue:
    :return:
    """
    component = ''
    for i in issue.raw["fields"]["components"]:
        component = i['name'] + ', ' + component
    component = component[:-2]
    return component


def get_result(issue):
    """
    获取处理结果的字段  如 产品问题、环境问题
    :param issue:
    :return:
    """
    result = ''
    try:
        result = issue.raw["fields"]["customfield_11100"]['value']
    except Exception:
        result = ''
    return result


def get_epic_link(issue):
    """
    获取epic_linke
    :param issue:
    :return:
    """
    result = ''
    try:
        result_l = issue.raw["fields"]["customfield_10900"]
        for result in result_l:
            result = result['name']
    except Exception:
        result = ''
    return result


def get_cse(issue):
    """
    获取epic_linke
    :param issue:
    :return:
    """
    result = ''
    try:
        result_l = issue.raw["fields"]["customfield_10007"]
        for result in result_l:
            result = result['name']
    except Exception:
        result = ''
    return result


def make_cse_env_num(cse_num):
    res = cse_num.split('-')
    num = int(res[1]) + 1
    cse_env_nu = 'CSE-' + str(num)
    return cse_env_nu


def create_data_escdesk(issues, tag):
    data1 = []
    for i in issues:
        k = {}
        ecsdesk_key = i.key  # 获取issue名字
        ecsdesk_summary = i.fields.summary
        # ecsdesk_summary = re.sub(r'[~!@#$%&+-<>]', ' ', ecsdesk_summary)
        ecsdesk_component = get_component(i)
        ecsdesk_status = i.raw["fields"]['status']['name']
        assigneer = i.raw["fields"]["assignee"]['displayName']
        reporter = i.raw["fields"]["reporter"]["displayName"]
        ecsdesk_epic_link = get_epic_link(i)
        cse_num = i.raw["fields"]["customfield_10007"]
        ecsdesk_result = get_result(i)
        ecsdesk_create = i.fields.created[0:19]
        ecsdesk_create_new = datetime.datetime.strptime(ecsdesk_create, '%Y-%m-%dT%H:%M:%S')
        ecsdesk_resolve = i.fields.updated[0:19]
        ecsdesk_resolve_new = datetime.datetime.strptime(ecsdesk_resolve, '%Y-%m-%dT%H:%M:%S')
        cesdesk_days = (ecsdesk_resolve_new - ecsdesk_create_new).days
        ecsdesk_time = round(
            float((ecsdesk_resolve_new - ecsdesk_create_new).seconds) / float(24 * 3600) + cesdesk_days, 2)

        ecs_key = ''
        ecs_create = ''
        ecs_resolve = ''
        ecs_time = ''
        for j in i.fields.issuelinks:
            links = j.raw.get("inwardIssue", '')
            if not links:
                continue
            key = links['key']
            if 'ECS-' in key and "clone" in j.raw['type']['outward']:
                ecs_key = key
                issue = jc.issue(ecs_key)
                ecs_create = issue.fields.created[0:19]
                ecs_create_new = datetime.datetime.strptime(ecs_create, '%Y-%m-%dT%H:%M:%S')
                try:
                    ecs_resolve = issue.fields.resolutiondate[0:19]
                    ecs_resolve_new = datetime.datetime.strptime(ecs_resolve, '%Y-%m-%dT%H:%M:%S')
                    ecs_days = (ecs_resolve_new - ecs_create_new).days
                    ecs_time = round(
                        float((ecs_resolve_new - ecs_create_new).seconds) / float(24 * 3600) + ecs_days, 2)
                except Exception:
                    ecs_resolve = ''
                    ecs_time = ''
        k['month'] = i.fields.resolutiondate[5:7]
        k['ecsdesk_key'] = ecsdesk_key
        k['ecsdesk_summary'] = delete_blank(ecsdesk_summary)
        k['ecsdesk_component'] = ecsdesk_component
        k['ecsdesk_status'] = ecsdesk_status
        k['assigneer'] = assigneer

        k['reporter'] = reporter
        k['ecsdesk_epic_link'] = ecsdesk_epic_link
        k['cse'] = make_cse_env_num(cse_num)
        k['ecsdesk_result'] = ecsdesk_result
        k['ecsdesk_create'] = ecsdesk_create
        k['ecsdesk_resolve'] = ecsdesk_resolve
        k['ecsdesk_time'] = str(ecsdesk_time)
        k['ecs_key'] = ecs_key
        k['ecs_create'] = ecs_create
        k['ecs_resolve'] = ecs_resolve
        k['ecs_time'] = str(ecs_time)
        data1.append(k)

    # 按月份将data排序
    data = sorted(data1, key=lambda k: k['month'])
    return data1


def get_body(issues, tag):
    """
    根据获取的数据，填充模板，生成html文件
    :param issues:
    :param tag:
    :return:
    """
    env = Environment(loader=FileSystemLoader(searchpath=CUR_DIR))
    template = env.get_template('case_time_%s.j2' % tag)
    output_data = get_data()
    content = template.render(data=output_data)
    return content


def get_pageid(title):
    page = confluence.get_page_by_title('ESK', title=title)
    if page:
        page_id = page['id']
    else:
        page = confluence.create_page('ESK', title, body='',
                                      parent_id='402489425', type='page', representation='storage')
        page_id = page['id']
    return page_id


confluence = Confluence(
    url='https://easystack.atlassian.net/wiki/',
    username=wiki_username,
    password=wiki_password)

# title_month = "问题解决时间统计(%s年%s月)" % (year, month)


ecsdesk_issue_month = search_all_issue(jc, jql_ecsdesk)
escdesk_data = create_data_escdesk(ecsdesk_issue_month, tag='month')

# 将所有的cse写入json文件
# cse_issue_month = search_all_issue(jc, jql_cse)
# cse_l = []
# for issue in cse_issue_month:
#     cse_dict = {}
#     cse_key = issue.key
#     prefecture_level_city = issue.fields.customfield_11338
#     cse_dict['cse'] = cse_key
#     cse_dict['prefecture_level_city'] = prefecture_level_city
#     cse_l.append(cse_dict)
#
#
# with open("cse_data.json", "w", encoding="utf-8") as f:
#     f.write(json.dumps(cse_l))

# 从json文件读取project为cse的相关配置
with open('case_per_month/cse_data.json', 'r', encoding='utf-8') as f:
    cse_data = json.loads(f.read())


# 将escdesk和cse列表合并成一个
def get_data():
    l = []
    for i in escdesk_data:
        cse = i['cse']
        for j in cse_data:
            cse_nu = j['cse']
            if cse_nu == cse:
                data = dict(i, **j)
                l.append(data)
    return l


# title_fy20_data_source = "test"
confluence.update_page(
    #page_id=get_pageid(title_month),
    page_id=904986625,
    title="2021-1-16",
    body=get_body(ecsdesk_issue_month, tag='month'))


# title_all = "问题展示 - 问题解决时间统计（按月)"
# ecsdesk_issue_all = search_all_issue(jc, "project = ECSDESK  AND \
#    issuetype in (Incident, problem, 'Service Request') AND \
#    created >= 2020-03-01 AND resolutiondate >= 2020-03-01")

# confluence.update_page(
#    page_id=get_pageid(title_all),
#    title=title_all.decode('utf-8'),
#    body=get_body(ecsdesk_issue_all, tag='all'))
