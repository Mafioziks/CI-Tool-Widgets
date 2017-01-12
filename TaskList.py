#!/usr/bin/env python3


class TaskList():
    """Task list for Jenkins."""

    tasks = []
    __lock__ = False

    def is_locked(self):
        """Check if list is locked."""
        return self.__lock__

    def lock(self):
        """Lock TaskList."""
        self.__lock__ = True

    def unlock(self):
        """Unlock TaskList."""
        self.__lock__ = False

    def add_custom_task(self, info):
        """Add task with custom parameters."""
        while self.is_locked():
            pass

        self.lock()
        if isinstance(info, dict):
            if len(self.tasks) > 0:
                id = self.tasks[len(self.tasks) - 1]['id'] + 1
            else:
                id = 0
            info.update({'id': id})
            self.tasks.append(info)
        self.unlock()
        return id

    def add_task(self, status, name, tag, url, description):
        """Add task to TaskList as soon as it is unlocked."""
        while self.is_locked():
            pass

        self.lock()
        if len(self.tasks) > 0:
            id = self.tasks[len(self.tasks)-1]['id'] + 1
        else:
            id = 0
        self.tasks.append({
            "id": id,
            "status": status,
            "name": name,
            "tag": tag,
            "url": url,
            "description": description
        })
        self.unlock()
        return id

    def get_task(self, id):
        """Get task from TaskList."""
        while self.is_locked():
            pass

        result = dict()
        self.lock()
        for task in self.tasks:
            if task['id'] == id:
                result = task
        # if id in self.tasks:
        #     t = self.tasks[id]
        #     self.unlock()
        #     return t

        self.unlock()
        return result

    def update_task(self, id, status):
        """Update task from TaskList as soon as it is unlocked."""
        while self.is_locked():
            pass

        self.lock()
        for task in self.tasks:
            if task['id'] == id:
                task['status'] = status
        self.unlock()

    def remove_task(self, id):
        """Remove task from TaskList as soon as it is unlocked."""
        while self.is_locked():
            pass

        self.lock()
        for task in self.tasks:
            if task['id'] == id:
                self.tasks.remove(task)
        # if id in self.tasks:
        #     del self.tasks[id]
        self.unlock()

    def get_with_status(self, status):
        """Get tasks with specified status when TaskList is unloked."""
        while self.is_locked():
            pass

        self.lock()
        if self.tasks is None:
            self.unlock()
            return None

        result = list()
        for item in self.tasks:
            if item['status'] == status:
                result.append(item)

        self.unlock()
        return result

    def get_first_git_task(self):
        """Get first task which is in git."""
        while self.is_locked():
            pass

        self.lock()
        result = dict()
        for task in self.tasks:
            if self.tasks[task]['vcs'].startswidth('git'):
                result.update({task: self.tasks[task]})
                break
        self.unlock()
        return result

    def get_first_svn_task(self):
        """Get first task which is in svn."""
        while self.is_locked():
            pass

        self.lock()
        result = dict()
        for task in self.tasks:
            if not self.tasks[task]['vcs'].startswidth('git'):
                result.update({task: self.tasks[task]})
                break
        self.unlock()
        return result

    def empty(self):
        """Check if task list is empty."""
        while self.is_locked():
            pass

        self.lock()
        if self.tasks is None:
            self.unlock()
            return True

        self.unlock()
        return False

    def get_first_task_key(self):
        """Get first task."""
        while self.is_locked():
            pass

        self.lock()
        # print(self.tasks)
        print('Get first task key - depracated')
        # first_task_key = self.tasks[0]
        self.unlock()
        return None

    def get_first_task(self):
        """Get first task."""
        while self.is_locked():
            pass

        self.lock()
        result = next(iter(self.tasks or []), None)
        self.unlock()
        return result
