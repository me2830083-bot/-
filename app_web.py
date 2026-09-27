import os
import shutil
from datetime import datetime
import pandas as pd
import streamlit as st

# ضبط إعدادات الصفحة وإضافة الأيقونة المميزة (💰)
st.set_page_config(
    page_title="نظام تسجيل المصروفات",
    page_icon="💰",
    layout="wide"
)

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


def load_all_data():
    all_records = []
    if not os.path.exists(DATA_DIR):
        return pd.DataFrame()
    for company in os.listdir(DATA_DIR):
        company_path = os.path.join(DATA_DIR, company)
        if os.path.isdir(company_path):
            for file in os.listdir(company_path):
                if file.endswith(".csv"):
                    filepath = os.path.join(company_path, file)
                    try:
                        df = pd.read_csv(filepath)
                        df["الشركة"] = company
                        all_records.append(df)
                    except Exception:
                        pass
    if all_records:
        full_df = pd.concat(all_records, ignore_index=True)
        if "المبلغ" in full_df.columns:
            full_df["المبلغ"] = pd.to_numeric(full_df["المبلغ"], errors="coerce").fillna(0)
        return full_df
    return pd.DataFrame()


st.title("💰 نظام إدارة وتسجيل المصروفات")

# القائمة الجانبية
st.sidebar.header("النمط والقائمة الجانبية")
app_mode = st.sidebar.radio("اختر الشاشة:", ["إدارة الحركات الشهرية", "📊 الرسم البياني والتحليلات"])

# جلب قائمة الشركات الموجودة (المجلدات)
existing_companies = [
    d for d in os.listdir(DATA_DIR) 
    if os.path.isdir(os.path.join(DATA_DIR, d))
]

if app_mode == "إدارة الحركات الشهرية":
    st.sidebar.header("إدارة الشركات والفترات")

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
            search_query = st.text_input("🔍 بحث باسم المستلم:", "").strip()

            if search_query:
                filtered_df = df[df["المستلم"].str.contains(search_query, case=False, na=False)]
            else:
                filtered_df = df

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
                    df.update(edited_df)
                else:
                    df = edited_df
                    
                save_monthly_data(selected_company, selected_year, selected_month, df)
                st.success("تم حفظ التعديلات بنجاح!")
                st.rerun()

            total_amount = df["المبلغ"].sum()
            st.metric(f"إجمالي مصروفات شهر {MONTH_NAMES[selected_month]}", f"{total_amount:,.2f} جنيه")
        else:
            st.info("لا توجد حركات مسجلة لهذه الشركة في هذا الشهر بعد.")

elif app_mode == "📊 الرسم البياني والتحليلات":
    st.subheader("📈 إحصائيات وإجمالي المدفوعات للشركات")
    
    all_df = load_all_data()
    
    if not all_df.empty and "الشركة" in all_df.columns and "المبلغ" in all_df.columns:
        # رسم بياني لإجمالي الدفعات لكل شركة
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

# قسم مسح البيانات المحمي بكلمة مرور
st.sidebar.markdown("---")
st.sidebar.subheader("⚠️ إدارة البيانات")

with st.sidebar.expander("🗑️ مسح كل البيانات"):
    pwd_input = st.text_input("أدخل كلمة المرور للمسح:", type="password")
    if st.button("تأكيد مسح البيانات"):
        if pwd_input == "2320166120":
            if os.path.exists(DATA_DIR):
                shutil.rmtree(DATA_DIR)
                os.makedirs(DATA_DIR, exist_ok=True)
                st.sidebar.success("تم مسح جميع البيانات بنجاح!")
                st.rerun()
        else:
            st.sidebar.error("كلمة المرور غير صحيحة!")

# حقوق التطوير
st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 **Developed by:** **Mohamed Elsayed**")
