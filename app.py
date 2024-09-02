from flask import Flask, request, jsonify
import openai
import os
import json
from dotenv import load_dotenv
import requests
import time
from threading import Thread

# 환경 변수 로드
load_dotenv()  # .env 파일을 로드하여 환경 변수를 설정
openai.api_key = os.getenv('OPENAI_API_KEY')  # 환경 변수에서 OpenAI API 키 가져오기

app = Flask(__name__)

# 세션 데이터를 저장할 파일 경로
session_file_path = 'kakaobootcamp/team/travel/chatbot/chatbot/session_data.json'

# 세션 파일 초기화
if not os.path.exists(session_file_path):
    with open(session_file_path, 'w') as f:
        json.dump({}, f)  # 빈 JSON 객체 저장

def load_session_data():
    """세션 데이터를 파일에서 로드"""
    with open(session_file_path, 'r') as f:
        return json.load(f)

def save_session_data(data):
    """세션 데이터를 파일에 저장"""
    with open(session_file_path, 'w') as f:
        json.dump(data, f)

def analyze_intent(user_input):
    """사용자 입력을 분석하여 의도를 식별"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "다음 사용자 입력의 의도를 다음 중 하나로 식별하세요: 여행지 추천, 추천, 알 수 없음. 관련이 있다면 '음식이 맛있다', '낭만적이다', '별이 많다', '밤하늘이 아름답다'와 같은 특정 키워드도 식별하세요."},
                {"role": "user", "content": f"User input: '{user_input}'"}
            ],
            max_tokens=50,
            temperature=0.2
        )
        
        # GPT 응답을 문자열로 받아오고 로그로 출력합니다.
        intent = response['choices'][0]['message']['content']
        intent_parts = intent.split("\n")
        intent = None
        keywords = []
        
        for part in intent_parts:
            if "의도:" in part:
                intent = part.split("의도:")[-1].strip().lower()
            if "관련 키워드:" in part:
                keyword_str = part.split("관련 키워드:")[-1].strip().lower()
                keywords = [kw.strip() for kw in keyword_str.split(",")]

        if not keywords:  # 키워드가 없다면 None으로 설정
            keywords = None

        return intent, keywords
    except Exception as e:
        print(f"Error in analyze_intent: {e}")
        return "unknown", None

def get_travel_recommendation_from_gpt(keywords):
    """GPT를 사용하여 키워드에 기반한 해외 여행지 추천 (한글 응답)"""
    for attempt in range(3):  # 최대 3번 재시도
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "다음 키워드를 바탕으로 대표적인 해외의 도시 하나만 추천해 주세요. 도시 이름만 반환해주세요"},
                    {"role": "user", "content": f"Keywords: {', '.join(keywords)}"}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            city = response['choices'][0]['message']['content'].strip()
            return city

        except openai.error.RateLimitError as e:
            print(f"Rate limit error: {e}")
            if "please try again in" in str(e).lower():
                delay_time = int(str(e).split("in ")[-1].split("s")[0]) + 1  # 오류 메시지에서 지연 시간 추출
                print(f"Waiting for {delay_time} seconds before retrying...")
                time.sleep(delay_time)  # 지연 후 재시도
            else:
                time.sleep(20)  # 기본 지연 시간
        
        except Exception as e:
            print(f"Error in get_travel_recommendation_from_gpt: {e}")
            return "추천하는 도시에 문제가 발생했습니다."
    
    # 최대 재시도 후 실패 시 메시지
    return "요청이 여러 번 실패했습니다. 나중에 다시 시도해 주세요."
    
def get_response(intent, keywords=None):
    """의도와 키워드에 따른 응답 생성"""
    session_data = load_session_data()
    last_intent = session_data.get('last_intent')

    if intent == "여행지 추천" and last_intent == "awaiting keyword" and not keywords:
        return "어떤 여행지를 추천해드릴까요?", "어떤 여행지를 추천해드릴까요?"

    if last_intent == "awaiting keyword" and keywords:
        city = get_travel_recommendation_from_gpt(keywords)
        session_data['last_intent'] = None  # 상태 초기화
        save_session_data(session_data)
        return f"추천드리는 도시 : {city}", city
    
    if intent == "여행지 추천" and not keywords:
        session_data['last_intent'] = "awaiting keyword"  # 키워드 기다리는 상태로 설정
        save_session_data(session_data)
        return "어떤 여행지를 추천해드릴까요?", "어떤 여행지를 추천해드릴까요?"
    
    if intent == "여행지 추천" and keywords:
        city = get_travel_recommendation_from_gpt(keywords)
        return f"추천드리는 도시 : {city}", city
    
    session_data['last_intent'] = None  # 기타 상황에서 상태 초기화
    save_session_data(session_data)
    return "죄송합니다, 이해하지 못했습니다.", None


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('input')
        if not user_input:
            return jsonify({'error': 'No input provided'}), 400

        # 의도 분석
        intent, raw_keywords = analyze_intent(user_input)
        keywords = raw_keywords if raw_keywords else None

        # 응답 생성
        message, city = get_response(intent, keywords)
        return jsonify({
            'intent_response': intent,  # 모델 응답 메시지 유형
            'message': message,         # 사용자에게 보여줄 메시지
            'recommendation': city      # 추천된 도시 이름
        })
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def get_prediction(input_text):
    """클라이언트 요청을 통해 서버에 입력을 전달하고 응답을 받습니다."""
    url = 'http://127.0.0.1:5000/chat'  # Flask 서버 주소
    data = {'input': input_text}  # 서버에서 기대하는 'input' 키로 수정
    
    # 요청 보내기
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        
        # 올바른 응답 키 사용
        intent_response = result.get('intent_response', '응답 없음')
        message = result.get('message', '메시지 없음')
        recommendation = result.get('recommendation', '추천 없음')
        
        print(f"의도 응답: {intent_response}")
        print(f"메시지: {message}")
        print(f"추천: {recommendation}")

    else:
        print(f"오류: {response.status_code}, {response.text}")

def run_server():
    """Flask 서버를 별도의 스레드에서 실행합니다."""
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # 서버 실행을 위한 스레드 시작
    server_thread = Thread(target=run_server)
    server_thread.start()

    # 서버가 완전히 시작될 때까지 대기
    time.sleep(3)  # 서버가 준비될 시간을 충분히 주기

    # 사용자로부터 계속 입력을 받아 처리
    while True:
        user_input = input("사용자 입력: ")
        if user_input.lower() in ['exit', 'quit']:
            print("종료합니다.")
            break
        get_prediction(user_input)
