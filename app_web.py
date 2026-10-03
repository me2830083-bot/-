import pandas as pd
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام إدارة المديونيات والمصاريف",
    page_icon="📊",
    layout="wide"
)

st.title("📊 واجهة إدارة ومتابعة المديونيات والأقسام")

st.sidebar.header("📁 مصدر البيانات")
# إضافة أداة لرفع الملف مباشرة من جهازك لضمان عمله فوراً على السحابة
uploaded_file = st.sidebar.file_uploader("اختر ملف الإكسل (debts.xlsx)", type=["xlsx", "xls"])

# إذا لم يتم رفع ملف، نحاول قراءته تلقائياً من المجلد إن وجد
data_source = None
if uploaded_file is not None:
    data_source = uploaded_file
else:
    try:
        data_source = "debts.xlsx"
    except Exception:
        data_source = None

if data_source is not None:
    try:
        # قراءة ملف الإكسل وتحديد أول ورقة عمل تلقائياً
        df_raw = pd.read_excel(data_source, header=None, engine='openpyxl')
        
        if df_raw is not None and not df_raw.empty:
            st.sidebar.success("تم قراءة ملف الإكسل بنجاح! ✅")
            
            st.subheader("📌 الأقسام الرئيسية (المقاولين والنقل)")
            
            # تقسيم الشاشة إلى عمودين لعرض جدول المقاولين وجدول النقل
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
            st.warning("⚠️ الملف المرفوع فارغ أو لا يحتوي على بيانات.")
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
    st.warning("⚠️ يرجى رفع ملف الإكسل (`debts.xlsx`) من القائمة الجانبية في أقصى اليسار/اليمين لعرض البيانات فوراً.")
    st.info("""
    **طريقة التشغيل السريعة:**
    1. اذهب إلى القائمة الجانبية.
    2. اضغط على زر **Browse files** (تصفح الملفات).
    3. اختر ملف `debts.xlsx` من جهازك، وستظهر الجداول فوراً أمامك!
    """)
