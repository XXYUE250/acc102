import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 页面设置
st.set_page_config(page_title="Superstore Sales Dashboard", layout="wide", page_icon="🛒")
st.title("🛒 Superstore Sales Executive Dashboard")

# 用折叠面板收纳说明
with st.expander("📖 About This Data Product (Click to expand)"):
    st.markdown("""
    **Problem Definition:** This interactive tool helps Regional Sales Managers analyze historical sales data to identify trends, best-selling categories, and geographical performance. 
    **Target User:** Business Analysts & Regional Sales Managers.
    """)


# 2. 数据加载与清洗
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("superstore_final_dataset (1).csv", encoding='windows-1252')
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d/%m/%Y', errors='coerce')

    # 修复 ArrowInvalid 报错：将 Postal_Code 整列转换为字符串，再填补缺失值
    df['Postal_Code'] = df['Postal_Code'].astype(str)
    df['Postal_Code'] = df['Postal_Code'].replace('nan', 'Unknown')

    df['Year'] = df['Order_Date'].dt.year
    df['Month'] = df['Order_Date'].dt.month
    return df


df = load_and_clean_data()

# 3. 侧边栏交互组件
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3094/3094936.png", width=100)
st.sidebar.header("🔍 Filter Dashboard")

years = df['Year'].dropna().unique()
regions = df['Region'].unique()
categories = df['Category'].unique()

selected_year = st.sidebar.multiselect("📅 Select Year", options=years, default=years)
selected_region = st.sidebar.multiselect("🌍 Select Region", options=regions, default=regions)
selected_category = st.sidebar.multiselect("📦 Select Category", options=categories, default=categories)

# 过滤数据
filtered_df = df[
    (df['Year'].isin(selected_year)) &
    (df['Region'].isin(selected_region)) &
    (df['Category'].isin(selected_category))
    ]

# 4. 核心指标卡 (KPIs)
col1, col2, col3, col4 = st.columns(4)
total_sales = filtered_df['Sales'].sum()
total_orders = filtered_df['Order_ID'].nunique()
avg_sales = filtered_df['Sales'].mean()
total_customers = filtered_df['Customer_ID'].nunique()

col1.metric("💰 Total Sales", f"${total_sales:,.2f}")
col2.metric("📦 Total Orders", f"{total_orders:,}")
col3.metric("👥 Total Customers", f"{total_customers:,}")
col4.metric("📊 Avg Sales/Item", f"${avg_sales:,.2f}")

st.markdown("---")

# 5. 自动生成智能洞察
if not filtered_df.empty:
    top_state = filtered_df.groupby('State')['Sales'].sum().idxmax()
    top_month = filtered_df.groupby('Month')['Sales'].sum().idxmax()
    top_category = filtered_df.groupby('Category')['Sales'].sum().idxmax()

    st.info(
        f"💡 **Automated Insights:** Based on your current filters, the highest revenue is generated in **{top_state}**. "
        f"The best-performing month is **Month {int(top_month)}**, and the leading category is **{top_category}**.")
else:
    st.warning("No data available for the selected filters.")

# 6. 标签页布局
tab1, tab2, tab3 = st.tabs(["📈 Business Overview", "🗺️ Geography & Hierarchy", "📁 Raw Data & Export"])

# ---------- 标签页 1：业务总览 ----------
with tab1:
    c1, c2 = st.columns([2, 1])
    with c1:
        sales_by_date = filtered_df.groupby('Order_Date')['Sales'].sum().reset_index()
        fig_line = px.line(sales_by_date, x='Order_Date', y='Sales', title='Sales Trend Over Time',
                           color_discrete_sequence=['#1f77b4'])
        # 修复未来版本警告：替换为 width='stretch'
        st.plotly_chart(fig_line, width='stretch')

    with c2:
        sales_by_segment = filtered_df.groupby('Segment')['Sales'].sum().reset_index()
        fig_pie = px.pie(sales_by_segment, values='Sales', names='Segment', title='Sales by Customer Segment',
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, width='stretch')

    c3, c4 = st.columns(2)
    with c3:
        sales_by_subcategory = filtered_df.groupby('Sub_Category')['Sales'].sum().reset_index()
        sales_by_subcategory = sales_by_subcategory.sort_values(by='Sales', ascending=True)
        fig_bar = px.bar(sales_by_subcategory, x='Sales', y='Sub_Category', orientation='h',
                         title='Sales by Sub-Category', color='Sales', color_continuous_scale='Blues')
        st.plotly_chart(fig_bar, width='stretch')

    with c4:
        top_products = filtered_df.groupby('Product_Name')['Sales'].sum().nlargest(10).reset_index()
        top_products = top_products.sort_values(by='Sales', ascending=True)
        fig_top10 = px.bar(top_products, x='Sales', y='Product_Name', orientation='h',
                           title='Top 10 Best-Selling Products', color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig_top10, width='stretch')

# ---------- 标签页 2：地理与层级分析 ----------
with tab2:
    c5, c6 = st.columns(2)
    with c5:
        sales_by_state = filtered_df.groupby('State')['Sales'].sum().reset_index()
        state_abbr = {
            'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
            'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
            'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
            'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
            'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
            'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
            'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
            'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
            'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
            'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
            'District of Columbia': 'DC'
        }
        sales_by_state['State_Abbr'] = sales_by_state['State'].map(state_abbr)
        fig_map = px.choropleth(
            sales_by_state, locations='State_Abbr', locationmode="USA-states",
            color='Sales', hover_name='State', scope="usa",
            color_continuous_scale="Viridis", title='Total Sales by State (USA)'
        )
        st.plotly_chart(fig_map, width='stretch')

    with c6:
        fig_tree = px.treemap(filtered_df, path=['Category', 'Sub_Category'], values='Sales',
                              title='Sales Hierarchy (Category -> Sub-Category)',
                              color='Sales', color_continuous_scale='Teal')
        st.plotly_chart(fig_tree, width='stretch')

# ---------- 标签页 3：数据探索与导出 ----------
with tab3:
    st.markdown("You can review the raw data table below and export it for further analysis in Excel.")
    # 这里的 use_container_width 在 dataframe 中不需要改，因为警告是针对 chart 元素的
    st.dataframe(filtered_df, use_container_width=True)

    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name='filtered_superstore_sales.csv',
        mime='text/csv'
    )