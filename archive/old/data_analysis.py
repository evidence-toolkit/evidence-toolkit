#!/usr/bin/env python3
"""
Simple Data Analysis Script
Demonstrates basic pandas and matplotlib functionality
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_sample_data():
    """Create sample data for analysis"""
    np.random.seed(42)  # For reproducible results

    # Generate sample sales data
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    products = ['Product A', 'Product B', 'Product C', 'Product D']

    data = []
    for date in dates:
        for product in products:
            sales = np.random.normal(100, 20)  # Normal distribution around 100
            price = np.random.uniform(10, 50)  # Random price between 10-50
            data.append({
                'date': date,
                'product': product,
                'sales': max(0, sales),  # Ensure non-negative sales
                'price': price,
                'revenue': max(0, sales) * price
            })

    return pd.DataFrame(data)

def analyze_data(df):
    """Perform basic data analysis"""
    print("=== DATA ANALYSIS SUMMARY ===")
    print(f"Dataset shape: {df.shape}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print()

    # Basic statistics
    print("=== SALES STATISTICS ===")
    print(df['sales'].describe())
    print()

    # Product performance
    print("=== PRODUCT PERFORMANCE ===")
    product_summary = df.groupby('product').agg({
        'sales': ['sum', 'mean'],
        'revenue': ['sum', 'mean']
    }).round(2)
    print(product_summary)
    print()

    return product_summary

def create_visualizations(df):
    """Create visualizations of the data"""
    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Sales Data Analysis Dashboard', fontsize=16, fontweight='bold')

    # 1. Sales over time (line plot)
    daily_sales = df.groupby('date')['sales'].sum()
    axes[0, 0].plot(daily_sales.index, daily_sales.values, linewidth=2)
    axes[0, 0].set_title('Total Daily Sales Over Time')
    axes[0, 0].set_xlabel('Date')
    axes[0, 0].set_ylabel('Sales')
    axes[0, 0].grid(True, alpha=0.3)

    # 2. Sales by product (bar chart)
    product_sales = df.groupby('product')['sales'].sum()
    bars = axes[0, 1].bar(product_sales.index, product_sales.values)
    axes[0, 1].set_title('Total Sales by Product')
    axes[0, 1].set_xlabel('Product')
    axes[0, 1].set_ylabel('Total Sales')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        axes[0, 1].text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}', ha='center', va='bottom')

    # 3. Revenue distribution (histogram)
    axes[1, 0].hist(df['revenue'], bins=30, alpha=0.7, edgecolor='black')
    axes[1, 0].set_title('Revenue Distribution')
    axes[1, 0].set_xlabel('Revenue')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].grid(True, alpha=0.3)

    # 4. Sales vs Price scatter plot
    colors = {'Product A': 'red', 'Product B': 'blue',
              'Product C': 'green', 'Product D': 'orange'}

    for product in df['product'].unique():
        product_data = df[df['product'] == product]
        axes[1, 1].scatter(product_data['price'], product_data['sales'],
                          label=product, color=colors[product], alpha=0.6)

    axes[1, 1].set_title('Sales vs Price by Product')
    axes[1, 1].set_xlabel('Price')
    axes[1, 1].set_ylabel('Sales')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('/home/bch/dev/tools/claude-stuff/sales_analysis_dashboard.png',
                dpi=300, bbox_inches='tight')
    print("Dashboard saved as 'sales_analysis_dashboard.png'")

    # Show the plot
    plt.show()

def main():
    """Main function to run the data analysis"""
    print("Starting Data Analysis Project")
    print("=" * 50)

    # Create sample data
    print("Creating sample data...")
    df = create_sample_data()
    print(f"Generated {len(df)} data points")
    print()

    # Perform analysis
    product_summary = analyze_data(df)

    # Create visualizations
    print("Creating visualizations...")
    create_visualizations(df)

    # Save data to CSV for future use
    csv_path = '/home/bch/dev/tools/claude-stuff/sales_data.csv'
    df.to_csv(csv_path, index=False)
    print(f"Data saved to '{csv_path}'")

    print()
    print("Analysis complete!")

if __name__ == "__main__":
    main()