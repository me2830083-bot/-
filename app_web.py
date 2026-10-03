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
# إضافة أداة لرفع الملف مباشرة
uploaded_file = st.sidebar.file_uploader("اختر ملف الإكسل (debts.xlsx)", type=["xlsx", "xls"])

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
        # محاولة قراءة ملف الإكسل باستخدام openpyxl أو xlrd تلقائياً حسب الامتداد
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
        # محاولة أخيرة بديلة في حال كان محرك openpyxl واجه مشكلة في تداخل الامتدادات
        try:
            df_raw = pd.read_excel(data_source, header=None)
            if df_raw is not None and not df_raw.empty:
                st.sidebar.success("تم قراءة الملف بنجاح بالطريقة البديلة! ✅")
                with st.expander("📁 عرض الملف كاملاً"):
                    st.dataframe(df_raw, use_container_width=True)
            else:
                st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        except Exception as inner_e:
            st.error(f"حدث خطأ أثناء قراءة الملف: {inner_e}")
else:
    st.warning("⚠️ يرجى رفع ملف الإكسل (`debts.xlsx`) من القائمة الجانبية.")
    st.info("""
    **نصيحة:** إذا كان اسم الملف في جهازك يظهر كـ `debts.xlsx.xlsx`، يمكنك إعادة تسميته على جهازك ليكون `debts.xlsx` فقط قبل رفعه، أو يمكنك رفعه كما هو (الكود الآن مصمم ليتعامل مع أي صيغة بفضل الله).
    """)
