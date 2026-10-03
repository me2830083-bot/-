import pandas as pd
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام إدارة المديونيات والمصاريف",
    page_icon="📊",
    layout="wide"
)

st.title("📊 واجهة إدارة ومتابعة المديونيات والأقسام")

# تحديد اسم ملف الإكسل الموجود في المجلد مباشرة
file_path = "debts.xlsx"

try:
    # قراءة الملف تلقائياً باستخدام openpyxl
    df_raw = pd.read_excel(file_path, header=None, engine='openpyxl')
    
    if df_raw is not None and not df_raw.empty:
        st.success("تم قراءة ملف الإكسل من المشروع بنجاح! ✅")
        
        st.subheader("📌 الأقسام الرئيسية (المقاولين والنقل)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👷 قسم المقاولين")
            try:
                contractors_df = df_raw.iloc[3:, [4, 5]].dropna(how="all")
                contractors_df.columns = ["الاسم", "المبلغ"]
                st.dataframe(contractors_df, use_container_width=True)
            except Exception:
                st.info("جاري تجهيز بيانات المقاولين...")
                
        with col2:
            st.markdown("### 🚛 قسم النقل")
            try:
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
        st.warning("⚠️ ملف الإكسل فارغ أو لا يحتوي على بيانات.")
        
except Exception as e:
    st.error(f"حدث خطأ أثناء قراءة الملف: تأكد من رفع ملف باسم 'debts.xlsx' في مجلد المشروع على جيت هوب. التفاصيل: {e}")
