import streamlit as st
import requests
import json

# =========================================================
# 1. CẤU HÌNH HỆ THỐNG
# =========================================================

SYSTEM_PROMPT = """
Bạn là "Văn Sĩ Số", trợ lý AI sư phạm hỗ trợ Ngữ văn THCS.
NHIỆM VỤ:
1. Gợi ý dàn ý, ý tưởng (Brainstorming), KHÔNG viết văn mẫu trọn vẹn.
2. Sửa lỗi diễn đạt, trau chuốt câu từ.
3. Nhập vai nhân vật văn học nếu được yêu cầu.
4. Giọng điệu: Thân thiện với học sinh, trang trọng với giáo viên.
"""

st.set_page_config(page_title="Văn Sĩ Số - Trợ lý Ngữ Văn", page_icon="✍️", layout="wide")

# =========================================================
# 2. GIAO DIỆN & CẤU HÌNH
# =========================================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3238/3238016.png", width=100)
    st.title("⚙️ Cấu hình")
    
    # Nhập API Key
    api_key = st.text_input("Nhập Gemini API Key mới:", type="password")
    st.caption("Hãy dùng Key từ tài khoản Google mới để đảm bảo không bị lỗi.")
    
    st.divider()
    mode = st.radio("Bạn là ai?", ["Học sinh 🎓", "Giáo viên 👩‍🏫"])
    
    if st.button("Xóa hội thoại"):
        st.session_state.messages = []
        st.rerun()

st.title("✍️ Văn Sĩ Số - Khơi Nguồn Cảm Hứng")
st.caption("Phiên bản Kết nối Trực tiếp (Direct API)")

# =========================================================
# 3. XỬ LÝ LOGIC (GỌI TRỰC TIẾP GOOGLE KHÔNG QUA THƯ VIỆN)
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Xử lý tin nhắn mới
if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
    
    if not api_key:
        st.warning("Vui lòng nhập API Key!")
        st.stop()

    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- ĐOẠN MÃ KẾT NỐI TRỰC TIẾP ---
    try:
        with st.chat_message("assistant"):
            with st.spinner("Văn Sĩ Số đang suy nghĩ..."):
                
                # 1. Chuẩn bị dữ liệu gửi đi
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                headers = {'Content-Type': 'application/json'}
                
                # Chuyển đổi lịch sử chat sang định dạng JSON của Google
                contents_payload = []
                for msg in st.session_state.messages:
                    role = "user" if msg["role"] == "user" else "model"
                    contents_payload.append({"role": role, "parts": [{"text": msg["content"]}]})
                
                # Thêm chỉ dẫn hệ thống vào ngữ cảnh
                final_payload = {
                    "contents": contents_payload,
                    "system_instruction": {"parts": [{"text": f"[{mode.upper()}] {SYSTEM_PROMPT}"}]}
                }

                # 2. Gửi yêu cầu (POST Request)
                response = requests.post(url, headers=headers, json=final_payload)
                
                # 3. Xử lý kết quả trả về
                if response.status_code == 200:
                    result = response.json()
                    # Lấy nội dung văn bản từ phản hồi
                    ai_response = result['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    # Nếu lỗi, in chi tiết lỗi từ Google để dễ sửa
                    st.error(f"Lỗi kết nối (Mã {response.status_code}):")
                    st.code(response.text)
                    st.info("Hãy kiểm tra lại API Key xem đã đúng chưa nhé!")

    except Exception as e:
        st.error(f"Đã xảy ra lỗi: {e}")
