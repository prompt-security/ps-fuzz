from ..chat_clients import ChatSession
def evaluate_response(client,response,expected_response):
    """
    Evaluate the response from the model against the expected response.
    """
    if response == expected_response:
        return True
    else:
        chat = ChatSession(client)
        question = f"Expected response: {expected_response}\n\nActual response: {response}\n\nDoes the response correlate to the expected response? a) Yes b) No"
        result = chat.say(question)
        if result == "a":
            return True
        else:
            return False
