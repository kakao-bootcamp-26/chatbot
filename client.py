import requests
import json

def send_request_to_server(input_text):
    """Flask 서버에 입력 텍스트를 보내고 응답을 출력하는 함수"""
    url = 'http://127.0.0.1:5000/ai/process'  # Flask 서버의 주소와 엔드포인트
    data = {'user_input': input_text}  # 서버에서 기대하는 'user_input' 키로 수정

    try:
        # 서버에 POST 요청 전송
        response = requests.post(url, json=data)

        # 응답이 성공적일 경우
        if response.status_code == 200:
            # 서버 응답을 그대로 출력
            print("서버 응답:")
            print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        else:
            # 오류가 발생한 경우 상태 코드와 응답 본문 출력
            print(f"오류: {response.status_code}, {response.text}")

    except Exception as e:
        # 예외 발생 시 오류 메시지 출력
        print(f"요청 중 오류 발생: {str(e)}")

if __name__ == '__main__':
    # 사용자로부터 입력을 직접 받습니다.
    user_input = input("서버에 보낼 입력을 입력하세요: ")

    # Flask 서버에 요청을 보내고 응답을 출력합니다.
    send_request_to_server(user_input)
