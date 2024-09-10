from flask import Flask, request, jsonify
from gptapi import travel_recommend, find_aim

#test

app = Flask(__name__)

@app.route('/ai/process', methods=['POST'])

def process_request():
    """사용자 입력을 받아 의도를 분석하고, 필요시 여행지를 추천하는 엔드포인트"""
    try:
        # JSON 데이터를 요청의 body에서 가져옴
        data = request.get_json()
        if data is None or 'user_input' not in data:
            return jsonify({'status': 'failure', 'message': 'Invalid or missing JSON data in the request'}), 400
    except Exception as e:
        return jsonify({'status': 'failure', 'message': 'Invalid JSON format in body', 'error': str(e)}), 400

    # 사용자의 입력 텍스트
    user_input = data.get('user_input')

    # 입력된 질문의 의도 분류
    intent = find_aim(user_input)
    
    # 의도에 따라 적절한 처리
    if intent == "여행 추천 요청":
        # 여행지 추천 실행
        recommendation = travel_recommend(user_input)
        response_data = {
            **recommendation
        }
    else:
        # 의도가 여행 추천이 아닌 경우 적절한 메시지 반환
        response_data = {
            'message': 'This request does not involve travel recommendations.'
        }

    return jsonify(response_data), 200

def run_ai_server():
    """AI 서버 실행"""
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    # AI 서버 실행
    run_ai_server()