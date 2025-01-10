class TokenCounter():
    _total_token = 0

    @staticmethod
    def add(token: int):
        TokenCounter._total_token += token
        print(f"total used token: {TokenCounter._total_token}")
