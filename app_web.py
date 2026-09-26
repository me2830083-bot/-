Skip to content
me2830083-bot
-
Repository navigation
Code
Issues
Pull requests
Actions
Projects
Wiki
Security and quality
Insights
Settings
Files
Go to file
t
T
app_web.py
​requirements.txt
-
/
app_web.py
in
main

Edit

Preview
Indent mode

Spaces
Indent size

4
Line wrap mode

No wrap
Editing app_web.py file contents
  1
  2
  3
  4
  5
  6
  7
  8
  9
 10
 11
 12
 13
 14
 15
 16
 17
 18
 19
 20
 21
 22
 23
 24
 25
 26
 27
 28
 29
 30
 31
 32
 33
 34
 35
 36
 37
 38
 39
 40
 41
 42
 43
 44
 45
 46
 47
 48
 49
 50
 51
 52
 53
 54
 55
 56
 57
 58
 59
 60
 61
 62
 63
 64
 65
 66
 67
 68
 69
import os
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="نظام تسجيل المصروفات", layout="wide")

# إنشاء مجلد البيانات إذا لم يكن موجوداً
DATA_DIR = "company_data"
os.makedirs(DATA_DIR, exist_ok=True)

COLUMNS = ["التاريخ", "نوع المعاملة", "المبلغ", "المستلم"]


def load_company_data(company_name):
    filepath = os.path.join(DATA_DIR, f"{company_name}.csv")
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df["التاريخ"] = pd.to_datetime(df["التاريخ"]).dt.date
        # التأكد من وجود عمود نوع المعاملة
        if "نوع المعاملة" not in df.columns:
            df.insert(1, "نوع المعاملة", "كاش")
        # الإبقاء فقط على الأعمدة المطلوبة وتجاهل "البيان / السبب" إن وجد
        return df[[col for col in COLUMNS if col in df.columns]]
    return pd.DataFrame(columns=COLUMNS)


def save_company_data(company_name, df):
    filepath = os.path.join(DATA_DIR, f"{company_name}.csv")
    df.to_csv(filepath, index=False)


st.title("📊 نظام إدارة وتسجيل المصروفات")

# القائمة الجانبية لإدارة الشركات
st.sidebar.header("إدارة الشركات")

# جلب قائمة الشركات المتاحة
existing_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
existing_companies = [os.path.splitext(f)[0] for f in existing_files]

# إضافة شركة جديدة
new_company = st.sidebar.text_input("إضافة شركة جديدة:")
if st.sidebar.button("إضافة الشركة"):
    if new_company.strip():
        if new_company.strip() not in existing_companies:
            df_empty = pd.DataFrame(columns=COLUMNS)
            save_company_data(new_company.strip(), df_empty)
            st.sidebar.success(f"تمت إضافة شركة {new_company}")
            st.rerun()
        else:
            st.sidebar.warning("الشركة موجودة بالفعل!")
    else:
        st.sidebar.error("يرجى كتابة اسم الشركة")

# اختيار الشركة الحالية
if existing_companies:
    selected_company = st.sidebar.selectbox(
        "اختر الشركة:", existing_companies
    )
else:
    selected_company = None
    st.info("قم بإضافة شركة جديدة من القائمة الجانبية للبدء.")

if selected_company:
    st.subheader(f"الشركة الحالية: {selected_company}")

    df = load_company_data(selected_company)

Use Control + Shift + m to toggle the tab key moving focus. Alternatively, use esc then tab to move to the next interactive element on the page.
 
