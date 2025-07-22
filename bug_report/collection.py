from github import Github
from github import Auth
import os
# 获取issues
def get_issues(repo_url,token,state):
    auth=Auth.Token(token)
    g=Github(auth=auth)
    repo=g.get_repo(repo_url)
    issues=repo.get_issues(state=state)
    return issues
token="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"
repo_url="duckdb/duckdb"
closed_issues=get_issues(repo_url,token,state="all")

def file_exists(directory, filename):
    file_path = os.path.join(directory, filename)
    return os.path.isfile(file_path)

for closed_issue in closed_issues:
    flag = 1
    
    # for label in closed_issue.labels:
    #     if label.name == "bug":
    #         flag = 1
    #         break
    if flag:
        idarray = closed_issue.url.split("/")
        id = idarray[len(idarray)-1]
        
        filename = id + ".txt"
        if file_exists("/mnt/data1/home/tiancl/llm-sql-generation/bug_report/duckdb_bug_report", filename):
             print("文件"+id+"已存在")
             continue
        content = f"ID: {id}\n"
        content += f"Title: {closed_issue.title}\n"
        content += "Description:\n" + (closed_issue.body or "No description provided")
        print("id:"+id)
        print("title:"+closed_issue.title)

        
        filepath = "/mnt/data1/home/tiancl/llm-sql-generation/bug_report/duckdb_bug_report/" + filename
        with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
