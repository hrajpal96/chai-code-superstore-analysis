import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🛒 Superstore Sales - EDA Dashboard")

def highlight_order_id(s):
    return ['background-color: yellow' if col == 'Order ID' else '' for col in s.index]


uploaded_file = st.file_uploader("Upload Superstore Dataset (CSV)", type=["csv"])
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.dataframe(data, use_container_width=True)
    st.subheader("Raw Data Preview")
    st.dataframe(data.head())
    data_types_df = pd.DataFrame(data.dtypes, columns=["Data Type"])
    data_types_df["Data Type"] = data_types_df["Data Type"].astype(str)  # Fix for Arrow

    # Dataset Overview
    st.markdown("### Dataset Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Shape", f"{data.shape[0]} rows × {data.shape[1]} columns")
        st.dataframe(data_types_df)
    with col2:
        st.metric("Missing Fields", int(data.isnull().sum().sum()))
        st.dataframe(data.isnull().sum()[data.isnull().sum() > 0].rename("Missing Count"))

    st.markdown("### Unique Value Counts")
    st.dataframe(data.nunique().to_frame("Unique Values").T)

    # Step 2: Duplicate Records
    st.markdown("### Duplicate Order IDs Analysis")
    duplicated_rows = data[data.duplicated(keep=False)]
    st.write(f"🔁 Duplicate Rows: {len(duplicated_rows)}")
    if not duplicated_rows.empty:
        st.dataframe(duplicated_rows.style.apply(highlight_order_id, axis=1))
        top_dupes = duplicated_rows['Order ID'].value_counts().head(10).reset_index()
        top_dupes.columns = ['Order ID', 'Count']
        fig = px.bar(top_dupes, x='Count', y='Order ID', orientation='h', title="Top 10 Duplicate Order IDs")
        st.plotly_chart(fig, use_container_width=True)
    data = data.drop_duplicates()

    # Step 3: Order Date Fix
    st.markdown("### Order Date Year Consistency")
    data['Order Date'] = pd.to_datetime(data['Order Date'], errors='coerce', dayfirst=True)
    data['Ship Date'] = pd.to_datetime(data['Ship Date'], errors='coerce', dayfirst=True)
    data['Order ID Year'] = data['Order ID'].str.extract(r'-(\d{4})-').astype(float)
    data['Order Date Year'] = data['Order Date'].dt.year
    mismatches = data['Order ID Year'] != data['Order Date Year']
    data.loc[mismatches, 'Order Date'] = data.loc[mismatches, 'Order Date'].apply(
        lambda dt: dt.replace(year=int(data['Order ID Year'].mode()[0])) if pd.notnull(dt) else dt
    )
    data.drop(columns=['Order ID Year'], inplace=True)

    # Monthly Trend Plot
    st.markdown("### Monthly Order Trend")
    data['Order Month'] = data['Order Date'].dt.to_period('M').astype(str)
    monthly = data.groupby('Order Month').size().reset_index(name='Order Count')
    fig = px.line(monthly, x='Order Month', y='Order Count', markers=True,
                  title="Monthly Order Volume Over Time",
                  labels={'Order Month': 'Month', 'Order Count': 'Number of Orders'})
    
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # Step 4: Shipping & Quantity Cleanup
    st.markdown("### Days to Ship & Quantity Cleanup")
    data['Days to Ship'] = (data['Ship Date'] - data['Order Date']).dt.days
    data['Ship Mode'] = data['Ship Mode'].fillna(data['Days to Ship'].map({0: 'Same Day', 7: 'Standard Class'}))
    data['Quantity'] = pd.to_numeric(data['Quantity'], errors='coerce')
    data = data[~data['Quantity'].isin([np.inf, -np.inf])]
    data['Quantity'] = data['Quantity'].fillna(data['Quantity'].median()).astype(int)
    st.dataframe(data[['Order ID', 'Quantity']].head().style.apply(highlight_order_id, axis=1))

    fig = px.box(data, x='Quantity', title="Typical Quantity Ordered per Transaction")
    st.plotly_chart(fig, use_container_width=True)

    q1 = data['Days to Ship'].quantile(0.25)
    q3 = data['Days to Ship'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 3 * iqr
    upper_bound = q3 + 3 * iqr

    # Filter out extreme outliers using 3*IQR logic
    filtered_days_to_ship = data[(data['Days to Ship'] >= lower_bound) & (data['Days to Ship'] <= upper_bound)]

    # Histogram plot on filtered data
    fig = px.histogram(filtered_days_to_ship, x='Days to Ship', nbins=20,
                    title="How Long Does Shipping Usually Take? (3×IQR Outlier Removal)")
    st.plotly_chart(fig, use_container_width=True)

    # Step 5: Mask Customer Name
    st.markdown("### Customer Privacy Handling")
    data['Customer Name Masked'] = data['Customer Name'].fillna('').apply(
        lambda name: '.'.join([n[0] for n in name.split() if n]) + '.' if name else '')
    data.drop(columns=['Customer Name'], inplace=True)
    initials = data['Customer Name Masked'].value_counts().head(20).reset_index()
    initials.columns = ['Initials', 'Count']
    fig = px.bar(initials, x='Count', y='Initials', orientation='h', title="Top Customer Initials")
    st.plotly_chart(fig, use_container_width=True)

    # Step 6 & 7: Clean State Info
    st.markdown("### Fixing State Names & Types")
    data['Postal Code'] = data['Postal Code'].astype(str).str.zfill(5)
    data['Sales Price'] = pd.to_numeric(data['Sales Price'], errors='coerce')
    data['Profit'] = pd.to_numeric(data['Profit'], errors='coerce')
    abbrev_map = pd.read_csv("https://raw.githubusercontent.com/jasonong/List-of-US-States/master/states.csv")
    mapping = dict(zip(abbrev_map['Abbreviation'], abbrev_map['State']))
    data['State'] = data['State'].replace(mapping)
    top_states = data['State'].value_counts().head(20).reset_index()
    top_states.columns = ['State', 'Orders']
    fig = px.bar(top_states, x='Orders', y='State', orientation='h', title="Top 20 States by Orders")
    st.plotly_chart(fig, use_container_width=True)

    # Step 8: Feature Engineering
    st.markdown("### Feature Enrichment")
    data['Original Price'] = data['Sales Price'] / (1 - data['Discount'].clip(upper=0.99))
    data['Total Sales'] = data['Sales Price'] * data['Quantity']
    data['Total Profit'] = data['Profit'] * data['Quantity']
    data['Discount Price'] = data['Original Price'] - data['Sales Price']
    data['Total Discount'] = data['Discount Price'] * data['Quantity']
    data['Shipping Urgency'] = data['Days to Ship'].apply(
    lambda x: 'Immediate' if x == 0 else ('Urgent' if 1 <= x <= 3 else 'Standard'))

    # Define category order explicitly
    urgency_order = ['Immediate', 'Urgent', 'Standard']
    data['Shipping Urgency'] = pd.Categorical(data['Shipping Urgency'], categories=urgency_order, ordered=True)

    # Plot sorted histogram
    ship_mode = st.selectbox("Choose Ship Mode", data['Ship Mode'].dropna().unique())
    filtered = data[data['Ship Mode'] == ship_mode]

    fig = px.histogram(
        filtered,
        x='Shipping Urgency',
        title=f"Shipping Urgency for {ship_mode}",
        category_orders={'Shipping Urgency': urgency_order}
    )

    st.plotly_chart(fig, use_container_width=True)

    # Step 9: Optional Outlier Cleaning skipped for simplicity

    # Step 10: Customer Segmentation
    st.markdown("### Customer Segmentation Analysis")
    data['Customer ID'] = data['Customer ID'].astype(str)
    cust_seg = data.groupby('Customer ID').agg({'Total Sales': 'sum', 'Total Profit': 'sum'}).reset_index()
    cust_seg['Sales Quintile'] = pd.qcut(cust_seg['Total Sales'], 5, labels=[1,2,3,4,5])
    cust_seg['Profit Quintile'] = pd.qcut(cust_seg['Total Profit'], 5, labels=[1,2,3,4,5])
    data = data.merge(cust_seg[['Customer ID', 'Sales Quintile', 'Profit Quintile']], on='Customer ID', how='left')

    heatmap = pd.crosstab(data['Sales Quintile'], data['Profit Quintile'])
    fig = px.imshow(heatmap.values, x=heatmap.columns.astype(str), y=heatmap.index.astype(str),
                    labels=dict(x="Profit Quintile", y="Sales Quintile", color="Count"),
                    title="Customer Segmentation: Sales vs Profit")
    st.plotly_chart(fig, use_container_width=True)

    # Step 11: Final Profit Insight
    st.markdown("### Most & Least Profitable Products")
    top_profit = data.groupby('Product Name')['Total Profit'].sum().sort_values(ascending=False).head(10).reset_index()
    bottom_profit = data.groupby('Product Name')['Total Profit'].sum().sort_values().head(10).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(top_profit, x='Total Profit', y='Product Name', orientation='h', title="Top 10 Profitable Products")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(bottom_profit, x='Total Profit', y='Product Name', orientation='h', title="Top 10 Loss-Making Products")
        st.plotly_chart(fig, use_container_width=True)

    # Step 12: Download Final Dataset
    if st.download_button("📥 Download Cleaned Dataset", data.to_csv(index=False), file_name="SuperStore_Cleaned.csv"):
        st.success("Download ready.")
