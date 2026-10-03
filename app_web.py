import os
import pandas as pd
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام إدارة المديونيات والمصاريف",
    page_icon="📊",
    layout="wide"
)

st.title("📊 واجهة إدارة ومتابعة المديونيات والأقسام")

# الشريط الجانبي لتحديد مسار الملف المحلي
st.sidebar.header("📁 إعدادات الملف المحلي")
file_path = st.sidebar.text_input("مسار أو اسم ملف الإكسل:", "debts.xlsx")

# زر لتحديث البيانات يدوياً من الملف
if st.sidebar.button("🔄 تحديث البيانات من الملف"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data
def load_excel_data(path):
    if os.path.exists(path):
        try:
            # قراءة الملف بالكامل بدون رأس افتراضي لنتمكن من توزيع الجداول الجانبية بدقة
            df = pd.read_excel(path, header=None)
            return df
        except Exception as e:
            return None
    return None

df_raw = load_excel_data(file_path)

if df_raw is not None and not df_raw.empty:
    st.sidebar.success("تم قراءة ملف الإكسل بنجاح! ✅")
    
    st.subheader("📌 الأقسام الرئيسية (المقاولين والنقل)")
    
    # تقسيم الشاشة إلى عمودين لعرض جدول المقاولين وجدول النقل كما هو موضح في صورتك
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👷 قسم المقاولين")
        try:
            # استخراج أعمدة المقاولين بناءً على تخطيط الشيت لديك
            contractors_df = df_raw.iloc[3:, [4, 5]].dropna(how="all")
            contractors_df.columns = ["الاسم", "المبلغ"]
            st.dataframe(contractors_df, use_container_width=True)
        except Exception:
            st.info("جاري تجهيز بيانات المقاولين...")
            
    with col2:
        st.markdown("### 🚛 قسم النقل")
        try:
            # استخراج أعمدة النقل بناءً على تخطيط الشيت لديك
            transport_df = df_raw.iloc[3:, [7, 8]].dropna(how="all")
            transport_df.columns = ["الاسم", "المبلغ"]
            st.dataframe(transport_df, use_container_width=True)
        except Exception:
            st.info("جاري تجهيز بيانات النقل...")

    st.markdown("---")
    
    # قسم البحث العام والتفصيلي
    st.subheader("🔍 بحث شامل في كافة البيانات")
    search_query = st.text_input("ابحث عن أي اسم أو بند (مثل: رمضان، الإيجار، أبناء أسيوط...):").strip()
    
    if search_query:
        mask = df_raw.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        filtered_df = df_raw[mask]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        with st.expander("📁 عرض ملف الإكسل كاملاً (الشيت الأصلي)"):
            st.dataframe(df_raw, use_container_width=True)

else:
    st.warning(f"⚠️ لم يتم العثور على الملف في المسار: `{file_path}`")
    st.info("""
    **تعليمات التشغيل:**
    1. ضع ملف الإكسل في نفس مجلد هذا الكود على جهازك وسمّه `debts.xlsx`.
    2. كلما قمت بتعديل البيانات وحفظها في الإكسل على جهازك، اضغط على زر **(تحديث البيانات من الملف)** في القائمة الجانبية لتظهر التعديلات فوراً.
    """)
