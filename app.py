from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)

# 모델과 벡터라이저 함께 로드
with open('kakaobootcamp/team/travel/chatbot/model/svm_model.pkl', 'rb') as model_file:
    model_pipeline = pickle.load(model_file)

# 챗봇 엔드포인트
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json

    user_input = data.get('input')

    if not user_input:
        return jsonify({'error': 'No input provided'}), 400

    # 예측 수행 (모델 파이프라인은 입력 데이터를 벡터화하고 예측을 수행함)
    prediction = model_pipeline.predict([user_input])

    # 예측 결과를 사용해 응답 생성
    response = f"{prediction[0]}"

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
