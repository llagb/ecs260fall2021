from github import Github
import os
from pprint import pprint
import datetime
import csv
import json
import requests # For checking the http(s) head response code

from files_changed_count_fetcher import get_files_changed_count


class CollectDataSet:
    def __init__(self):
        self.token ='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'
        self.get_api_token()

    def get_api_token(self):
        #self.token = os.getenv('GITHUB_TOKEN')
        self.git_hub_obj = Github(self.token)

    def read_project_names(self, filename):
        with open(filename) as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            project_dict = {}
            project_count = 0
            skipper_count = 0
            for row in csv_reader:
                if row[1] == 'Retired':
                    project_count += 1

                    if not row[2]:
                        project_url = row[0].replace('https://github.com/', '')
                    else:
                        project_url = row[2].replace('https://github.com/', '')

                    print("Project : ", project_count, project_url)
                    project_dict[project_url] = {}

                    if project_count == 1:
                        if project_count % 5 == 0:
                            print("CheckPoint")
                            #pass
                        try:

                            repo = self.git_hub_obj.get_repo(project_url)
                            forks = repo.get_forks()
                            total_fork_count = forks.totalCount
                            fork_count_within_time = 0
                            incubation_start_date = datetime.datetime.strptime(row[3], '%m/%d/%y')
                            incubation_end_date = datetime.datetime.strptime(row[4], '%m/%d/%y')
                            print("total_fork_count: ", total_fork_count)

                            if total_fork_count <= 3000:

                                fork_counter = 0
                                for each_fork in forks:
                                    fork_counter += 1
                                    print("fork_count : ", fork_counter, each_fork.full_name)
                                    # ----------------Head of Debugged Section2 by Lynden----------------
                                    # Important fix...
                                    # This means the fork is not retrieving any page, http(s) response
                                    # code is 404 or other 400+ code
                                    if requests.head(each_fork.html_url).status_code >= 400:
                                        continue
                                    # ----------------Tail of Debugged Section2 by Lynden----------------
                                    if incubation_start_date <= each_fork.created_at <= incubation_end_date:

                                        project_dict[project_url][each_fork.full_name] = {}
                                        fork_count_within_time += 1
                                        print("fork_count_within_time : ", fork_count_within_time)
                                        # ----------------Head of Debugged Section3 by Lynden----------------
                                        # Make a new variable, which will be used twice later. This can make
                                        # fetching URLs more reliable under the stress of fetching tons of URLs
                                        # One for the following and the other one for the loop
                                        forkCommits_within_incubation = each_fork.get_commits(
                                            since=datetime.datetime.strptime(row[3], '%m/%d/%y'),
                                            until=datetime.datetime.strptime(row[4], '%m/%d/%y'))
                                        # ----------------Tail of Debugged Section3 by Lynden----------------
                                        commit_count_within_incubation = forkCommits_within_incubation.totalCount

                                        project_dict[project_url][each_fork.full_name]["watchers_count"] = \
                                            each_fork.subscribers_count
                                        project_dict[project_url][each_fork.full_name]["star_count"] = \
                                            each_fork.subscribers_count
                                        project_dict[project_url][each_fork.full_name]["branches_count"] = \
                                            each_fork.get_branches().totalCount
                                        project_dict[project_url][each_fork.full_name]["total_commits_count"] = \
                                            each_fork.get_commits().totalCount
                                        project_dict[project_url][each_fork.full_name]["commits_count_within_incubation"] = \
                                            commit_count_within_incubation

                                        print("each_fork.get_commits().totalCount", each_fork.get_commits().totalCount)

                                        # Commits related feature extraction each fork:
                                        commits_time_counter = 0
                                        total_no_of_times_files_modified = 0
                                        total_no_of_lines_added = 0
                                        total_no_of_lines_deleted = 0

                                        for commit in forkCommits_within_incubation:
                                            commits_time_counter += 1
                                            # ----------------Head of Debugged Section1 by Lynden----------------
                                            # Added the checking conditions for the variables.
                                            files_modified = 0
                                            if commit != None and commit.html_url != None:
                                                # The get_files_changed_count() is fixed in its corresponding .py file.
                                                files_modified = get_files_changed_count(commit.html_url)
                                            print("commits_time_counter: ", commits_time_counter)
                                            total_no_of_times_files_modified += files_modified
                                            if commit != None and commit.stats != None:
                                                if commit.stats._additions != None and commit.stats._additions.value != None:
                                                    total_no_of_lines_added += commit.stats._additions.value
                                                if commit.stats._deletions != None and commit.stats._deletions.value != None:
                                                    total_no_of_lines_deleted += commit.stats._deletions.value
                                            # ----------------Tail of Debugged Section1 by Lynden----------------
                                        project_dict[project_url][each_fork.full_name]['total_no_of_times_files_modified'] = \
                                            total_no_of_times_files_modified
                                        project_dict[project_url][each_fork.full_name]['total_no_of_lines_added'] = \
                                            total_no_of_lines_added
                                        project_dict[project_url][each_fork.full_name]['total_no_of_lines_deleted'] = \
                                            total_no_of_lines_deleted
                                print('fork_count_within_time', fork_count_within_time)
                                project_dict[project_url]['total_fork_count']= total_fork_count
                                project_dict[project_url]['watchers_count'] = repo.subscribers_count
                                project_dict[project_url]['star_count'] = repo.stargazers_count
                                project_dict[project_url]['open_issues_count'] = repo.open_issues_count
                                project_dict[project_url]['size'] = repo.size
                                project_dict[project_url]['fork_count_within_time'] = fork_count_within_time

                            else:
                                skipper_count += 1
                                print(">>>>>>>Skipping extraction>>>>>>>>>", skipper_count)

                        except Exception as ex:
                            print(ex)
                            print("Check URL >>>>>>", project_url, total_fork_count)
        result = json.dumps(project_dict, indent=4)
        json_file = open("data_set2.json", "w")
        json_file.write(result)
        json_file.close()
        return



class_obj = CollectDataSet()
class_obj.read_project_names(filename='retired_projects_updated_urls.csv')
