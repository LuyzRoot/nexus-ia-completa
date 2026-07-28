class SampleAgent:
    def __init__(self):
        self.name = "sample_agent"

    def act(self, text: str) -> str:
        return f"Agent({self.name}) received: {text}"
