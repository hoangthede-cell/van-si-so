import streamlit as st
import requests
import json

# =========================================================
# CẤU HÌNH: DÙNG BẢN GEMINI PRO (1.0) CHUẨN QUỐC TẾ
# (Bản này tương thích với mọi loại tài khoản cũ/mới)
# =========================================================

SYSTEM_PROMPT = """
Bạn là "Văn Sĩ Số", trợ lý AI sư phạm hỗ trợ Ngữ văn THCS.
NHIỆM VỤ:
1. Gợi ý dàn ý, ý tưởng (Brainstorming).
2. Sửa lỗi diễn đạt, trau chuốt câu từ.
3. Giọng điệu: Thân thiện, sư phạm.
"""

st.set_page_config(page_title="Văn Sĩ Số", page_icon="✍️")

# =========================================================
# GIAO DIỆN
# =========================================================

with st.sidebar:
    st.title("⚙️ Cài đặt")
    api_key = st.text_input("Nhập API Key:", type="password")
    
    # Thêm nút chọn phiên bản để thầy/cô tự đổi nếu lỗi
    model_choice = st.selectbox(
        "Chọn phiên bản AI:", 
        ["gemini-pro", "gemini-1.5-flash"],
        index=0 # Mặc định chọn gemini-pro (An toàn nhất)
    )
    
    st.info("Mẹo: Nếu bản này lỗi, hãy thử đổi sang bản kia.")
    if st.button("Xóa lịch sử"):
        st.session_state.messages = []
        st.rerun()

st.title("✍️ Văn Sĩ Số")
st.caption(f"Đang chạy phiên bản: {model_choice}")

# =========================================================
# XỬ LÝ KẾT NỐI (LOGIC)
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Nhập nội dung..."):
    
    if not api_key:
        st.warning("Chưa nhập API Key!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Đang kết nối..."):
                
                # Tạo URL dựa trên phiên bản đã chọn
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_choice}:generateContent?key={api_key}"
                headers = {'Content-Type': 'application/json'}
                
                contents = []
                for msg in st.session_state.messages:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": msg["content"]}]})
                
                payload = {
                    "contents": contents,
                    # Gemini Pro đôi khi kén cấu trúc system_instruction, ta đưa thẳng vào prompt
                    "generationConfig": {"temperature": 0.7}
                }

                # Gửi yêu cầu
                response = requests.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    # Xử lý trường hợp Google trả về cấu trúc khác nhau
                    try:
                        ans = result['candidates'][0]['content']['parts'][0]['text']
                    except:
                        ans = "AI không phản hồi nội dung. Hãy thử câu hỏi khác."
                        
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                else:
                    # In lỗi rõ ràng để xử lý
                    err_msg = response.text
                    st.error(f"Lỗi (Mã {response.status_code}): {err_msg}")
                    if response.status_code == 404:
                        st.warning(f"👉 Tài khoản của thầy/cô không dùng được bản {model_choice}. Hãy đổi sang bản kia ở cột bên trái!")
                    elif response.status_code == 429:
                        st.warning("👉 API Key này đã hết hạn mức miễn phí hôm nay. Hãy tạo Key từ Gmail khác.")

    except Exception as e:
        st.error(f"Lỗi hệ thống: {e}")
