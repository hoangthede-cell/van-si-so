import streamlit as st
import subprocess
import sys

# =========================================================
# 🚑 CẤP CỨU: TỰ ĐỘNG CÀI ĐẶT THƯ VIỆN MỚI NHẤT
# (Bỏ qua luôn file requirements.txt để tránh lỗi)
# =========================================================
try:
    import google.generativeai as genai
    # Kiểm tra xem có đúng bản mới không, nếu lỗi thì cài lại
    model_check = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    # Nếu chưa có thư viện hoặc thư viện cũ -> Cài ngay lập tức
    print("Đang nâng cấp hệ thống AI... Vui lòng đợi...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "google-generativeai"])
    import google.generativeai as genai

# =========================================================
# 1. CẤU HÌNH HỆ THỐNG (SYSTEM INSTRUCTION)
# =========================================================

SYSTEM_PROMPT = """
### VAI TRÒ CỦA BẠN
Bạn là "Văn Sĩ Số", một trợ lý AI sư phạm, thân thiện và am hiểu văn học, chuyên hỗ trợ học sinh và giáo viên THCS.

### NHIỆM vụ CỐT LÕI
1. KHÔNG viết bài văn mẫu hoàn chỉnh.
2. Gợi mở tư duy, lập dàn ý, sửa lỗi diễn đạt.
3. Dữ liệu: SGK Ngữ văn 6, 7, 8, 9 (GDPT 2018).

### VÍ DỤ (FEW-SHOT):
User: "Viết bài văn tả mẹ."
Model: "Chào bạn! Tớ không viết giúp cả bài được, nhưng tớ gợi ý 3 hướng này nhé: (1) Mẹ lúc chăm sóc em ốm, (2) Đôi bàn tay mẹ, (3) Mẹ trong công việc. Bạn chọn ý nào?"
"""

# =========================================================
# 2. GIAO DIỆN STREAMLIT
# =========================================================

st.set_page_config(page_title="Văn Sĩ Số - Trợ lý Ngữ Văn", page_icon="✍️", layout="wide")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3238/3238016.png", width=100)
    st.title("⚙️ Cấu hình")
    
    # Nhập API Key
    api_key = st.text_input("Nhập Google Gemini API Key:", type="password")
    st.markdown("[Lấy API Key miễn phí tại đây](https://aistudio.google.com/app/apikey)")
    
    st.divider()
    mode = st.radio("Bạn là ai?", ["Học sinh 🎓", "Giáo viên 👩‍🏫"])
    
    if st.button("Xóa hội thoại"):
        st.session_state.messages = []
        st.rerun()

st.title("✍️ Văn Sĩ Số - Khơi Nguồn Cảm Hứng")
st.caption("Trợ lý AI hỗ trợ Lập dàn ý và Rèn luyện kỹ năng Viết (Phiên bản Tự sửa lỗi)")

# =========================================================
# 3. XỬ LÝ LOGIC CHATBOT
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Nhập câu hỏi của bạn ở đây..."):
    
    if not api_key:
        st.warning("Vui lòng nhập API Key để bắt đầu!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Cấu hình AI
        genai.configure(api_key=api_key)
        
        # Dùng model chuẩn 1.5 Flash
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", 
            system_instruction=SYSTEM_PROMPT
        )

        context_prompt = f"[{mode.upper()}] {prompt}"
        
        history_gemini = []
        for msg in st.session_state.messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history_gemini.append({"role": role, "parts": [msg["content"]]})

        chat_session = model.start_chat(history=history_gemini)
        
        with st.chat_message("assistant"):
            with st.spinner("Văn Sĩ Số đang suy nghĩ..."):
                response = chat_session.send_message(context_prompt)
                st.markdown(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        # Bắt lỗi và hiện thông báo thân thiện hơn
        st.error(f"Đã xảy ra lỗi kết nối: {e}")
        st.info("💡 Mẹo: Hãy thử kiểm tra lại API Key hoặc tạo Key mới từ dự án khác.")
