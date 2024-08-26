import requests
from translate import user_input
import os

def get_prediction(input_text):
    # 서버 주소를 환경 변수에서 가져오도록 수정합니다.
    server_url = os.getenv('SERVER_URL', 'http://localhost:5000')
    url = f'{server_url}/chat'
    data = {'input': input_text}
    
    # POST 요청으로 데이터를 서버에 보냄
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Server response: {result['response']}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

if __name__ == '__main__':
    test_input = "음식이 맛있는 곳." # 입력
    chat_input = user_input(test_input)
    get_prediction(chat_input)
