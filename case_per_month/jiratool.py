# 封装jira一些方法
import sys

from jira import JIRA

from case_per_month import jira_settings


class JiraTool(object):
    def __init__(self, server, username, password, maxResults=50):
        self.server = server
        self.basic_auth = (username, password)
        # issues查询的最大值
        self.maxResults = maxResults

    def login(self):
        self.jira = JIRA(server=self.server, basic_auth=self.basic_auth)
        if self.jira == None:
            print('连接失败')
            sys.exit(-1)

    def get_projects(self):
        """
        获得jira 的所有项目
        :return:
        """
        return [(p.key, p.name, p.id) for p in self.jira.projects()]

    # def get_components(self, project):
    #     """
    #     获得某项目的所有模块
    #     :param project:
    #     :return:
    #     """
    #     return [(c.name, c.id) for c in self.jira.project_components(self.jira.project(project))]

    def create_component(self, project, compoment, description, leadUserName=None, assigneeType=None,
                         isAssigneeTypeValid=False):
        """
        # 创建项目模块
        :param project: 模块所属项目
        :param compoment:模块名称
        :param description:模块描述
        :param leadUserName:
        :param assigneeType:
        :param isAssigneeTypeValid:
        :return:
        """
        components = self.jira.project_components(self.jira.project(project))
        if compoment not in [c.name for c in components]:
            self.jira.create_component(compoment, project, description=description, leadUserName=leadUserName,
                                       assigneeType=assigneeType, isAssigneeTypeValid=isAssigneeTypeValid)

    def create_issue(self, project, compoment, summary, description, assignee, issuetype, priority='Medium'):
        """
        创建提交issue
        :param project: 项目
        :param issuetype: 问题类型，Task
        :param summary: 主题
        :param compoment: 模块
        :param description: 描述
        :param assignee: 经办人
        :param priority: 优先级
        :return:
        """
        issue_dict = {
            'project': {'key': project},
            'issuetype': {'id': issuetype},
            'summary': summary,
            'components': [{'name': compoment}],
            'description': description,
            'assignee': {'name': assignee},
            'priority': {'name': priority},
        }
        return self.jira.create_issue(issue_dict)

    def delete_issue(self, issue):
        """
        删除issue
        :param issue:
        :return:
        """
        issue.delete()

    def update_issue_content(self, issue, issue_dict):
        """
        更新issue内容
        :param issue:
        :param issue_dict:
            issue_dict = {
                'project': {'key': project},
                'issuetype': {'id': issuetype},
                'summary': summary,
                'components': [{'name': compoment}],
                'description': description,
                'assignee': {'name': assignee},
                'priority': {'name': priority},
            }
        :return:
        """
        issue.update(fields=issue_dict)

    def update_issue_issuetype(self, issue, issuetype):
        """
        更新bug 状态
        :param issue:
        :param issuetype: 可以为id值如11，可以为值如'恢复开启问题'
        :return:
        """
        transitions = self.jira.transitions(issue)
        # print([(t['id'], t['name']) for t in transitions])
        self.jira.transition_issue(issue, issuetype)

    def search_all_issue(self, jql):
        block_size = 100
        block_num = 0
        issues = []
        while True:
            start_idx = block_num * block_size
            part_issues = self.jira.search_issues(jql, start_idx, block_size)
            if len(part_issues) == 0:
                break
            block_num += 1
            issues.extend(part_issues)
        return issues

    # def search_issues(self, jql):
    #     """
    #     查询bug
    #     :param jql: 查询语句，如"project=项目key AND component = 模块 AND status=closed AND summary ~标题 AND description ~描述"
    #     :return:
    #     """
    #     try:
    #         # maxResults参数是设置返回数据的最大值，默认是50。
    #         issues = self.jira.search_issues(jql, maxResults=self.maxResults)
    #     except Exception as e:
    #         print(e)
    #         sys.exit(-1)
    #     return issues

    def search_issue_content(self, issue, content_type):
        """
        获取issue 的相关信息
        :param issue:
        :param content_type:项目project; 模块名称components; 标题summary; 缺陷类型issuetype; 具体描述内容description; 经办人assignee; 报告人reporter; 解决结果resolution; bug状态status; 优先级priority; 创建时间created; 更新时间updated; 评论comments
        :return:
        """
        # 评论
        if content_type == 'comments':
            return [c.body for c in self.jira.comments(issue)]
        if hasattr(issue.fields, content_type):
            result = getattr(issue.fields, content_type)
            if isinstance(result, list):
                return [c.name for c in result if hasattr(c, 'name')]
            return result

    def get_issue_types(self):
        """
        获取所有issues类型
        :return:
        """
        issue_type_name = []
        issue_types = self.jira.issue_types()
        for issue_type in issue_types:
            issue_type_name.append(issue_type.name)
        return issue_type_name

    def get_components(self, issue):
        """
        获取组件字段
        :param issue: 每个issue
        :return:
        """
        for i in issue.fields.components:
            components = i.name
            return components

    def get_epic_link(self, issue):
        """
        获取epic_link字段
        :param issue: 每个issue
        :return:
        """
        for i in issue.fields.customfield_10900:
            epic_link = i.name
            return epic_link

    def make_cse_env_num(self, cse_num):
        try:
            res = cse_num.split('-')
            num = int(res[1]) + 1
            cse_env_nu = 'CSE-' + str(num)
        except Exception as e:
            cse_env_nu = ''
        return cse_env_nu

    def get_result(self, issue):
        """
        获取处理结果的字段  如 产品问题、环境问题
        :param issue:
        :return:
        """
        if issue.fields.customfield_11100:
            result = issue.fields.customfield_11100.value
        else:
            result = ''
        return result

    def get_resolve_time(self, issue):
        try:
            resolve_time = issue.fields.resolutiondate[0:19]
        except Exception as e:
            print(e)
            resolve_time = ''
        print(resolve_time)
        return resolve_time


jiratool = JiraTool(jira_settings.JIRA_SERVER, jira_settings.JIRA_USERNAME, jira_settings.JIRA_PASSWORD)
jiratool.login()
