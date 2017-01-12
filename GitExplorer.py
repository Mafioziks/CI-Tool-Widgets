import gitlab
import re

from Config import Config as Con

class GitExplorer:

    def __init__(self):
        con = Con()
        settings = con.get_settings()

        self.git = gitlab.Gitlab(
            url=settings['gitlab'],
            http_username=settings['username'],
            http_password=settings['password'],
            email=settings['username'],
            password=settings['password']
        )
        self.git.auth()

    def get_mr_title(self, project, mr):
        """Get title for merge request."""
        if project.startswith('git'):
            res = re.search(':(.+)\.git', project)
            if res is None or res.group(1) is None:
                return None
            project = res.group(1)

        res = re.search('\d+', mr)
        if res is None or res.group(0) is None:
            return None

        mr = int(res.group(0))

        g_project = self.git.projects.get(project)
        g_mr = self.git.project_mergerequests.list(
            project_id=g_project.id,
            state="opened"
        )

        for r_mr in g_mr:
            if r_mr.iid == mr:
                return r_mr.title

        return None

    def get_project_mrs(self, project):
        g_project = self.git.projects.get(project)
        return self.git.project_mergerequests.list(
            project_id=g_project.id,
            state="opened"
        )

    def get_mr_title_for_url(self, url, mr):
        res = re.search(':(.+)\.git', url)

        if res is not None and res.group(1) is not None:
            return self.get_mr_title(res.group(1), mr)
        else:
            return None


if __name__ == '__main__':
    print('Not self running programm :(')
