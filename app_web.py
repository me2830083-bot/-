import os
from datetime import datetime
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# 1. إعداد الاتصال بـ Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"] if "SUPABASE_URL" in st.secrets else os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets["SUPABASE_KEY"] if "SUPABASE_KEY" in st.secrets else os.getenv("SUPABASE_KEY")

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# 2. دوال التعامل مع البيانات من Supabase
def fetch_companies():
    """جلب قائمة الشركات المسجلة في الجدول"""
    try:
        response = supabase.table("payments").select("company_name").execute()
        companies = list(set([item["company_name"] for item in response.data if item.get("company_name")]))
        return sorted(companies)
    except Exception as e:
        st.error(f"خطأ في جلب الشركات: {e}")
        return []

def fetch_projects(company_name):
    """جلب المشاريع الخاصة بشركة معينة"""
    try:
        response = supabase.table("payments").select("project_name").eq("company_name", company_name).execute()
        projects = list(set([item["project_name"] for item in response.data if item.get("project_name")]))
        return sorted(projects)
    except Exception as e:
        st.error(f"خطأ في جلب المشاريع: {e}")
        return []

def fetch_data():
    """جلب كل بيانات الجدول لعرضها في لوحة التحكم"""
    try:
        response = supabase.table("payments").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {e}")
        return pd.DataFrame()

# 3. واجهة المستخدم عبر Streamlit
st.set_page_config(page_title="نظام إدارة المصاريف والمشاريع", layout="wide")

st.title("📊 نظام إدارة المصاريف والمشاريع المالية")
st.markdown("---")

# الشريط الجانبي للإدخال أو التصفح
st.sidebar.header("إدارة البيانات")

menu = st.sidebar.selectbox("اختر الصفحة", ["لوحة التحكم والتقارير", "إضافة مصروف جديد"])

if menu == "إضافة مصروف جديد":
    st.subheader("➕ تسجيل مصروف جديد")
    
    with st.form("expense_form"):
        company_name = st.text_input("اسم الشركة / العميل")
        project_name = st.text_input("اسم المشروع")
        amount = st.number_input("المبلغ", min_value=0.0, format="%.2f")
        expense_date = st.date_input("التاريخ", value=datetime.today())
        notes = st.text_area("ملاحظات إضافية")
        
        submit_button = st.form_submit_button(label="حفظ البيانات")
        
        if submit_button:
            if company_name and project_name:
                try:
                    data = {
                        "company_name": company_name,
                        "project_name": project_name,
                        "amount": amount,
                        "expense_date": str(expense_date),
                        "notes": notes
                    }
                    supabase.table("payments").insert(data).execute()
                    st.success("تم حفظ المصروف بنجاح في قاعدة البيانات!")
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الحفظ: {e}")
            else:
                st.warning("يرجى إدخال اسم الشركة واسم المشروع على الأقل.")

elif menu == "لوحة التحكم والتقارير":
    st.subheader("📈 نظرة عامة والتقارير المالية")
    
    df = fetch_data()
    
    if not df.empty:
        # عرض إحصائيات سريعة
        total_amount = df["amount"].sum() if "amount" in df.columns else 0
        st.metric(label="إجمالي المصاريف", value=f"{total_amount:,.2f}")
        
        st.markdown("### جدول البيانات المسجلة")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد بيانات مسجلة حتى الآن. يمكنك إضافة مصروف جديد من القائمة الجانبية.")
