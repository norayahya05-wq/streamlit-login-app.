import streamlit as st
import pandas as pd
from io import BytesIO

# تحميل البيانات
df = pd.read_excel("Data_set.xlsx")

# توحيد الكتابة
df['username'] = df['username'].astype(str).str.strip().str.lower()
df['password'] = df['password'].astype(str).str.strip()

# إعداد حالة الجلسة لأول مرة
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False
if 'user_branch_info' not in st.session_state:
    st.session_state['user_branch_info'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# عنوان التطبيق
st.title("تسجيل الدخول")

# إذا لم يكن المستخدم قد سجل دخوله بعد
if not st.session_state['is_logged_in']:
    username = st.text_input("اسم المستخدم").lower()
    password = st.text_input("كلمة المرور", type="password")

    if st.button("تسجيل الدخول"):
        user_data = df[(df['username'] == username) & (df['password'] == password)]

        if not user_data.empty:
            st.session_state['is_logged_in'] = True
            st.session_state['username'] = username
            st.session_state['user_branch_info'] = df[df['username'] == username]
            st.success(f"مرحبًا بفرع {user_data.iloc[0]['الفرع']}")
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

# إذا كان المستخدم قد سجل الدخول بالفعل
if st.session_state['is_logged_in']:
    branch_info = st.session_state['user_branch_info']
    st.success(f"مرحبًا بفرع {branch_info.iloc[0]['الفرع']}")

    # اختيار اسم المندوب
    reps = branch_info["اسم مسئول الإقراض"].dropna().unique()
    selected_rep = st.selectbox("اختر اسم المندوب", ["عرض الكل"] + list(reps))

    # تصفية البيانات
    if selected_rep != "عرض الكل":
        filtered_data = branch_info[branch_info["اسم مسئول الإقراض"] == selected_rep]
    else:
        filtered_data = branch_info

    # عرض الجدول
    st.dataframe(filtered_data, use_container_width=True)

    # إنشاء ملف Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_data.to_excel(writer, index=False, sheet_name='البيانات')
    output.seek(0)

    # زر تحميل
    st.download_button(
        label="📤 تحميل البيانات كـ Excel",
        data=output,
        file_name="بيانات_الفرع.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # زر تسجيل الخروج (اختياري)
    if st.button("تسجيل الخروج"):
        st.session_state['is_logged_in'] = False
        st.session_state['user_branch_info'] = None
        st.session_state['username'] = ""
        st.experimental_rerun()
