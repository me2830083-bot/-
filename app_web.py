from datetime import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="نظام تسجيل المصروفات",
    page_icon="💰",
    layout="wide"
)

# رابط جوجل شيت الخاص بك
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TykY6twiO-uivvU7BSYW2ky60vv-T42G1YiJ7FdfYL4/edit#gid=0"

COLUMNS = ["الشركة", "التاريخ", "نوع المعاملة", "المبلغ", "المستلم"]

# الاتصال بـ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl="0")
        if df.empty:
            return pd.DataFrame(columns=COLUMNS)
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    conn.update(spreadsheet=SHEET_URL, data=df)

st.title("💰 نظام إدارة وتسجيل المصروفات")

# القائمة الجانبية
app_mode = st.sidebar.radio("اختر الشاشة:", ["إدارة الحركات", "📊 الرسم البياني والتحليلات"])

df_all = load_data()

if app_mode == "إدارة الحركات":
    st.sidebar.header("إدارة الشركات")
    
    # إضافة شركة جديدة
    new_company = st.sidebar.text_input("إضافة شركة جديدة:")
    if st.sidebar.button("إضافة الشركة"):
        if new_company.strip():
            st.sidebar.success(f"تم اعتماد شركة {new_company.strip()}، يمكنك اختيارها الآن من القائمة.")
        else:
            st.sidebar.error("يرجى كتابة اسم الشركة")

    # جلب الشركات المسجلة أو إتاحة إدخال شركة جديدة
    existing_companies = list(df_all["الشركة"].unique()) if "الشركة" in df_all.columns and not df_all.empty else []
    if new_company.strip() and new_company.strip() not in existing_companies:
        existing_companies.append(new_company.strip())

    if existing_companies:
        selected_company = st.sidebar.selectbox("اختر الشركة:", sorted(existing_companies))
    else:
        selected_company = None
        st.info("قم بإضافة شركة جديدة من القائمة الجانبية للبدء.")

    if selected_company:
        st.subheader(f"🏢 الشركة: {selected_company}")

        # نموذج إضافة حركة جديدة
        with st.form("payment_form", clear_on_submit=True):
            st.write("### ➕ تسجيل حركة جديدة")
            col1, col2, col3 = st.columns(3)
            with col1:
                date_val = st.date_input("التاريخ", datetime.now().date())
            with col2:
                payment_type = st.selectbox("نوع المعاملة", ["كاش", "تحويل", "شيك"])
                amount_val = st.number_input("المبلغ", min_value=0.0, step=10.0, format="%.2f")
            with col3:
                recipient_val = st.text_input("المستلم")

            submit = st.form_submit_button("حفظ الحركة في Google Sheets")

            if submit:
                if amount_val > 0 and recipient_val.strip():
                    new_row = pd.DataFrame([{
                        "الشركة": selected_company,
                        "التاريخ": str(date_val),
                        "نوع المعاملة": payment_type,
                        "المبلغ": amount_val,
                        "المستلم": recipient_val.strip(),
                    }])
                    updated_df = pd.concat([df_all, new_row], ignore_index=True)
                    save_data(updated_df)
                    st.success("تم تسجيل الحركة وحفظها أونلاين بنجاح!")
                    st.rerun()
                else:
                    st.error("يرجى إدخال المبلغ واسم المستلم بشكل صحيح.")

        st.write("---")
        st.write("### 📋 سجل المدفوعات الخاص بالشركة")

        company_df = df_all[df_all["الشركة"] == selected_company] if "الشركة" in df_all.columns else pd.DataFrame()

        if not company_df.empty:
            st.dataframe(company_df, use_container_width=True)
            total_amount = pd.to_numeric(company_df["المبلغ"], errors="coerce").sum()
            st.metric("إجمالي مصروفات الشركة", f"{total_amount:,.2f} جنيه")
        else:
            st.info("لا توجد حركات مسجلة لهذه الشركة بعد.")

elif app_mode == "📊 الرسم البياني والتحليلات":
    st.subheader("📈 إحصائيات وإجمالي المدفوعات للشركات")
    
    if not df_all.empty and "الشركة" in df_all.columns and "المبلغ" in df_all.columns:
        df_all["المبلغ"] = pd.to_numeric(df_all["المبلغ"], errors="coerce").fillna(0)
        company_totals = df_all.groupby("الشركة")["المبلغ"].sum().reset_index()
        
        st.write("### 🏆 ترتيب الشركات حسب أعلى إجمالي مدفوعات")
        st.bar_chart(company_totals.set_index("الشركة")["المبلغ"])
        st.dataframe(company_totals.style.format({"المبلغ": "{:,.2f} جنيه"}), use_container_width=True)
    else:
        st.info("لا توجد بيانات مسجلة في الشيت حتى الآن.")

st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 **Developed by:** **Mohamed Elsayed**")
