import streamlit as st
import requests
import base64
from PIL import Image
import io

# 1. Gemini API 설정 (발급받은 자신의 API 키를 입력하세요)
GOOGLE_API_KEY = ""

# 페이지 기본 설정
st.set_page_config(
    page_title="정찬우의 약물 상호작용 검색기",
    page_icon="💊",
    layout="centered"
)

# 웹사이트 타이틀 및 설명
st.title("💊 약속 (藥·束)")
st.subheader("약 사진을 찍어 함께 먹으면 안 되는 약과 음식을 알아보세요.")

st.warning(
    "⚠️ **주의 및 면책조항:** 본 서비스는 AI 기술을 활용한 참고용 정보만을 제공하며, "
    "전문적인 의학적 진단이나 약사의 복약 지도를 대체할 수 없습니다."
)

# 2. 이미지 업로드 기능
img_file = st.file_uploader("약 이름이 보이는 사진을 업로드하세요", type=["jpg", "jpeg", "png"])
camera_file = st.camera_input("또는 카메라로 직접 촬영하세요")

target_image = None
if img_file is not None:
    target_image = Image.open(img_file)
elif camera_file is not None:
    target_image = Image.open(camera_file)

# 이미지를 이진 데이터(Bytes)로 변환하는 함수
def encode_image_to_base64(image):
    buffered = io.BytesIO()
    # 이미지 포맷을 JPEG로 통일하여 저장
    image.convert("RGB").save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# 3. 이미지 분석 및 결과 출력
if target_image is not None:
    st.image(target_image, caption="업로드된 이미지", use_container_width=True)
    
    if st.button("💊 상호작용 분석 시작"):
        st.write("🔄 **AI가 이미지에서 약 이름을 찾고 주의사항을 분석 중입니다...**")
        
        try:
            # 이미지를 AI가 읽을 수 있는 텍스트 형태로 변환
            base64_image = encode_image_to_base64(target_image)
            
            # 구글 Gemini 서버 주소 (라이브러리 없이 직접 호출)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
            
            # AI에게 보낼 요청 데이터 구조 짜기
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": """당신은 전문 약사이자 의학 지식 가이드입니다. 
                            제공된 이미지에서 약 이름이나 성분명을 정확하게 인식해 주세요.
                            그 후, 인식된 약물들을 기준으로 아래 항목에 맞춰 일반인이 이해하기 쉽게 설명해 주세요.

                            [출력 양식]
                            ### 🔍 1. 인식된 약물 정보
                            - 이미지에서 인식한 약 이름 또는 성분명

                            ### 🚫 2. 함께 복용하면 안 되는 약 (병용 금기)
                            - 이 약과 함께 먹으면 부작용이 생기거나 약효가 떨어지는 다른 약 성분/종류와 이유

                            ### 🍏 3. 피해야 할 음식 및 음료 (식품 상호작용)
                            - 이 약을 복용할 때 피해야 할 음식(예: 자몽, 우유, 커피, 술 등)과 그 이유

                            ### 💡 4. 복용 시 추가 주의사항
                            - 식전/식후 복용 여부나 보관 방법 등 유용한 팁"""
                        },
                        {
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }]
            }
            
            # 구글 서버로 전송 및 답변 받기
            response = requests.post(url, headers=headers, json=payload)
            result_json = response.json()
            
            # 받은 답변에서 글자만 쏙 빼내기
            answer_text = result_json['candidates'][0]['content']['parts'][0]['text']
            
            st.success("✅ 분석이 완료되었습니다!")
            st.divider()
            st.markdown(answer_text)
            
        except Exception as e:
            st.error("분석 중 오류가 발생했습니다.")
            st.info("API 키가 올바른지 다시 확인해 주시거나, 약 이름이 잘 보이게 사진을 다시 찍어주세요.")
