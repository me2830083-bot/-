import os
import zipfile
from datetime import datetime
import pandas as pd
import streamlit as st

try:
    from supabase import create_client, Client
except ImportError:
    st.warning("⚠️ جاري إعداد وتثبيت مكتبة Supabase على السيرفر... يرجى الانتظار دقيقة وإعادة تحميل الصفحة (Refresh).")
    st.stop()
# 1. إعداد الاتصال بـ Supabase
# ==========================================
SUPABASE_URL = st.secrets["SUPABASE_URL"] if "SUPABASE_URL" in st.secrets else os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets["SUPABASE_KEY"] if "SUPABASE_KEY" in st.secrets else os.getenv("SUPABASE_KEY")

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ==========================================
# 2. دوال التعامل مع البيانات عبر Supabase
# ==========================================
def fetch_companies():
    """جلب قائمة الشركات المسجلة في الجدول"""
    try:
        response = supabase.table("payments").select("company_name").execute()
        companies = list(set([item["company_name"] for item in response.data if item.get("company_name")]))
        return sorted(companies)
    except Exception as e:
        st.error(f"خطأ في جلب الشركات: {e}")
        return []

def load_monthly_data(company_name, year, month):
    """جلب بيانات شركة معينة لشهر وسنة محددين"""
    try:
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        response = (
            supabase.table("payments")
            .select("id, date, payment_type, amount, recipient")
            .eq("company_name", company_name)
            .gte("date", start_date)
            .lt("date", end_date)
            .execute()
        )
        
        data = response.data
        if data:
            df = pd.DataFrame(data)
            df.rename(columns={
                "date": "التاريخ",
                "payment_type": "نوع المعاملة",
                "amount": "المبلغ",
                "recipient": "المستلم"
            }, inplace=True)
            return df
        return pd.DataFrame(columns=["id", "التاريخ", "نوع المعاملة", "المبلغ", "المستلم"])
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {e}")
        return pd.DataFrame(columns=["id", "التاريخ", "نوع المعاملة", "المبلغ", "المستلم"])

def insert_payment(company_name, date_val, payment_type, amount, recipient):
    """إضافة حركة جديدة إلى Supabase"""
    try:
        data = {
            "company_name": company_name,
            "date": str(date_val),
            "payment_type": payment_type,
            "amount": float(amount),
            "recipient": recipient
        }
        supabase.table("payments").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"فشل حفظ الحركة: {e}")
        return False

def load_all_data():
    """جلب كل البيانات للتحليلات"""
    try:
        response = supabase.table("payments").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df.rename(columns={
                "company_name": "الشركة",
                "date": "التاريخ",
                "payment_type": "نوع المعاملة",
                "amount": "المبلغ",
                "recipient": "المستلم"
            }, inplace=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"خطأ في جلب بيانات التحليلات: {e}")
        return pd.DataFrame()

# ==========================================
# 3. الواجهة والتطبيق
# ==========================================
MONTH_NAMES = {
    1: "يناير (01)", 2: "فبراير (02)", 3: "مارس (03)", 4: "أبريل (04)",
    5: "مايو (05)", 6: "يونيو (06)", 7: "يوليو (07)", 8: "أغسطس (08)",
    9: "سبتمبر (09)", 10: "أكتوبر (10)", 11: "نوفمبر (11)", 12: "ديسمبر (12)"
}

st.title("📊 نظام إدارة وتسجيل المصروفات")

st.sidebar.header("النمط والقائمة الجانبية")
app_mode = st.sidebar.radio("اختر الشاشة:", ["إدارة الحركات الشهرية", "📊 الرسم البياني والتحليلات"])

existing_companies = fetch_companies()

if app_mode == "إدارة الحركات الشهرية":
    st.sidebar.header("إدارة الشركات والفترات")

    new_company = st.sidebar.text_input("إضافة شركة جديدة:")
    if st.sidebar.button("إضافة الشركة"):
        if new_company.strip():
            comp_name = new_company.strip()
            if comp_name not in existing_companies:
                # إضافة سجل وهمي مبدئي أو مجرد تحديث القائمة
                insert_payment(comp_name, datetime.now().date(), "كاش", 0.0, "افتتاحي")
                st.sidebar.success(f"تمت إضافة شركة {comp_name}")
                st.rerun()
            else:
                st.sidebar.warning("الشركة موجودة بالفعل!")
        else:
            st.sidebar.error("يرجى كتابة اسم الشركة")

    if existing_companies:
        selected_company = st.sidebar.selectbox("اختر الشركة:", sorted(existing_companies))
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        selected_year = st.sidebar.number_input(
            "السنة:", min_value=2020, max_value=2035, value=current_year, step=1
        )
        
        selected_month = st.sidebar.selectbox(
            "الشهر:", 
            options=list(MONTH_NAMES.keys()), 
            format_func=lambda x: MONTH_NAMES[x],
            index=current_month - 1
        )
    else:
        selected_company = None
        st.info("قم بإضافة شركة جديدة من القائمة الجانبية للبدء.")

    if selected_company:
        st.subheader(f"🏢 الشركة: {selected_company} | 📅 سجل شهر: {MONTH_NAMES[selected_month]} {selected_year}")

        df = load_monthly_data(selected_company, selected_year, selected_month)

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

            submit = st.form_submit_button("حفظ الحركة")

            if submit:
                if amount_val > 0 and recipient_val.strip():
                    if insert_payment(selected_company, date_val, payment_type, amount_val, recipient_val.strip()):
                        st.success("تم تسجيل الحركة بنجاح في Supabase!")
                        st.rerun()
                else:
                    st.error("يرجى إدخال المبلغ واسم المستلم بشكل صحيح.")

        st.write("---")
        st.write("### 📋 سجل المدفوعات الحالي")

        if not df.empty:
            st.dataframe(df[["التاريخ", "نوع المعاملة", "المبلغ", "المستلم"]], use_container_width=True)
            total_amount = pd.to_numeric(df["المبلغ"], errors="coerce").sum()
            st.metric(f"إجمالي مصروفات شهر {MONTH_NAMES[selected_month]}", f"{total_amount:,.2f} جنيه")
        else:
            st.info("لا توجد حركات مسجلة لهذه الشركة في هذا الشهر بعد.")

elif app_mode == "📊 الرسم البياني والتحليلات":
    st.subheader("📈 إحصائيات وإجمالي المدفوعات للشركات")
    
    all_df = load_all_data()
    
    if not all_df.empty and "الشركة" in all_df.columns and "المبلغ" in all_df.columns:
        all_df["المبلغ"] = pd.to_numeric(all_df["المبلغ"], errors="coerce").fillna(0)
        company_totals = all_df.groupby("الشركة")["المبلغ"].sum().reset_index()
        company_totals = company_totals.sort_values(by="المبلغ", ascending=False)
        
        st.write("### 🏆 ترتيب الشركات حسب أعلى إجمالي مدفوعات")
        st.bar_chart(company_totals.set_index("الشركة")["المبلغ"])
        
        st.write("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("#### 📄 تفاصيل إجمالي الشركات")
            st.dataframe(company_totals.style.format({"المبلغ": "{:,.2f} جنيه"}), use_container_width=True)
            
        with col2:
            if "نوع المعاملة" in all_df.columns:
                st.write("#### 💳 توزيع المدفوعات حسب نوع المعاملة")
                type_totals = all_df.groupby("نوع المعاملة")["المبلغ"].sum().reset_index()
                st.bar_chart(type_totals.set_index("نوع المعاملة")["المبلغ"])
    else:
        st.info("لا توجد بيانات مسجلة في النظام حتى الآن لعرض الرسم البياني.")

st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 **Developed by:** **Mohamed Elsayed**")
