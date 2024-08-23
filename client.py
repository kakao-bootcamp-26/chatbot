import requests
from translate import user_input, user_output

def get_prediction(input_text):
    url = 'http://192.168.219.139:5000/chat'  # Flask 서버 주소
    data = {'input': input_text}
    
    # POST 요청으로 데이터를 서버에 보냄
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Server response: {result['response']}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

if __name__ == '__main__':
    test_input = "Great place with nice ambiance and delicious food." # 입력
    get_prediction(test_input)