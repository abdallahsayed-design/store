import streamlit as st
import pandas as pd
import os

# إعدادات الصفحة
st.set_page_config(page_title="نظام المخازن الذكي", layout="wide")

# ملفات البيانات
INVENTORY_FILE = "inventory_data.csv"
USERS_FILE = "users_data.csv"

# دالة لتهيئة الملفات
def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame([{"username": "admin", "password": "123"}]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(INVENTORY_FILE):
        pd.DataFrame(columns=["كود الصنف", "اسم الصنف", "الكمية", "آخر تحديث بواسطة"]).to_csv(INVENTORY_FILE, index=False)

init_files()

# واجهة تسجيل الدخول
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 تسجيل الدخول للنظام")
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        u_df = pd.read_csv(USERS_FILE)
        if ((u_df['username'] == user) & (u_df['password'] == str(pw))).any():
            st.session_state.auth = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("بيانات الدخول خاطئة")
else:
    # لوحة التحكم الرئيسية
    st.sidebar.title(f"👤 مرحباً: {st.session_state.user}")
    menu = ["📦 عرض المخزن", "➕ إضافة صنف", "🔄 وارد وصادر", "👥 إدارة المستخدمين"]
    choice = st.sidebar.selectbox("القائمة", menu)

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.rerun()

    df = pd.read_csv(INVENTORY_FILE)

    if choice == "📦 عرض المخزن":
        st.header("📊 حالة المخزن الحالية")
        st.table(df)

    elif choice == "➕ إضافة صنف":
        st.header("إضافة صنف جديد")
        c1, c2 = st.columns(2)
        item_id = c1.text_input("كود الصنف")
        item_name = c2.text_input("اسم الصنف")
        qty = st.number_input("الكمية الابتدائية", min_value=0)
        if st.button("حفظ"):
            new_data = pd.DataFrame([{"كود الصنف": item_id, "اسم الصنف": item_name, "الكمية": qty, "آخر تحديث بواسطة": st.session_state.user}])
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(INVENTORY_FILE, index=False)
            st.success("تم الإضافة!")

    elif choice == "🔄 وارد وصادر":
        st.header("حركة المخزون")
        item = st.selectbox("اختر الصنف", df['اسم الصنف'].unique() if not df.empty else [])
        if item:
            action = st.radio("نوع العملية", ["وارد (إضافة)", "صادر (سحب)"])
            amount = st.number_input("الكمية", min_value=1)
            if st.button("تأفيذ"):
                idx = df[df['اسم الصنف'] == item].index[0]
                if "وارد" in action:
                    df.at[idx, 'الكمية'] += amount
                else:
                    df.at[idx, 'الكمية'] -= amount
                df.at[idx, 'آخر تحديث بواسطة'] = st.session_state.user
                df.to_csv(INVENTORY_FILE, index=False)
                st.success("تم التحديث!")

    elif choice == "👥 إدارة المستخدمين":
        st.header("إضافة يوزر جديد")
        new_u = st.text_input("اسم المستخدم الجديد")
        new_p = st.text_input("كلمة المرور", type="password")
        if st.button("إنشاء حساب"):
            u_df = pd.read_csv(USERS_FILE)
            new_user_df = pd.DataFrame([{"username": new_u, "password": new_p}])
            u_df = pd.concat([u_df, new_user_df], ignore_index=True)
            u_df.to_csv(USERS_FILE, index=False)
            st.success(f"تم إنشاء حساب لـ {new_u}")

