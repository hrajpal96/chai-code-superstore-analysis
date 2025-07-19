import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("🛒 Superstore Sales - EDA Case Study")

uploaded_file = st.file_uploader("Upload Superstore Dataset (CSV)", type=["csv"])
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.subheader("Raw Data Preview")
    st.dataframe(data.head())

    # Step 1: Basic metadata
    st.markdown("### Dataset Info")
    st.write("Shape:", data.shape)
    st.write("Data Types:", data.dtypes)
    st.write("Missing Values:", data.isnull().sum()[data.isnull().sum() > 0])
    st.markdown("### Unique Values")
    st.dataframe(data.nunique().to_frame().T)

    # Heatmap for missing values
    if st.checkbox("Show Missing Value Heatmap"):
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(data.isnull(), cbar=False, cmap="viridis", ax=ax)
        st.pyplot(fig)

    # Step 2: Duplicate Records
    st.markdown("### Step 2: Duplicate Records")
    duplicated_rows = data[data.duplicated(keep=False)]
    st.write(f"Duplicate rows: {len(duplicated_rows)}")
    if not duplicated_rows.empty:
        st.dataframe(
    duplicated_rows.style.highlight(
            lambda x: ['background-color: yellow'] * len(x),
            subset=['Order ID']
        )
    )
        st.bar_chart(duplicated_rows['Order ID'].value_counts().head(10))
    data = data.drop_duplicates()

    # Step 3: Date Handling
    st.markdown("### Step 3: Date Handling")
    data['Order Date'] = pd.to_datetime(data['Order Date'], errors='coerce', dayfirst=True)
    data['Ship Date'] = pd.to_datetime(data['Ship Date'], errors='coerce', dayfirst=True)
    data['Order ID Year'] = data['Order ID'].str.extract(r'-(\d{4})-').astype(float)
    data['Order Date Year'] = data['Order Date'].dt.year
    data.loc[data['Order ID Year'] != data['Order Date Year'], 'Order Date'] = \
        data.loc[data['Order ID Year'] != data['Order Date Year'], 'Order Date'].apply(
            lambda dt: dt.replace(year=int(data['Order ID Year'].mode()[0])) if pd.notnull(dt) else dt
        )
    data.drop(columns=['Order ID Year'], inplace=True)
    st.dataframe(data.head().style.highlight_subset(['Order ID', 'Order Date'], color='lightblue'))

    # Step 4: Impute & Clean
    st.markdown("### Step 4: Cleaning Days to Ship and Quantity")
    data['Days to Ship'] = (data['Ship Date'] - data['Order Date']).dt.days
    data['Ship Mode'] = data['Ship Mode'].fillna(data['Days to Ship'].map({0: 'Same Day', 7: 'Standard Class'}))
    data['Quantity'] = pd.to_numeric(data['Quantity'], errors='coerce')
    data = data[~data['Quantity'].isin([np.inf, -np.inf])]
    data['Quantity'].fillna(data['Quantity'].median(), inplace=True)
    data['Quantity'] = data['Quantity'].astype(int)
    st.dataframe(data.head().style.highlight_subset(['Days to Ship', 'Quantity'], color='lightyellow'))

    # Step 5: Mask Customer Name
    st.markdown("### Step 5: Mask Customer Name")
    data['Customer Name Masked'] = data['Customer Name'].fillna('').apply(
        lambda name: '.'.join([n[0] for n in name.split() if n]) + '.' if name else '')
    data.drop(columns=['Customer Name'], inplace=True)
    st.dataframe(data.head().style.highlight_subset(['Customer Name Masked'], color='lightgreen'))

    # Step 6: Type Conversion
    st.markdown("### Step 6: Type Conversion")
    data['Postal Code'] = data['Postal Code'].astype(str).str.zfill(5)
    data['Sales Price'] = pd.to_numeric(data['Sales Price'], errors='coerce')
    data['Profit'] = pd.to_numeric(data['Profit'], errors='coerce')

    # Step 7: Replace State Abbreviations
    st.markdown("### Step 7: Replace State Abbreviations")
    abbrev_map = pd.read_csv("https://raw.githubusercontent.com/jasonong/List-of-US-States/master/states.csv")
    mapping = dict(zip(abbrev_map['Abbreviation'], abbrev_map['State']))
    data['State'] = data['State'].replace(mapping)
    st.dataframe(data.head().style.highlight_subset(['State'], color='lightcoral'))

    # Step 8: Feature Engineering
    st.markdown("### Step 8: Feature Engineering")
    data['Original Price'] = data['Sales Price'] / (1 - data['Discount'].clip(upper=0.99))
    data['Total Sales'] = data['Sales Price'] * data['Quantity']
    data['Total Profit'] = data['Profit'] * data['Quantity']
    data['Discount Price'] = data['Original Price'] - data['Sales Price']
    data['Total Discount'] = data['Discount Price'] * data['Quantity']
    data['Shipping Urgency'] = data['Days to Ship'].apply(
        lambda x: 'Immediate' if x == 0 else ('Urgent' if 1 <= x <= 3 else 'Standard'))
    st.dataframe(data.head().style.highlight(['Total Sales', 'Total Profit'], color='lightcyan'))

    # Step 9: Visualization - Shipping Urgency
    st.markdown("### Step 9: Shipping Urgency Distribution")
    fig, ax = plt.subplots()
    sns.countplot(data=data, x='Shipping Urgency', order=['Immediate', 'Urgent', 'Standard'], ax=ax)
    st.pyplot(fig)

    # Step 10: Save Output
    if st.button("Download Cleaned Data"):
        data.to_csv("SuperStore_Cleaned_Streamlit.csv", index=False)
        st.success("Data saved as SuperStore_Cleaned_Streamlit.csv")