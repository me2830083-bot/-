import os
import shutil
from datetime import datetime
import pandas as pd
import streamlit as st

# ضبط إعدادات الصفحة وإضافة الأيقونة المميزة (💰)
st.set_page_config(
    page_title="نظام إدارة الوارد وعُهد الموظفين",
    page_icon="💰",
    layout="wide"
)

# مجلدات البيانات الرئيسية
DATA_DIR = "company_data"         # خاص بالوارد من الشركات فقط
EMPLOYEES_DIR = "employees_data"  # خاص بحسابات وعُهد الموظفين
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EMPLOYEES_DIR, exist_ok=True)

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


# دوال خاصة بإدارة حسابات الموظفين
def get_employee_month_filepath(employee_name, year, month):
    emp_folder = os.path.join(EMPLOYEES_DIR, employee_name)
    os.makedirs(emp_folder, exist_ok=True)
    filename = f"{employee_name}_{year}_{month:02d}_custody.csv"
    return os.path.join(emp_folder, filename)


def add_employee_custody(employee_name, date_val, payment_type, amount):
    year = date_val.year
    month = date_val.month
    filepath = get_employee_month_filepath(employee_name, year, month)
    
    cols = ["التاريخ", "نوع المعاملة", "اسم الموظف", "المبلغ المنصرف كعهدة"]
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        if "نوع المعاملة" not in df.columns:
            df.insert(1, "نوع المعاملة", "صرف تحويل")
    else:
        df = pd.DataFrame(columns=cols)
    
    new_row = {
        "التاريخ": date_val,
        "نوع المعاملة": payment_type,
        "اسم الموظف": employee_name,
        "المبلغ المنصرف كعهدة": amount
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
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


def load_all_custody_data():
    all_records = []
    if not os.path.exists(EMPLOYEES_DIR):
        return pd.DataFrame()
    for emp in os.listdir(EMPLOYEES_DIR):
        emp_path = os.path.join(EMPLOYEES_DIR, emp)
        if os.path.isdir(emp_path):
            for file in os.listdir(emp_path):
                if file.endswith("_custody.csv"):
                    filepath = os.path.join(emp_path, file)
                    try:
                        df = pd.read_csv(filepath)
                        if "نوع المعاملة" not in df.columns:
                            df.insert(1, "نوع المعاملة", "صرف تحويل")
                        all_records.append(df)
                    except Exception:
                        pass
    if all_records:
        full_df = pd.concat(all_records, ignore_index=True)
        if "المبلغ المنصرف كعهدة" in full_df.columns:
            full_df["المبلغ المنصرف كعهدة"] = pd.to_numeric(full_df["المبلغ المنصرف كعهدة"], errors="coerce").fillna(0)
        return full_df
    return pd.DataFrame()


# حساب إجمالي الخزينة (إجمالي الوارد - إجمالي العهد المنصرفة)
all_incoming_df = load_all_data()
all_custody_df = load_all_custody_data()

total_incoming_treasury = all_incoming_df["المبلغ"].sum() if not all_incoming_df.empty else 0.0
total_custody_treasury = all_custody_df["المبلغ المنصرف كعهدة"].sum() if not all_custody_df.empty else 0.0
treasury_balance = total_incoming_treasury - total_custody_treasury


st.title("💰 نظام إدارة الوارد وعُهد الموظفين")

# عرض ملخص الخزينة بشكل احترافي ومنسق في الشريط الجانبي
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏦 **ملخص حركة الخزينة**")

with st.sidebar.container():
    st.markdown(f"""
    <div style='background-color: #1e2530; padding: 12px; border-radius: 8px; border: 1px solid #2f3742;'>
        <p style='margin: 4px 0; color: #a3bffa; font-size: 14px;'>📥 <b>إجمالي الوارد:</b> <span style='float: left; color: #ffffff;'>{total_incoming_treasury:,.2f} ج</span></p>
        <p style='margin: 4px 0; color: #f6ad55; font-size: 14px;'>📤 <b>إجمالي العهد:</b> <span style='float: left; color: #ffffff;'>{total_custody_treasury:,.2f} ج</span></p>
        <hr style='margin: 8px 0; border-color: #2f3742;'>
        <p style='margin: 4px 0; color: #68d391; font-size: 15px;'>💰 <b>الرصيد المتبقي:</b><br><span style='font-size: 18px; font-weight: bold; color: #68d391;'>{treasury_balance:,.2f} جنيه</span></p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")

# القائمة الجانبية مع إضافة "الواجهة الرئيسية" في المقدمة
st.sidebar.header("النمط والقائمة الجانبية")
app_mode = st.sidebar.radio(
    "اختر الشاشة:", 
    ["🏠 الواجهة الرئيسية (لوحة المؤشرات)", "إدارة الوارد من الشركات", "👤 حسابات وعُهد الموظفين", "📊 الرسم البياني والتحليلات"]
)

# جلب قائمة الشركات الموجودة
existing_companies = [
    d for d in os.listdir(DATA_DIR) 
    if os.path.isdir(os.path.join(DATA_DIR, d))
]

if app_mode == "🏠 الواجهة الرئيسية (لوحة المؤشرات)":
    st.subheader("🏠 الواجهة الرئيسية - لوحة المؤشرات والتحليلات البصرية")
    
    # 1. تصميم بطاقات KPI احترافية وملونة
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style='background-color: #1a365d; padding: 16px; border-radius: 10px; border-left: 5px solid #3182ce;'>
            <p style='color: #bee3f8; margin: 0; font-size: 14px;'>📥 إجمالي الوارد العام</p>
            <h3 style='color: #ffffff; margin: 5px 0 0 0;'>{total_incoming_treasury:,.2f} ج</h3>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='background-color: #744210; padding: 16px; border-radius: 10px; border-left: 5px solid #d69e2e;'>
            <p style='color: #feebc8; margin: 0; font-size: 14px;'>📤 إجمالي الصرف / العهد</p>
            <h3 style='color: #ffffff; margin: 5px 0 0 0;'>{total_custody_treasury:,.2f} ج</h3>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        balance_color = "#22543d" if treasury_balance >= 0 else "#742a2a"
        border_color = "#38a169" if treasury_balance >= 0 else "#e53e3e"
        st.markdown(f"""
        <div style='background-color: {balance_color}; padding: 16px; border-radius: 10px; border-left: 5px solid {border_color};'>
            <p style='color: #c6f6d5; margin: 0; font-size: 14px;'>💰 الرصيد المتبقي بالخزينة</p>
            <h3 style='color: #ffffff; margin: 5px 0 0 0;'>{treasury_balance:,.2f} ج</h3>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # 2. تنويع الأشكال: عرض مقارنة الشركات (أعمدة) بجانب توزيع الوارد (مخطط مساحي / خطي)
    r1_col1, r1_col2 = st.columns(2)
    
    with r1_col1:
        st.write("#### 🏢 حصة كل شركة من إجمالي الوارد")
        if not all_incoming_df.empty and "الشركة" in all_incoming_df.columns:
            company_totals = all_incoming_df.groupby("الشركة")["المبلغ"].sum().reset_index()
            # عرض مخطط أعمدة تنافسي
            st.bar_chart(company_totals.set_index("الشركة")["المبلغ"])
        else:
            st.info("لا توجد بيانات شركات مسجلة بعد.")
            
    with r1_col2:
        st.write("#### 💳 تحليل حركة السيولة حسب (نوع المعاملة)")
        if not all_incoming_df.empty and "نوع المعاملة" in all_incoming_df.columns:
            incoming_type_totals = all_incoming_df.groupby("نوع المعاملة")["المبلغ"].sum().reset_index()
            # استخدام مخطط خطي متغير (Line Chart) للتنويع البصري
            st.line_chart(incoming_type_totals.set_index("نوع المعاملة")["المبلغ"])
        else:
            st.info("لا توجد بيانات وارد مسجلة بعد.")
            
    st.markdown("---")
    
    # 3. قسم خاص بمقارنة المصروفات والعهد بطريقة مميزة
    st.write("#### 📊 مقارنة تفصيلية لحركات الصرف والعهد حسب نوع المعاملة")
    if not all_custody_df.empty and "نوع المعاملة" in all_custody_df.columns:
        custody_type_totals = all_custody_df.groupby("نوع المعاملة")["المبلغ المنصرف كعهدة"].sum().reset_index()
        st.bar_chart(custody_type_totals.set_index("نوع المعاملة")["المبلغ المنصرف كعهدة"])
    else:
        st.info("لا توجد حركات صرف مسجلة بعد.")

elif app_mode == "إدارة الوارد من الشركات":
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

    companies_options = ["الكل"] + sorted(existing_companies)
    selected_company = st.sidebar.selectbox("اختر الشركة / العرض:", companies_options)
    
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

    if selected_company == "الكل":
        st.subheader(f"🏢 جميع الشركات | 📅 سجل شهر: {MONTH_NAMES[selected_month]} {selected_year}")
        
        all_months_records = []
        for comp in existing_companies:
            comp_df = load_monthly_data(comp, selected_year, selected_month)
            if not comp_df.empty:
                comp_df["الشركة"] = comp
                all_months_records.append(comp_df)
        
        if all_months_records:
            df_all = pd.concat(all_months_records, ignore_index=True)
            total_all_amount = df_all["المبلغ"].sum()
            
            st.write("### 📋 سجل الوارد الشامل لكل الشركات لهذا الشهر")
            st.dataframe(df_all[["الشركة", "التاريخ", "نوع المعاملة", "المبلغ", "المستلم"]].style.format({"المبلغ": "{:,.2f} جنيه"}), use_container_width=True)
            st.metric(f"إجمالي الوارد لكل الشركات لشهر {MONTH_NAMES[selected_month]}", f"{total_all_amount:,.2f} جنيه")
        else:
            st.info("لا توجد حركات مسجلة لجميع الشركات في هذا الشهر بعد.")
            
    else:
        st.subheader(f"🏢 الشركة: {selected_company} | 📅 سجل شهر: {MONTH_NAMES[selected_month]} {selected_year}")

        df = load_monthly_data(selected_company, selected_year, selected_month)

        # نموذج إضافة حركة جديدة مع خيارات الصرف الجديدة
        with st.form("payment_form", clear_on_submit=True):
            st.write("### ➕ تسجيل حركة جديدة (وارد أو صرف)")
            st.caption(f"💡 **المتبقي في الخزينة:** {treasury_balance:,.2f} جنيه")

            col1, col2, col3 = st.columns(3)
            with col1:
                date_val = st.date_input("التاريخ", datetime.now().date())
            with col2:
                payment_type = st.selectbox(
                    "نوع المعاملة", 
                    ["وارد كاش", "وارد تحويل", "وارد شيك", "صرف كاش", "صرف تحويل", "صرف شيك"]
                )
                amount_val = st.number_input("المبلغ", min_value=0.0, step=10.0, format="%.2f")
            with col3:
                recipient_val = st.text_input("جهة الوارد / اسم الموظف للصرف")

            submit = st.form_submit_button("حفظ الحركة")

            if submit:
                if amount_val > 0 and recipient_val.strip():
                    name_val = recipient_val.strip()
                    
                    if payment_type.startswith("صرف"):
                        if amount_val > treasury_balance:
                            st.error(f"⚠️ تنبيه: المبلغ المطلوب ({amount_val:,.2f} جنيه) أكبر من المتبقي في الخزينة ({treasury_balance:,.2f} جنيه)!")
                        else:
                            add_employee_custody(name_val, date_val, payment_type, amount_val)
                            new_treasury = treasury_balance - amount_val
                            st.success(f"تم تنفيذ مبلغ {amount_val:,.2f} جنيه ({payment_type}) للمستفيد: {name_val} بنجاح. | المتبقي في الخزينة: {new_treasury:,.2f} جنيه")
                            st.rerun()
                    else:
                        new_row = {
                            "التاريخ": date_val,
                            "نوع المعاملة": payment_type,
                            "المبلغ": amount_val,
                            "المستلم": name_val,
                        }
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        save_monthly_data(selected_company, selected_year, selected_month, df)
                        st.success("تم تسجيل الوارد للشركة بنجاح!")
                        st.rerun()
                else:
                    st.error("يرجى إدخال المبلغ والاسم بشكل صحيح.")

        st.write("---")
        st.write("### 📋 سجل الوارد الحالي للشركة")

        if not df.empty:
            search_query = st.text_input("🔍 بحث في الوارد:", "").strip()

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
                        options=["وارد كاش", "وارد تحويل", "وارد شيك"],
                        required=True,
                    )
                },
            )

            if "edit_authenticated" not in st.session_state:
                st.session_state.edit_authenticated = False

            if not st.session_state.edit_authenticated:
                edit_pwd = st.text_input("🔒 أدخل كلمة المرور لتفعيل حفظ التعديلات على الجدول:", type="password")
                if st.button("التحقق من كلمة المرور"):
                    if edit_pwd == "2320155120":
                        st.session_state.edit_authenticated = True
                        st.success("كلمة المرور صحيحة، يمكنك حفظ التعديلات الآن!")
                        st.rerun()
                    else:
                        st.error("كلمة المرور الخاصة بالتعديل غير صحيحة!")
            else:
                st.info("✅ تم التحقق من كلمة المرور بنجاح. يمكنك حفظ التعديلات.")
                if st.button("حفظ التعديلات على الجدول"):
                    if search_query:
                        df.update(edited_df)
                    else:
                        df = edited_df
                        
                    save_monthly_data(selected_company, selected_year, selected_month, df)
                    st.session_state.edit_authenticated = False
                    st.success("تم حفظ التعديلات بنجاح!")
                    st.rerun()

            total_amount = df["المبلغ"].sum()
            st.metric(f"إجمالي الوارد لشهر {MONTH_NAMES[selected_month]}", f"{total_amount:,.2f} جنيه")
        else:
            st.info("لا توجد حركات وارد مسجلة لهذه الشركة في هذا الشهر بعد.")

elif app_mode == "👤 حسابات وعُهد الموظفين":
    st.subheader("👤 تقرير حسابات وعُهد الموظفين")
    
    st.sidebar.header("فلترة عهد الموظفين بالفترة")
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    emp_selected_year = st.sidebar.number_input(
        "سنة العهد:", min_value=2020, max_value=2035, value=current_year, step=1, key="emp_year"
    )
    emp_selected_month = st.sidebar.selectbox(
        "شهر العهد:", 
        options=list(MONTH_NAMES.keys()), 
        format_func=lambda x: MONTH_NAMES[x],
        index=current_month - 1,
        key="emp_month"
    )

    employees = [
        d for d in os.listdir(EMPLOYEES_DIR) 
        if os.path.isdir(os.path.join(EMPLOYEES_DIR, d))
    ]
    
    if employees:
        options_list = ["الكل"] + sorted(employees)
        selected_employee = st.selectbox("اختر اسم الموظف لاستعراض عهده:", options_list)
        
        if selected_employee == "الكل":
            all_custody_records = []
            for emp in employees:
                emp_file = get_employee_month_filepath(emp, emp_selected_year, emp_selected_month)
                if os.path.exists(emp_file):
                    emp_df = pd.read_csv(emp_file)
                    if "نوع المعاملة" not in emp_df.columns:
                        emp_df.insert(1, "نوع المعاملة", "صرف تحويل")
                    all_custody_records.append(emp_df)
            
            if all_custody_records:
                full_custody_df = pd.concat(all_custody_records, ignore_index=True)
                total_all_custody = full_custody_df["المبلغ المنصرف كعهدة"].sum()
                
                if total_all_custody > total_incoming_treasury:
                    st.warning(f"⚠️ **تنبيه هام:** إجمالي الصرف ({total_all_custody:,.2f} جنيه) أكبر من إجمالي الوارد العام ({total_incoming_treasury:,.2f} جنيه)!")

                st.metric(f"إجمالي الصرف لجميع الموظفين لشهر {MONTH_NAMES[emp_selected_month]}", f"{total_all_custody:,.2f} جنيه")
                st.write("---")
                st.write(f"### 📄 دفتر شامل لكل حركات الصرف للموظفين لشهر {MONTH_NAMES[emp_selected_month]} {emp_selected_year}:")
                st.dataframe(full_custody_df.style.format({"المبلغ المنصرف كعهدة": "{:,.2f} جنيه"}), use_container_width=True)
            else:
                st.info(f"لا توجد أي سجلات صرف مسجلة لشهر {MONTH_NAMES[emp_selected_month]} {emp_selected_year}.")
        else:
            emp_file = get_employee_month_filepath(selected_employee, emp_selected_year, emp_selected_month)
            if os.path.exists(emp_file):
                emp_df = pd.read_csv(emp_file)
                if "نوع المعاملة" not in emp_df.columns:
                    emp_df.insert(1, "نوع المعاملة", "صرف تحويل")
                
                total_custody = emp_df["المبلغ المنصرف كعهدة"].sum() if not emp_df.empty else 0
                st.metric(f"إجمالي الصرف للموظف: {selected_employee} ({MONTH_NAMES[emp_selected_month]})", f"{total_custody:,.2f} جنيه")
                
                st.write("---")
