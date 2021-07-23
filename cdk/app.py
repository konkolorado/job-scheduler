from aws_cdk import core as cdk

from cdk.stack import JobSchedulerStack


class JobSchedulerApp(cdk.App):
    def __init__(self):
        super().__init__()
        JobSchedulerStack(self, "JobSchedulerStack")


JobSchedulerApp().synth()
