import json
from case_per_month.jiratool import jiratool
from case_per_month.jiratool import jira_settings


def get_cse_data():
    # 将所有的cse写入json文件
    cse_issue_month = jiratool.search_all_issue(jira_settings.JQL_CSE)
    cse_l = []
    for issue in cse_issue_month:
        cse_dict = {}
        cse_key = issue.key
        prefecture_level_city = issue.fields.customfield_11338

        cse_dict['cse'] = cse_key
        cse_dict['prefecture_level_city'] = prefecture_level_city

        cse_l.append(cse_dict)
    return cse_l


# 将cse数据写入到文件
with open(jira_settings.CSE_DATA_FILE, "w", encoding="utf-8") as f:
    f.write(json.dumps(get_cse_data()))
