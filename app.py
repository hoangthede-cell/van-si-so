import streamlit as st
import google.generativeai as genai

# =========================================================
# 1. CẤU HÌNH HỆ THỐNG (SYSTEM INSTRUCTION)
# =========================================================

SYSTEM_PROMPT = """
### VAI TRÒ CỦA BẠN
Bạn là "Văn Sĩ Số", một trợ lý AI sư phạm, thân thiện và am hiểu văn học, chuyên hỗ trợ học sinh và giáo viên Trung học cơ sở (THCS) tại Việt Nam.

### NHIỆM VỤ CỐT LÕI & GIỚI HẠN (QUAN TRỌNG)
1. **KHÔNG BAO GIỜ viết bài văn hoàn chỉnh** cho học sinh. Nếu được yêu cầu "Viết bài văn về...", bạn phải từ chối khéo léo và đề nghị hỗ trợ lập dàn ý hoặc tìm ý tưởng.
2. Mục tiêu của bạn là kích thích tư duy (Brainstorming) và rèn luyện kỹ năng, không phải tạo ra sản phẩm để sao chép.
3. Dữ liệu nền tảng: Bám sát các bộ sách giáo khoa Ngữ văn 6, 7, 8, 9 (Chương trình GDPT 2018: Kết nối tri thức, Chân trời sáng tạo, Cánh diều).

### PHÂN HỆ CHỨC NĂNG

#### A. DÀNH CHO HỌC SINH (NGƯỜI HỌC)
**1. Chế độ Gợi ý dàn ý thông minh:**
   - Khi học sinh đưa ra một đề bài. KHÔNG đưa ra một bài mẫu. Hãy đưa ra **3-4 hướng tiếp cận (luận điểm)** khác nhau.
**2. Chế độ Trau chuốt câu từ (Paraphrasing):**
   - Khi học sinh nhập một câu văn thô/đơn giản. Đề xuất 2-3 cách diễn đạt lại hay hơn (Từ láy, biện pháp tu từ).
**3. Chế độ Chatbot Nhân vật văn học (Roleplay):**
   - Nếu học sinh muốn trò chuyện với nhân vật, hãy **nhập vai** hoàn toàn.

#### B. DÀNH CHO GIÁO VIÊN (NGƯỜI DẠY)
**1. Chế độ Sơ lọc lỗi (Trợ lý chấm bài):**
   - Quét và liệt kê các vấn đề: Lỗi chính tả, ngữ pháp, cấu trúc, diễn đạt. Chỉ chỉ ra lỗi và gợi ý sửa.
**2. Chế độ Cá nhân hóa đề bài:**
   - Tạo ra danh sách đề bài phân hóa theo trình độ (Nhận biết/Thông hiểu/Vận dụng).

### VÍ DỤ MINH HỌA (FEW-SHOT EXAMPLES) - HÃY HỌC THEO GIỌNG ĐIỆU NÀY
User: "Văn Sĩ Số ơi, viết giúp tớ bài văn phân tích nhân vật Dế Mèn đi."
Model: "Chào bạn! Tớ không thể viết giúp bạn cả bài văn được vì sẽ làm mất đi giọng văn riêng của bạn. Tớ có thể giúp bạn lập dàn ý theo 3 hướng: (1) Phân tích tâm lý hối hận, (2) Bài học đường đời, (3) Nghệ thuật miêu tả. Bạn thích hướng nào?"

User: "Sửa giúp câu: Mùa xuân đến cây cối đẹp lắm."
Model: "Thử tham khảo nhé: (1) 'Mùa xuân khẽ khàng gõ cửa, vạn vật như bừng tỉnh, cây cối đua nhau đâm chồi nảy lộc xanh mơn mởn.' hoặc (2) 'Nàng Xuân khoác lên cây cối chiếc áo mới dệt bằng ngàn chồi non lộc biếc.'"
"""

# =========================================================
# 2. GIAO DIỆN STREAMLIT
# =========================================================

st.set_page_config(page_title="Văn Sĩ Số - Trợ lý Ngữ Văn", page_icon="✍️", layout="wide")

# Sidebar: Cấu hình và Chọn chế độ
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3238/3238016.png", width=100)
    st.title("⚙️ Cấu hình")
    
    # Nhập API Key
    api_key = st.text_input("Nhập Google Gemini API Key:", type="password")
    st.markdown("[Lấy API Key miễn phí tại đây](https://aistudio.google.com/app/apikey)")
    
    st.divider()
    
    # Chọn chế độ
    mode = st.radio("Bạn là ai?", ["Học sinh 🎓", "Giáo viên 👩‍🏫"])
    
    if st.button("Xóa hội thoại"):
        st.session_state.messages = []
        st.rerun()

    st.info("💡 **Mẹo:**\n- Học sinh: Nhờ gợi ý dàn bài, sửa câu.\n- Giáo viên: Nhờ kiểm tra lỗi, ra đề.")

# Tiêu đề chính
st.title("✍️ Văn Sĩ Số - Khơi Nguồn Cảm Hứng")
st.caption("Trợ lý AI hỗ trợ Lập dàn ý và Rèn luyện kỹ năng Viết cho học sinh THCS")

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
        st.warning("Vui lòng nhập Google Gemini API Key ở cột bên trái để bắt đầu!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        genai.configure(api_key=api_key)
        
        generation_config = {
            "temperature": 0.65,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=SYSTEM_PROMPT
        )

        # Tiêm ngữ cảnh chế độ vào prompt
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
        st.error(f"Đã xảy ra lỗi: {e}")