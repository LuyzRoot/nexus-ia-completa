class LocalClient:
    def __init__(self):
        pass

    def predict(self, prompt: str) -> str:
        return f"[local echo] {prompt}"
