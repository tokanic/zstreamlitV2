import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import requests
from datetime import datetime, timedelta
import pytz

# Enhanced Streamlit Configuration
st.set_page_config(
    page_title="Advanced Binance Trading Dashboard", 
    page_icon=":chart_with_upwards_trend:", 
    layout="wide"
)

# Configuration and Constants
API_SERVER = "http://34.47.211.154:5001"  # Replace with your actual server URL
INDIAN_TZ = pytz.timezone('Asia/Kolkata')

# Advanced Helper Functions
def safe_fetch_data(endpoint):
    """Enhanced error handling and logging for API requests"""
    try:
        response = requests.get(f"{API_SERVER}/{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Request Error for {endpoint}: {e}")
        return None

def format_timestamp(timestamp, format_type='full'):
    """Flexible timestamp formatting with multiple options"""
    if not timestamp:
        return "N/A"
    
    try:
        # Convert to datetime
        dt = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        dt_indian = dt.astimezone(INDIAN_TZ)
        
        if format_type == 'full':
            return dt_indian.strftime('%d %b %Y, %I:%M:%S %p')
        elif format_type == 'date':
            return dt_indian.strftime('%d %b %Y')
        elif format_type == 'time':
            return dt_indian.strftime('%I:%M %p')
    except Exception as e:
        st.warning(f"Timestamp formatting error: {e}")
        return "Invalid Time"

def format_currency(value, currency='USDT', precision=2):
    """Advanced currency formatting with color coding"""
    try:
        value = float(value)
        formatted = f"{value:.{precision}f} {currency}"
        
        if value > 0:
            return f"<span style='color:green'>+{formatted}</span>"
        elif value < 0:
            return f"<span style='color:red'>{formatted}</span>"
        else:
            return f"<span style='color:gray'>{formatted}</span>"
    except:
        return f"N/A {currency}"

# Sidebar and Navigation
def create_sidebar():
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/4b/Binance_logo.png", width=200)
    st.sidebar.title("Binance Pro Dashboard")
    
    menu_options = [
        "🏦 Account Overview", 
        "📊 Positions", 
        "📝 Orders", 
        "📈 Trade Analytics", 
        "💹 Performance Metrics"
    ]
    
    return st.sidebar.radio("Navigation", menu_options)

# Dashboard Sections
def account_overview():
    """Comprehensive Account Overview Section"""
    st.header("Account Overview")
    account_data = safe_fetch_data("account_summary")
    
    if not account_data:
        st.warning("Unable to fetch account data")
        return
    
    # Create columns for key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Balance", 
            value=format_currency(account_data.get('Balance', 0)),
            help="Total account balance across all assets"
        )
    
    with col2:
        st.metric(
            label="Unrealized PNL", 
            value=format_currency(account_data.get('Unrealized PNL', 0)),
            help="Profit/Loss from current open positions"
        )
    
    with col3:
        st.metric(
            label="Available Margin", 
            value=format_currency(account_data.get('Margin Balance', 0)),
            help="Margin balance available for trading"
        )
    
    with col4:
        st.metric(
            label="Free Balance", 
            value=format_currency(account_data.get('Available Balance', 0)),
            help="Balance available for new trades"
        )

def positions_analysis():
    """Advanced Positions Analysis"""
    st.header("Active Positions Dashboard")
    positions_data = safe_fetch_data("positions")
    
    if not positions_data:
        st.warning("No active positions found")
        return
    
    df = pd.DataFrame(positions_data)
    
    # Enhanced DataFrame Display
    st.dataframe(
        df.style.format({
            'Entry Time': format_timestamp,
            'Current PNL': lambda x: format_currency(x)
        }),
        use_container_width=True
    )
    
    # Position Distribution Chart
    if not df.empty:
        fig = px.pie(
            df, 
            names='Symbol', 
            values='Amount', 
            title='Position Size Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)

def trade_analytics():
    """Comprehensive Trade Analytics"""
    st.header("Advanced Trade Analytics")
    
    # Fetch and process trade data
    trade_data = safe_fetch_data("trade_analytics")
    
    if not trade_data:
        st.warning("Trade analytics unavailable")
        return
    
    df = pd.DataFrame(trade_data)
    
    # Performance Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Trades", len(df))
    
    with col2:
        win_rate = (df['PNL'] > 0).mean() * 100
        st.metric("Win Rate", f"{win_rate:.2f}%")
    
    with col3:
        total_pnl = df['PNL'].sum()
        st.metric("Total PNL", format_currency(total_pnl))
    
    # Advanced Charts
    fig1 = px.bar(df, x='Symbol', y='PNL', title='PNL by Trading Pair')
    fig2 = px.line(df, x='Timestamp', y='PNL', title='PNL Over Time')
    
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

def main():
    """Main Dashboard Orchestrator"""
    selected_menu = create_sidebar()
    
    # Routing based on menu selection
    if selected_menu == "🏦 Account Overview":
        account_overview()
    elif selected_menu == "📊 Positions":
        positions_analysis()
    elif selected_menu == "📈 Trade Analytics":
        trade_analytics()
    
    # Add footer
    st.markdown("---")
    st.markdown("© 2025 Advanced Binance Trading Dashboard")

# Entry Point
if __name__ == "__main__":
    main()
