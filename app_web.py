import os
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="نظام تسجيل المصروفات", layout="wide")

# إنشاء مجلد البيانات إذا لم يكن موجوداً
DATA_DIR = "company_data"
os.makedirs(DATA_DIR, exist_ok=True)


def load_company_data(company_name):
    filepath = os.path.join(DATA_DIR, f"{company_name}.csv")
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df["التاريخ"] = pd.to_datetime(df["التاريخ"]).dt.date
        return df
    return pd.DataFrame(
        columns=["التاريخ", "المبلغ", "المستلم", "البيان / السبب"]
    )


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
            df_empty = pd.DataFrame(
                columns=["التاريخ", "المبلغ", "المستلم", "البيان / السبب"]
            )
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

    # نموذج إضافة مدفوعات
    with st.form("payment_form", clear_on_submit=True):
        st.write("### تسجيل حركة جديدة")
        col1, col2 = st.columns(2)
        with col1:
            date_val = st.date_input("التاريخ", datetime.now().date())
            amount_val = st.number_input(
                "المبلغ", min_value=0.0, step=10.0, format="%.2f"
            )
        with col2:
            recipient_val = st.text_input("المستلم")
            notes_val = st.text_input("البيان / السبب")

        submit = st.form_submit_button("حفظ الحركة")

        if submit:
            if amount_val > 0 and recipient_val.strip():
                new_row = {
                    "التاريخ": date_val,
                    "المبلغ": amount_val,
                    "المستلم": recipient_val.strip(),
                    "البيان / السبب": notes_val.strip(),
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_ignore_index=True) if hasattr(pd, "concat") else df
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_company_data(selected_company, df)
                st.success("تم تسجيل الحركة بنجاح!")
                st.rerun()
            else:
                st.error("يرجى إدخال المبلغ واسم المستلم بشكل صحيح.")

    st.write("---")
    st.write("### سجل المدفوعات الحالي")

    if not df.empty:
        # عرض البيانات وإتاحة التعديل/الحذف
        edited_df = st.data_editor(
            df, num_rows="dynamic", use_container_width=True
        )

        if st.button("حفظ التعديلات على الجدول"):
            save_company_data(selected_company, edited_df)
            st.success("تم حفظ التعديلات بنجاح!")
            st.rerun()

        # حساب الإجمالي
        total_amount = edited_df["المبلغ"].sum()
        st.metric("إجمالي المصروفات", f"{total_amount:,.2f}")
    else:
        st.write("لا توجد حركات مسجلة بهذه الشركة بعد.")
