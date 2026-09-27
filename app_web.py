from datetime import datetime
import pandas as pd
import streamlit as st

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="نظام تسجيل المصروفات",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# رابط Google Sheet الخاص بك بصيغة CSV للتصدير المباشر
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1TykY6twiO-uivvU7BSYW2ky60vv-T42G1YiJ7FdfYL4/export?format=csv"

COLUMNS = ["الشركة", "التاريخ", "نوع المعاملة", "المبلغ", "المستلم"]

@st.cache_data(ttl=5)  # تحديث تلقائي كل 5 ثوانٍ
def load_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
        return df[COLUMNS]
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

st.title("💰 نظام إدارة وتسجيل المصروفات")

# القائمة الجانبية
app_mode = st.sidebar.radio("اختر الشاشة:", ["إضافة وحفظ حركات", "📋 عرض سجل الحركات", "📊 الرسم البياني والتحليلات"])

df_all = load_data()

if app_mode == "إضافة وحفظ حركات":
    st.subheader("➕ تسجيل حركة جديدة")
    
    # قائمة الشركات المسجلة ساباقاً إن وجدت
    existing_companies = [c for c in df_all["الشركة"].dropna().unique() if str(c).strip() != ""] if not df_all.empty else []
    
    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        if existing_companies:
            selected_company_opt = st.selectbox("اختر شركة مسجلة:", ["-- اختر شركة --"] + sorted(existing_companies))
        else:
            selected_company_opt = "-- اختر شركة --"
    with col_comp2:
        new_company_input = st.text_input("أو اكتب اسم شركة جديدة:")

    # تحديد اسم الشركة النهائي
    final_company = new_company_input.strip() if new_company_input.strip() else (selected_company_opt if selected_company_opt != "-- اختر شركة --" else "")

    st.write("---")
    
    with st.form("entry_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            date_val = st.date_input("التاريخ", datetime.now().date())
        with col2:
            payment_type = st.selectbox("نوع المعاملة", ["كاش", "تحويل", "شيك"])
            amount_val = st.number_input("المبلغ", min_value=0.0, step=10.0, format="%.2f")
        with col3:
            recipient_val = st.text_input("المستلم")

        submit = st.form_submit_button("عرض وتجهيز السطر لإضافته للشيت")

        if submit:
            if final_company and amount_val > 0 and recipient_val.strip():
                st.success(f"تم تسجيل البيانات بنجاح لشركة: {final_company}")
                st.info("قم بنسخ هذا السطر أو إضافته في Google Sheets مباشرة:")
                st.code(f"{final_company},{date_val},{payment_type},{amount_val},{recipient_val.strip()}", language="text")
            else:
                st.error("يرجى التأكد من اختيار/كتابة اسم الشركة، وإدخال المبلغ واسم المستلم.")

elif app_mode == "📋 عرض سجل الحركات":
    st.subheader("📋 عرض البيانات المسجلة من Google Sheets")
    
    if not df_all.empty and df_all["الشركة"].dropna().count() > 0:
        st.dataframe(df_all.dropna(how="all"), use_container_width=True)
        
        # تصفية حسب الشركة
        companies = [c for c in df_all["الشركة"].dropna().unique() if str(c).strip() != ""]
        if companies:
            st.write("---")
            filter_company = st.selectbox("تصفية حسب الشركة:", ["الكل"] + sorted(companies))
            if filter_company != "الكل":
                filtered_df = df_all[df_all["الشركة"] == filter_company]
                st.dataframe(filtered_df, use_container_width=True)
                total = pd.to_numeric(filtered_df["المبلغ"], errors="coerce").sum()
                st.metric(f"إجمالي مصروفات {filter_company}", f"{total:,.2f} جنيه")
    else:
        st.info("لا توجد بيانات مسجلة في Google Sheets حالياً. أضف رؤوس الأعمدة (الشركة، التاريخ، نوع المعاملة، المبلغ، المستلم) في أول صف بالشيت لتظهر هنا.")

elif app_mode == "📊 الرسم البياني والتحليلات":
    st.subheader("📈 إحصائيات وإجمالي المدفوعات للشركات")
    
    if not df_all.empty and df_all["المبلغ"].dropna().count() > 0:
        df_analysis = df_all.copy()
        df_analysis["المبلغ"] = pd.to_numeric(df_analysis["المبلغ"], errors="coerce").fillna(0)
        company_totals = df_analysis.groupby("الشركة")["المبلغ"].sum().reset_index()
        
        st.bar_chart(company_totals.set_index("الشركة")["المبلغ"])
        st.dataframe(company_totals.style.format({"المبلغ": "{:,.2f} جنيه"}), use_container_width=True)
    else:
        st.info("لا توجد بيانات مسجلة في الشيت حتى الآن.")

st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 **Developed by:** **Mohamed Elsayed**")
