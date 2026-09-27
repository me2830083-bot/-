from datetime import datetime
import pandas as pd
import streamlit as st

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="نظام تسجيل المصروفات",
    page_icon="💰",
    layout="wide"
)

# رابط Google Sheet الخاص بك بصيغة CSV للتصدير المباشر
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1TykY6twiO-uivvU7BSYW2ky60vv-T42G1YiJ7FdfYL4/export?format=csv"

COLUMNS = ["الشركة", "التاريخ", "نوع المعاملة", "المبلغ", "المستلم"]

@st.cache_data(ttl=5)  # إعادة تحديث البيانات كل 5 ثوانٍ تلقائياً
def load_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        # التأكد من وجود كافة الأعمدة
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
        return df[COLUMNS]
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

st.title("💰 نظام إدارة وتسجيل المصروفات")

# القائمة الجانبية
app_mode = st.sidebar.radio("اختر الشاشة:", ["عرض وسجل الحركات", "📊 الرسم البياني والتحليلات"])

df_all = load_data()

if app_mode == "عرض وسجل الحركات":
    st.sidebar.header("تصفية الشركات")
    
    # جلب الشركات المسجلة من الشيت
    existing_companies = list(df_all["الشركة"].dropna().unique()) if not df_all.empty else []

    if existing_companies:
        selected_company = st.sidebar.selectbox("اختر الشركة لعرض بياناتها:", sorted(existing_companies))
        
        st.subheader(f"🏢 الشركة: {selected_company}")
        st.write("### 📋 سجل المدفوعات الخاص بالشركة")

        company_df = df_all[df_all["الشركة"] == selected_company]

        if not company_df.empty:
            st.dataframe(company_df, use_container_width=True)
            total_amount = pd.to_numeric(company_df["المبلغ"], errors="coerce").sum()
            st.metric("إجمالي مصروفات الشركة", f"{total_amount:,.2f} جنيه")
        else:
            st.info("لا توجد حركات مسجلة لهذه الشركة بعد.")
    else:
        st.info("لا توجد بيانات مسجلة في الشيت حالياً. قم بإضافة بياناتك مباشرة في Google Sheets لتظهر هنا.")

elif app_mode == "📊 الرسم البياني والتحليلات":
    st.subheader("📈 إحصائيات وإجمالي المدفوعات للشركات")
    
    if not df_all.empty:
        df_analysis = df_all.copy()
        df_analysis["المبلغ"] = pd.to_numeric(df_analysis["المبلغ"], errors="coerce").fillna(0)
        company_totals = df_analysis.groupby("الشركة")["المبلغ"].sum().reset_index()
        
        st.write("### 🏆 ترتيب الشركات حسب أعلى إجمالي مدفوعات")
        st.bar_chart(company_totals.set_index("الشركة")["المبلغ"])
        st.dataframe(company_totals.style.format({"المبلغ": "{:,.2f} جنيه"}), use_container_width=True)
    else:
        st.info("لا توجد بيانات مسجلة في الشيت حتى الآن.")

st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 **Developed by:** **Mohamed Elsayed**")
