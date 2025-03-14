# TikTok Refugees Related Posts Data Dashboard

## Overview
This Streamlit-based dashboard provides interactive visualizations for analyzing RedNote posts related to "TikTok Refugees." It allows users to explore trends, category distributions, and geographic insights based on uploaded data.

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

## Data Requirements
The uploaded CSV file should contain the following columns:
- `time`: Timestamp in milliseconds
- `title`: Post title
- `desc`: Post Content
- `category`: Post category (mapped to readable names)
- `ip_location`: Geographic location of Chinese Province (province-level data)

## Data Coverage
- Time Range: The dataset covers posts from a specific time period, depending on the uploaded data. The example data is covered from 2025.1.2 to 2025.2.19
- Total Posts: The total number of posts available in the dataset will be displayed in the dashboard after uploading the file.

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

