import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import json
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 设置页面标题和布局
st.set_page_config(page_title="TikTok Refugees Related Posts Data Analysis", layout="wide")
st.title("TikTok Refugees Related Posts Data Dashboard")

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
    .geo-header {
        background-color: #e74c3c;  /* 红色 */
    }
    .sample-header {
        background-color: #f39c12;  /* 黄色 */
    }
</style>
""", unsafe_allow_html=True)

# 自定义彩色小标题函数
def colored_header(label, color_class):
    st.markdown(f'<div class="section-header {color_class}">{label}</div>', unsafe_allow_html=True)

# 定义省份中心坐标映射
PROVINCE_CENTERS = {
  "北京": [116.405285, 39.904989],
  "天津": [117.190182, 39.125596],
  "河北": [114.502461, 38.045474],
  "山西": [112.549248, 37.857014],
  "内蒙古": [111.670801, 40.818311],
  "辽宁": [123.429096, 41.796767],
  "吉林": [125.3245, 43.886841],
  "黑龙江": [126.642464, 45.756967],
  "上海": [121.472644, 31.231706],
  "江苏": [118.767413, 32.041544],
  "浙江": [120.153576, 30.287459],
  "安徽": [117.283042, 31.86119],
  "福建": [119.306239, 26.075302],
  "江西": [115.892151, 28.676493],
  "山东": [117.000923, 36.675807],
  "河南": [113.665412, 34.757975],
  "湖北": [114.298572, 30.584355],
  "湖南": [112.982279, 28.19409],
  "广东": [113.280637, 23.125178],
  "广西": [108.320004, 22.82402],
  "海南": [110.33119, 20.031971],
  "重庆": [106.504962, 29.533155],
  "四川": [104.065735, 30.659462],
  "贵州": [106.713478, 26.578343],
  "云南": [102.712251, 25.040609],
  "西藏": [91.132212, 29.660361],
  "陕西": [108.948024, 34.263161],
  "甘肃": [103.823557, 36.058039],
  "青海": [101.778916, 36.623178],
  "宁夏": [106.278179, 38.46637],
  "新疆": [87.617733, 43.792818],
  "台湾": [121.509062, 25.044332],
  "香港": [114.173355, 22.320048],
  "澳门": [113.54909, 22.198951]
}

# 类别映射字典，用于显示更友好的类别名称
CATEGORY_NAMES = {
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

# 帮助函数
def get_available_columns(df):
    # 排除非数值列
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    # 排除ip_location列(如果是数值列)
    if 'ip_location' in numeric_cols:
        numeric_cols.remove('ip_location')
    return numeric_cols

def get_category_columns(df):
    # 检查 DataFrame 是否包含 'category' 列
    return ['category_name'] if 'category_name' in df.columns else []

# 创建标签页
tab1, tab2 = st.tabs(["TikTok Refugees Topic Trend", "TikTok Refugees Topic Geographic Distribution"])

# 上传CSV文件
with st.sidebar:
    st.header("Upload your data")
    uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

# 如果有文件上传
if uploaded_file is not None:
    # 读取CSV文件
    # try:
    @st.cache_data
    def load_data(file):
        df = pd.read_csv(file)
        
        # 查找并处理时间列
        if 'time' in df.columns:
            df['time'] = pd.to_numeric(df['time'], errors='coerce')
            df['date'] = pd.to_datetime(df['time'], unit='ms').dt.date
        
        # 处理类别列
        if 'category' in df.columns:
            df['category'] = df['category'].astype(str)
            df['category_name'] = df['category'].map(lambda x: CATEGORY_NAMES.get(x, x))
        
        return df
    
    df = load_data(uploaded_file)
    st.sidebar.success("File succesfully processed!")
    
    # 数据分析标签页
    with tab1:
        colored_header("overview-header", "overview-header")
        st.write(f"Total number of posts: {len(df)}")
        
        # 类别分布
        if 'category' in df.columns:
            colored_header("category stats", "category-header")
            
            # 计算每个类别的帖子总数
            category_distribution = df['category_name'].value_counts().reset_index()
            category_distribution.columns = ['Catgory', 'Post Count']
            
            # 按帖子数量降序排序
            category_distribution = category_distribution.sort_values('Post Count', ascending=False)
            
            # 创建柱状图
            fig_category = px.bar(
                category_distribution, 
                x='Catgory', 
                y='Post Count',
                title='Post Count of Different Categories of Posts',
                color='Catgory',
                labels={'Catgory': 'Post Catgory', 'Post Count': 'Post Count'}
            )
            
            # 优化布局
            fig_category.update_layout(
                height=500,
                xaxis_tickangle=-45,
                showlegend=False
            )
            
            # 分成两列显示图表和数据
            col1, col2 = st.columns([3, 2])
            with col1:
                st.plotly_chart(fig_category, use_container_width=True)
            with col2:
                st.write("Detailed Category Count Data:")
                st.dataframe(category_distribution, height=450)
            
            # 时间趋势分析
            if 'date' in df.columns:
                colored_header("TikTok Refugees Topic Trend(categorized by category", "trend-header")
                
                # 按日期和类别分组，计算每天每个类别的帖子数量
                daily_counts = df.groupby(['date', 'category_name']).size().reset_index(name='count')
                
                # 获取类别列表
                categories = df['category_name'].unique().tolist()
                sorted_categories = sorted(categories)
                
                # 选择要显示的类别
                selected_categories = st.multiselect(
                    "Choose the catogory you wanna display", 
                    options=sorted_categories,
                    default=sorted_categories[:min(5, len(sorted_categories))]
                )
                
                # 绘制趋势图
                if selected_categories:
                    filtered_data = daily_counts[daily_counts['category_name'].isin(selected_categories)]
                    
                    if len(filtered_data) > 0:
                        # 创建趋势图
                        fig = px.line(
                            filtered_data, 
                            x='date', 
                            y='count', 
                            color='category_name',
                            # title='TikTok Refugees Topic Trend(categorized by category)',
                            labels={'date': 'date', 'count': 'count', 'category_name': 'category'}
                        )
                        
                        # 优化布局
                        fig.update_layout(
                            height=600,
                            margin=dict(t=90, b=70),  # 增加顶部和底部的间距
                            xaxis_title_standoff=20,  # 调整 X 轴标签与图表的距离
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
                        
                        # 显示图表
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Please choose at least one category to display")
                
                # 按日期查看帖子
                colored_header("Check Posts By Date", "date-header")
                
                # 获取唯一日期
                unique_dates = sorted(df['date'].unique())
                if len(unique_dates) > 0:
                    selected_date = st.selectbox("Select a Date Below", options=unique_dates)
                    
                    if selected_date:
                        # 显示该日期的帖子样例
                        date_posts = df[df['date'] == selected_date]
                        if len(date_posts) > 0:
                            
                            
                            # 显示该日期每个类别的帖子数量
                            category_counts = date_posts['category_name'].value_counts().reset_index()
                            category_counts.columns = ['category', 'post_count']
                            st.write("**The number of posts of different category:**")
                            st.dataframe(category_counts)
                            
                            # 显示帖子样例
                            if 'title' in date_posts.columns and 'desc' in date_posts.columns:
                                st.write("**Post Example:**")
                                sample_posts = date_posts.sample(min(3, len(date_posts)))
                                
                                for idx, row in sample_posts.iterrows():
                                    st.markdown(f"**Title:** {row['title']}")
                                    st.markdown(f"**Content:** {row['desc']}")
                                    st.markdown(f"**Category:** {row.get('category_name', row['category'])}")
                                    st.markdown("---")
                        else:
                            st.info(f"{selected_date} No posts data")
                else:
                    st.info("No valid date-data")
        else:
            st.warning("The CSV file lacks of category column")
    
    # 地理分布标签页
    with tab2:
        colored_header("TikTok Refugees Topic Geographic Distribution", "geo-header")
        # 检查是否存在 ip_location 列
        if 'ip_location' not in df.columns:
            st.error("error: couldn't find 'ip_location' column within CSV file")
        else:
            # 确保 ip_location 列为字符串类型
            if df['ip_location'].dtype != 'object':
                df['ip_location'] = df['ip_location'].astype(str)

        # 获取分类列
        category_columns = get_category_columns(df)

        # 只取 "category" 这一列的名字（确保是字符串）
        category_column = category_columns[0] if category_columns else None  

        # 确保 category_column 存在
        if category_column:
            unique_categories = df[category_column].dropna().unique().tolist() if category_column in df.columns else []

            if not unique_categories:
                st.warning(f"列 {category_column} 中没有可用的类别数据")
                selected_category = None
            else:
                # 选择要显示的类别
                selected_category = st.selectbox(
                    "Select the topic you wanna display", 
                    unique_categories,  
                    key="geo_selected_category"
                )

                # 仅保留所选类别的数据
                filtered_df = df[df[category_column] == selected_category] if selected_category != "nan" else df

                # 创建省份数据映射
                province_counts = {}

                # 处理 ip_location，统计每个省份的帖子数量
                unmapped_count = 0

                for index, row in filtered_df.iterrows():
                    location_str = str(row['ip_location'])

                    found_province = False
                    for province_name in PROVINCE_CENTERS.keys():
                        if province_name in location_str:
                            province_counts[province_name] = province_counts.get(province_name, 0) + 1
                            found_province = True
                            break

                    if not found_province:
                        unmapped_count += 1  # 记录未匹配的数量

                # 如果有省份数据，则创建地图
                if province_counts:
                    # 创建 folium 地图
                    m = folium.Map(location=[35.0, 105.0], zoom_start=4)

                    # 添加地图标题
                    title_html = f'''<h3 align="center" style="font-size:16px"><b>TikTok Refugees Topic Geographic Distribution</b>'''
                    if selected_category != "All":
                        title_html += f''' - category: {selected_category}</h3>'''
                    else:
                        title_html += '''</h3>'''

                    m.get_root().html.add_child(folium.Element(title_html))

                    # 尝试加载 GeoJSON
                    try:
                        geojson_url = "https://raw.githubusercontent.com/apache/echarts/master/map/json/china.json"
                        response = requests.get(geojson_url)
                        china_geojson = response.json()
                    except Exception as e:
                        china_geojson = None

                    # 选择可视化方式
                    if china_geojson is not None:
                        # 创建 DataFrame 供 Choropleth 使用
                        choropleth_data = pd.DataFrame([
                            {"province": province, "count": count}
                            for province, count in province_counts.items()
                        ])

                        try:
                            folium.Choropleth(
                                geo_data=china_geojson,
                                name='choropleth',
                                data=choropleth_data,
                                columns=['province', 'count'],
                                key_on='feature.properties.name',
                                fill_color='YlOrRd',
                                fill_opacity=0.7,
                                line_opacity=0.2,
                                legend_name='Post Count Distribution'
                            ).add_to(m)

                            # 为每个省份添加文本标注
                            for province, count in province_counts.items():
                                if province in PROVINCE_CENTERS:
                                    lat, lon = PROVINCE_CENTERS[province][1], PROVINCE_CENTERS[province][0]
                                    popup_text = f"{province}: {count} posts"
                                    folium.Marker(
                                        [lat, lon],
                                        popup=popup_text,
                                        icon=folium.DivIcon(
                                            icon_size=(0, 0),
                                            html=f'<div style="font-size: 10pt">{province}</div>',
                                        )
                                    ).add_to(m)

                            folium.LayerControl().add_to(m)
                        except Exception as e:
                            st.error(f"创建 Choropleth 地图时出错: {e}")
                            st.warning("将回退到基于点的热力图")

                            # 创建热力图数据
                            heat_data = []
                            for province, count in province_counts.items():
                                if province in PROVINCE_CENTERS:
                                    lat, lon = PROVINCE_CENTERS[province][1], PROVINCE_CENTERS[province][0]
                                    heat_data.append([lat, lon, count])

                            # 添加热力图层
                            HeatMap(heat_data).add_to(m)
                    else:
                        # 如果没有 GeoJSON，则创建点热力图
                        heat_data = []
                        for province, count in province_counts.items():
                            if province in PROVINCE_CENTERS:
                                lat, lon = PROVINCE_CENTERS[province][1], PROVINCE_CENTERS[province][0]
                                heat_data.append([lat, lon, count])

                        # 添加热力图层
                        HeatMap(heat_data).add_to(m)

                    # 显示地图
                    map_title = "Topic Heat-Map"
                    if category_column:
                        map_title += f" (category: {selected_category})"

                    # 将 province_counts 转换为 DataFrame 以便展示
                    province_count_df = pd.DataFrame(
                        list(province_counts.items()), columns=["Province", "Post Count"]
                    ).sort_values(by="Post Count", ascending=False)
                    
                    st.subheader(map_title)
                    # 创建左右布局
                    col1, spacer, col2 = st.columns([3, 0.5, 1]) # 75% 地图 + 25% 表格

                    with col1:
                        folium_static(m)  # 在左侧显示地图

                    # spacer 为空列，用于增加间距

                    with col2:
                        st.dataframe(province_count_df.set_index("Province"), height=500)  # 调整表格高度，使其与地图对齐

                else:
                    st.warning("Failed to match location data to any province")



# Guiding Section
with st.sidebar.expander("User Guide"):
    st.markdown("""
    ### How to Use This Visualization Tool

    1. Upload a CSV file containing TikTok Refugees data.
    2. In the "Data Analysis" tab:
       - View category distribution statistics.
       - Select a category to generate a time trend chart.
       - Choose a specific date to view post details.
    3. In the "Geographic Distribution" tab:
       - Select a category to view the geographic heatmap for different topics.

    ### Data Requirements

    The CSV file should include the following columns:
    - `time`: Timestamp (milliseconds)
    - `title`: Post title
    - `desc`: Post description
    - `category`: Post category
    - `ip_location`: IP geographic location

    Other numerical columns will be used for heatmap weight calculations.
    """)
