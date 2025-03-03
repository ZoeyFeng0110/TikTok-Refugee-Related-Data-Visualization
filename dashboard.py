import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# 设置页面标题和布局
st.set_page_config(page_title="TikTok Refugees Topic Trend", layout="wide")
st.title("TikTok Refugees Topic Trend Visualization")

# 自定义CSS样式，添加彩色小标题装饰
st.markdown("""
<style>
    .section-header {
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        font-weight: bold;
        color: white;
    }
    .overview-header {
        background-color: #3498db;  /* 蓝色 */
    }
    .category-header {
        background-color: #2ecc71;  /* 绿色 */
    }
    .trend-header {
        background-color: #9b59b6;  /* 紫色 */
    }
    .date-header {
        background-color: #e67e22;  /* 橙色 */
    }
    .sample-header {
        background-color: #f39c12;  /* 黄色 */
    }
</style>
""", unsafe_allow_html=True)

# 自定义彩色小标题函数
def colored_header(label, color_class):
    st.markdown(f'<div class="section-header {color_class}">{label}</div>', unsafe_allow_html=True)

# 上传CSV文件
uploaded_file = st.file_uploader("Upload your CSV File", type=['csv'])

if uploaded_file is not None:
    # 加载数据
    @st.cache_data
    def load_data(file):
        try:
            df = pd.read_csv(file)
            
            # 打印列名以便调试
            st.write("Column name in CSV file:", list(df.columns))
            
            # 检查'time'列是否存在
            if 'time' not in df.columns:
                st.error("CSV文件中缺少'time'列。请检查列名是否正确。")
                # 显示替代方案
                time_cols = [col for col in df.columns if 'time' in col.lower()]
                if time_cols:
                    st.write("发现可能的时间相关列:", time_cols)
                    # 使用第一个找到的时间列
                    df['time'] = df[time_cols[0]]
                    st.info(f"已使用 '{time_cols[0]}' 作为时间列")
                else:
                    return None
            
            # 将时间戳转换为日期
            df['time'] = pd.to_numeric(df['time'], errors='coerce')
            df['date'] = pd.to_datetime(df['time'], unit='ms').dt.date
            
            # 确保category列存在
            if 'category' not in df.columns:
                st.error("CSV文件中缺少'category'列")
                return None
            
            return df
        except Exception as e:
            st.error(f"加载数据时出错: {str(e)}")
            return None
    
    df = load_data(uploaded_file)
    
    if df is not None:
        # 显示数据概览
        st.subheader("Overview of Data")
        st.write(f"Total Data Count: {len(df)}")
        
        # 数据预处理
        @st.cache_data
        def preprocess_data(df):
            # 确保类别是字符串类型
            df['category'] = df['category'].astype(str)
            
            # 类别映射字典，用于显示更友好的类别名称
            category_names = {
                "1a": "TikTok Ban/Censorship",
                "1b": "Adjusting to RedNote",
                "2a": "Language & Cultural Exchange",
                "2b": "National Identity & Stereotypes",
                "2c": "Food & Lifestyle & Fashion",
                "3a": "Political & Social Movements",
                "3b": "Free Speech & Digital Rights",
                "3c": "Digital Nationalism & Globalization",
                "4": "Marketing & E-Commerce",
                "5a": "Memes & Humor",
                "5b": "Self-Expression & Stories",
                "5c": "Friendship & Community",
                "5d": "Hobbies & Lifestyle",
                "6": "Arts & Creativity",
                "7": "Other",
                "N/A": "N/A"
            }
            
            # 替换类别代码为名称，确保处理NaN值
            df['category_name'] = df['category'].map(lambda x: category_names.get(x, "未分类"))
            
            # 按日期和类别分组，计算每天每个类别的帖子数量
            daily_counts = df.groupby(['date', 'category_name']).size().reset_index(name='count')
            
            # 获取类别列表，确保所有元素都是字符串
            categories = [str(cat) for cat in df['category_name'].unique() if cat is not None and pd.notna(cat)]
            
            return daily_counts, categories
        
        daily_counts, categories = preprocess_data(df)
        
         # 添加类别分布柱状图
        colored_header("All Posts Category Distribution", "category-header")

        # st.subheader("All Posts Category Distribution")
        
        # 计算每个类别的帖子总数
        category_distribution = df['category_name'].value_counts().reset_index()
        category_distribution.columns = ['Category', 'Posts Count']
        
        # 按帖子数量降序排序
        category_distribution = category_distribution.sort_values('Posts Count', ascending=False)
        
        # 创建柱状图
        fig_category = px.bar(
            category_distribution, 
            x='Category', 
            y='Posts Count',
            title='Posts Category Distribution',
            color='Category',  # 使用类别作为颜色区分
            labels={'Category': 'Posts Category', 'Posts Count': 'Number of Posts'}
        )
        
        # 优化布局
        fig_category.update_layout(
            height=500,
            xaxis_tickangle=-45,  # 倾斜x轴标签以便阅读
            showlegend=False  # 隐藏图例，因为颜色已经在X轴标签中显示
        )
        
        # 显示柱状图
        # st.plotly_chart(fig_category, use_container_width=True)
        
        # 添加表格显示具体数据
        col1, col2 = st.columns([3, 2])
        with col1:
            st.plotly_chart(fig_category, use_container_width=True, key="category_chart")
        with col2:
            st.write("Detials of Posts Categories:")
            st.dataframe(category_distribution, height=450)
        
        # 生成趋势图
        # st.subheader("Topic Trend")
        colored_header("Topic Trend", "trend-header")
        
        
        # 安全地对类别进行排序
        try:
            sorted_categories = sorted(categories)
        except Exception as e:
            st.warning(f"排序类别时出错: {str(e)}。将使用未排序的类别列表。")
            sorted_categories = categories
        
        # 选择要显示的类别
        selected_categories = st.multiselect(
            "Choose your Display Catogory", 
            options=sorted_categories,
            default=sorted_categories[:min(5, len(sorted_categories))]  # 默认显示前5个类别
        )
        
        # 过滤选中的类别
        if selected_categories:
            filtered_data = daily_counts[daily_counts['category_name'].isin(selected_categories)]
            
            if len(filtered_data) > 0:
                # 创建趋势图
                fig = px.line(
                    filtered_data, 
                    x='date', 
                    y='count', 
                    color='category_name',
                    title='TikTok Refugees Topic Trends(Group by Catogory)',
                    labels={'date': 'Date', 'count': 'Posts Count', 'category_name': 'Category'}
                )
                
                # 优化布局
                fig.update_layout(
                    height=600,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # 显示图表
                st.plotly_chart(fig, use_container_width=True, key="trend_chart")
                
                # 添加日期详情
                # st.subheader("Check Posts by Day")
                colored_header("Check Posts by Day", "date-header")
                
                # 安全地获取唯一日期
                unique_dates = sorted(df['date'].unique())
                if len(unique_dates) > 0:
                    selected_date = st.selectbox("Select date to check posts", options=unique_dates)
                    
                    if selected_date:
                        # 显示该日期的帖子样例
                        date_posts = df[df['date'] == selected_date]
                        if len(date_posts) > 0:
                            st.markdown(f"#### Detail of posts of {selected_date}")
                            # st.subheader(f"Detail of posts of {selected_date}")
                            # 显示该日期每个类别的帖子数量
                            category_counts = date_posts['category_name'].value_counts().reset_index()
                            category_counts.columns = ['Catogory', 'Count of Posts']
                            st.write("The number of posts of Category:")
                            st.dataframe(category_counts)
                            
                            # 显示帖子样例
                            st.write("Posts Example:")
                            sample_posts = date_posts.sample(min(3, len(date_posts)))
                            
                            for idx, row in sample_posts.iterrows():
                                st.markdown(f"**Title:** {row['title']}")
                                st.markdown(f"**Description:** {row['desc']}")
                                st.markdown(f"**Category:** {row.get('category_name', row['category'])}")
                                st.markdown("---")
                        else:
                            st.info(f"There's no posts example on {selected_date}")
                else:
                    st.info("There's no valied date")
            else:
                st.warning("There's no data in this category")
        else:
            st.warning("Please choose at least one category to display")
else:
    st.info("Please upload CSV file to generate visualization")

# 添加一些使用指南
with st.expander("Usage Guidelines"):
    st.markdown("""
    ### How to Use This Visualization Tool

    1. Upload a CSV file containing TikTok Refugees data
    2. Select the categories you want to view in the multi-select box
    3. View the generated time series trend chart, showing the number of posts over time for each category
    4. In the "View Posts by Date" section, select a specific date to view post details and examples for that date

    ### Data Requirements

    The CSV file must include the following columns:
    - `time`: Timestamp (in milliseconds)
    - `title`: Post title
    - `desc`: Post description
    - `category`: Post category
    """)