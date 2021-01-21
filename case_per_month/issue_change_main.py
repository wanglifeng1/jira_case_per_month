import os
import json

from case_per_month import jira_settings
from case_per_month.middle_change_case import confluence, get_body, create_ecsdesk_data, get_issues


if __name__ == '__main__':
    cf = confluence(jira_settings.WIKI_SERVER, jira_settings.JIRA_USERNAME, jira_settings.JIRA_PASSWORD)
    # ********************************** 注意：此处jql语句一定要替换 *************************************
    ecsdesk_data_list = create_ecsdesk_data(get_issues(jira_settings.JQL_ECSDESK_CHANGE))
    with open(jira_settings.CSE_DATA_FILE, 'r', encoding='utf-8') as f:
        cse_data_list = json.loads(f.read())

    # 更新confluence
    cf.update_page(
        # page_id=get_pageid(title_month),
        page_id=904986625,
        title="2021-1-16",
        body=get_body(ecsdesk_data_list, cse_data_list, jira_settings.CHANGE_TEMPLATE_NAME))
