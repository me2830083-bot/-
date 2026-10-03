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

# الشريط الجانبي لتحديد مسار الملف (تم ضبط القيمة الافتراضية لاسم الملف المرفوع على جيت هوب)
st.sidebar.header("📁 إعدادات الملف")
file_path = st.sidebar.text_input("مسار أو اسم ملف الإكسل:", "debts.xlsx")

# زر لتحديث البيانات يدوياً من الملف
if st.sidebar.button("🔄 تحديث البيانات من الملف"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data
def load_excel_data(path):
    # التحقق من وجود الملف محلياً أو على بيئة الاستضافة
    if os.path.exists(path):
        try:
            # قراءة ملف الإكسل وتحديد أول ورقة عمل تلقائياً
            df = pd.read_excel(path, header=None, engine='openpyxl')
            return df
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
            return None
    return None

df_raw = load_excel_data(file_path)

if df_raw is not None and not df_raw.empty:
    st.sidebar.success("تم قراءة ملف الإكسل بنجاح! ✅")
    
    st.subheader("📌 الأقسام الرئيسية (المقاولين والنقل)")
    
    # تقسيم الشاشة إلى عمودين لعرض جدول المقاولين وجدول النقل
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👷 قسم المقاولين")
        try:
            # استخراج أعمدة المقاولين بناءً على تخطيط الشيت
            contractors_df = df_raw.iloc[3:, [4, 5]].dropna(how="all")
            contractors_df.columns = ["الاسم", "المبلغ"]
            st.dataframe(contractors_df, use_container_width=True)
        except Exception:
            st.info("جاري تجهيز بيانات المقاولين...")
            
    with col2:
        st.markdown("### 🚛 قسم النقل")
        try:
            # استخراج أعمدة النقل بناءً على تخطيط الشيت
            transport_df = df_raw.iloc[3:, [7, 8]].dropna(how="all")
            transport_df.columns = ["الاسم", "المبلغ"]
            st.dataframe(transport_df, use_container_width=True)
        except Exception:
            st.info("جاري تجهيز بيانات النقل...")

    st.markdown("---")
    
    # قسم البحث العام والتفصيلي
    st.subheader("🔍 بحث شامل في كافة البيانات")
    search_query = st.text_input("ابحث عن أي اسم أو بند:").strip()
    
    if search_query:
        mask = df_raw.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        filtered_df = df_raw[mask]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        with st.expander("📁 عرض ملف الإكسل كاملاً (الشيت الأصلي)"):
            st.dataframe(df_raw, use_container_width=True)

else:
    st.warning(f"⚠️ لم يتم العثور على الملف في المسار أو أن الملف فارغ: `{file_path}`")
    st.info("""
    **تعليمات التشغيل على السحابة:**
    1. تأكد أن ملف `debts.xlsx` مرفوع في المجلد الرئيسي لمستودع جيت هوب بجانب كود التطبيق.
    2. تأكد أن الاسم مكتوب بدقة في خانة المسار الجانبية.
    3. اضغط على زر **(تحديث البيانات من الملف)** أو قم بإعادة تشغيل التطبيق (Reboot) من لوحة تحكم Streamlit Cloud.
    """)
