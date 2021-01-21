# jira相关
JIRA_SERVER = "https://easystack.atlassian.net"
JIRA_USERNAME = "lifeng.wang@easystack.cn"
JIRA_PASSWORD = "3M1l91Hivjo4O35PJt4u31FA"
WIKI_SERVER = 'https://easystack.atlassian.net/wiki/'

# jira查询语句
JQL_ECSDESK_PROBLEM = "project = ECSDESK  AND " \
              "issuetype in (Incident, Problem, 'Service Request') AND " \
              "created >= 2021-01-14 AND created <= 2021-01-16 AND " \
              "status in (Closed, Completed, Done, Resolved, Canceled)"
JQL_ECSDESK_CHANGE = "project = ECSDESK AND issuetype = Change AND " \
                     "status in (Approved, Closed) AND " \
                     "created >= 2021-01-01 AND created <= 2021-01-21"
JQL_ECSDESK_TASK = 'created >= 2021-01-01 AND created <= 2021-01-21 AND ' \
                   'project = ECSDESK AND issuetype = Task AND ' \
                   'status in (Done, Open, Pending, Reopened, "Work in progress")'
JQL_CSE = "project = CSE AND issuetype = 环境详细信息"


# 生成的cse数据文件名称
CSE_DATA_FILE = 'cse_data.json'

# 前端页面所用模板
PROBLEM_TEMPLATE_NAME = 'case_problem_per_month.j2'
CHANGE_TEMPLATE_NAME = 'case_change_per_month.j2'
TASK_TEMPLATE_NAME = 'case_task_per_month.j2'
