from random import randrange

from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):
    def on_start(self):
        self.keynames = []
    
    @task(2)
    def push(self):
        response = self.client.post('/', 'I am a value')
        
        self.keynames.append(response.json()['url'])
    
    @task(2)
    class Pull(TaskSet):
        max_wait = 2000
        
        @task(1)
        def pull(self):
            if self.parent.keynames:
                self.client.get(
                    '/{}'.format(self.parent.keynames[randrange(len(self.parent.keynames))]),
                    name='/<key>'
                )
            else:
                self.interrupt()
        
        @task(1)
        def pull_bad(self):
            with self.client.get('/badkey!', catch_response=True) as response:
                if response.status_code == 404:
                    response.success()


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 10
    max_wait = 55000
