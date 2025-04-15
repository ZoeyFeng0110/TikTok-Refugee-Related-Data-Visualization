# TikTok Refugees Related Posts Data Dashboard

## Overview
This Streamlit-based dashboard provides interactive visualizations for analyzing posts related to "TikTok Refugees." It allows users to explore trends, category distributions, and geographic insights based on uploaded data.

## Features
- **Data Upload**: Users can upload a CSV file for analysis.
- **Category Distribution**: Visualize the distribution of posts across different categories.
- **Time Trends**: Track topic trends over time with interactive line charts.
- **Geographic Analysis**: View post distribution on a province-level heatmap or choropleth map.
- **Post Exploration**: Filter and examine posts by category and date.

## Installation
Ensure you have Python installed, then install the required dependencies:
```bash
pip install streamlit pandas numpy folium streamlit-folium plotly requests
```

## Running the App
To launch the dashboard, run:
```bash
streamlit run app.py
```

## Online Demo
You can access the online version of this dashboard here:  
🔗 **[TikTok Refugees Data Dashboard](https://zoeyfeng0110-tiktok-refugee-related-data-visua-dashboard-cbi2me.streamlit.app/)**  
After opening the link in your browser, you can use the `examplecsv` file from this repository to display data.

## Data Management 
- The dataset consists of all posts retrieved from Rednote using the keyword **"TikTok refugee"** between **January 2, 2025, and February 19, 2025**.
  
- The categorization of posts was performed using a locally deployed **Llama 3.2-8B** model.

## Data Requirements
The uploaded CSV file should contain the following columns:
- `time`: Timestamp in milliseconds
- `title`: Post title
- `desc`: Post description
- `category`: Post category (mapped to readable names)
- `ip_location`: Geographic location (province-level data)

## Data Coverage
- **Time Range**: The dataset covers posts from **January 2, 2025, to February 19, 2025**.
- **Total Posts**: The total number of posts available in the dataset will be displayed in the dashboard after uploading the file.

## Usage Guide
1. Upload your CSV file via the sidebar.
2. Navigate between tabs:
   - **Topic Trend Analysis**: View post trends categorized by topic.
   - **Geographic Distribution**: Explore post distribution across regions.
3. Customize visualizations by selecting specific categories or dates.

## Dependencies
- Streamlit
- Pandas
- NumPy
- Folium
- Plotly
- Requests

## License
This project is open-source under the MIT License.

