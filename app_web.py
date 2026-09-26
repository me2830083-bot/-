import os
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="نظام تسجيل المصروفات", layout="wide")

# مجلد البيانات الرئيسي
DATA_DIR = "company_data"
os.makedirs(DATA_DIR, exist_ok=True)

COLUMNS = ["التاريخ", "نوع المعاملة", "المبلغ", "المستلم"]

# أسماء الأشهر بالعربي
MONTH_NAMES = {
    1: "يناير (01)", 2: "فبراير (02)", 3: "مارس (03)", 4: "أبريل (04)",
    5: "مايو (05)", 6: "يونيو (06)", 7: "يوليو (07)", 8: "أغسطس (08)",
    9: "سبتمبر (09)", 10: "أكتوبر (10)", 11: "نوفمبر (11)", 12: "ديسمبر (12)"
}


def get_month_filepath(company_name, year, month):
    company_folder = os.path.join(DATA_DIR, company_name)
    os.makedirs(company_folder, exist_ok=True)
    filename = f"{company_name}_{year}_{month:02d}.csv"
    return os.path.join(company_folder, filename)


def load_monthly_data(company_name, year, month):
    filepath = get_month_filepath(company_name, year, month)
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df["التاريخ"] = pd.to_datetime(df["التاريخ"]).dt.date
        if "نوع المعاملة" not in df.columns:
            df.insert(1, "نوع المعاملة", "كاش")
        return df[[col for col in COLUMNS if col in df.columns]]
    return pd.DataFrame(columns=COLUMNS)


def save_monthly_data(company_name, year, month, df):
    filepath = get_month_filepath(company_name, year, month)
    df.to_csv(filepath, index=False)


st.title("📊 نظام إدارة وتسجيل المصروفات الشهري")

# القائمة الجانبية
st.sidebar.header("إدارة الشركات والفترات")

# جلب قائمة الشركات الموجودة (المجلدات)
existing_companies = [
    d for d in os.listdir(DATA_DIR) 
    if os.path.isdir(os.path.join(DATA_DIR, d))
]

# إضافة شركة جديدة
new_company = st.sidebar.text_input("إضافة شركة جديدة:")
if st.sidebar.button("إضافة الشركة"):
    if new_company.strip():
        comp_name = new_company.strip()
        comp_dir = os.path.join(DATA_DIR, comp_name)
        if not os.path.exists(comp_dir):
            os.makedirs(comp_dir, exist_ok=True)
            st.sidebar.success(f"تمت إضافة شركة {comp_name}")
            st.rerun()
        else:
            st.sidebar.warning("الشركة موجودة بالفعل!")
    else:
        st.sidebar.error("يرجى كتابة اسم الشركة")

if existing_companies:
    selected_company = st.sidebar.selectbox("اختر الشركة:", sorted(existing_companies))
    
    # اختيار السنة والشهر
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

    # نموذج إضافة مدفوعات جديدة
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
                new_row = {
                    "التاريخ": date_val,
                    "نوع المعاملة": payment_type,
                    "المبلغ": amount_val,
                    "المستلم": recipient_val.strip(),
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_monthly_data(selected_company, selected_year, selected_month, df)
                st.success("تم تسجيل الحركة بنجاح!")
                st.rerun()
            else:
                st.error("يرجى إدخال المبلغ واسم المستلم بشكل صحيح.")

    st.write("---")
    st.write("### 📋 سجل المدفوعات الحالي")

    if not df.empty:
        # شريط البحث باسم المستلم
        search_query = st.text_input("🔍 بحث باسم المستلم:", "").strip()

        # تصفية الجدول بناءً على البحث
        if search_query:
            filtered_df = df[df["المستلم"].str.contains(search_query, case=False, na=False)]
        else:
            filtered_df = df

        # عرض الجدول القابل للتعديل
        edited_df = st.data_editor(
            filtered_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "نوع المعاملة": st.column_config.SelectboxColumn(
                    "نوع المعاملة",
                    options=["كاش", "تحويل", "شيك"],
                    required=True,
                )
            },
        )

        if st.button("حفظ التعديلات على الجدول"):
            if search_query:
                # تحديث الصفوف التي تم تعديلها فقط في البيانات الأصلية
                df.update(edited_df)
            else:
                df = edited_df
                
            save_monthly_data(selected_company, selected_year, selected_month, df)
            st.success("تم حفظ التعديلات بنجاح!")
            st.rerun()

        # حساب الإجمالي للشهر
        total_amount = df["المبلغ"].sum()
        st.metric(f"إجمالي مصروفات شهر {MONTH_NAMES[selected_month]}", f"{total_amount:,.2f} جنيه")
    else:
        st.info("لا توجد حركات مسجلة لهذه الشركة في هذا الشهر بعد.")
