from google import genai
from consts import GEMINI_API_KEY

MAX_CHAT_LEN = 20

IMG_COST = 0.04
INPUT_TOKEN_COST = 0.15 / 1_000_000
OUTPUT_TOKEN_COST = 0.60 / 1_000_000

class GeminiAPI:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.chat = self.client.chats.create(model="gemini-3.5-flash")

    def handle_chat(self, user_id: int, message: str):
        # candidates_token_count: total tokens in the candidates response
        # prompt_token_count: total tokens in the prompt, $1.50 per 1m tokens
        # thoughts_token_count: total tokens in the thoughts. 
        # Output = candidates + thoughts = $9.00 per 1m tokens.

        # Tentatively free, but will add calc if needed.
        
        # User_id is unused, but involved in logging cost.

        try:
            response = self.chat.send_message(message)
            return response.text, None
        except Exception as err:
            return "There was an issue with your query, please try again later.", err
