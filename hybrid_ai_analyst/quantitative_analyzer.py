import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
import asyncio
import os
from datetime import datetime

class QuantitativeAnalyzer:
    """
    Quantitative analysis pipeline for processing structured financial data.
    Calculates key metrics like Month-over-Month growth, total revenue,
    and other financial indicators to assess startup performance.
    """
    
    def __init__(self):
        """Initialize the quantitative analyzer"""
        pass
    
    async def analyze_financial_data(self, csv_path: str) -> str:
        """
        Analyze financial data from CSV file and generate quantitative summary.
        
        Args:
            csv_path: Path to the CSV file containing financial data
            
        Returns:
            Quantitative summary of financial performance
        """
        try:
            # Read and validate CSV data
            df = await self._load_and_validate_data(csv_path)
            
            # Calculate key metrics
            metrics = await self._calculate_metrics(df)
            
            # Generate quantitative summary
            summary = await self._generate_quantitative_summary(metrics)
            
            return summary
            
        except Exception as e:
            raise Exception(f"Quantitative analysis failed: {str(e)}")
    
    async def _load_and_validate_data(self, csv_path: str) -> pd.DataFrame:
        """
        Load and validate CSV data.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Validated pandas DataFrame
        """
        try:
            df = pd.read_csv(csv_path)
            
            # Basic validation
            if df.empty:
                raise ValueError("CSV file is empty")
            
            # Checking for required columns (assuming standard format)
            required_columns = ['month', 'revenue']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                # Trying to infer column names
                if len(df.columns) >= 2:
                    
                    df.columns = ['month', 'revenue'] + list(df.columns[2:])
                else:
                    raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Converting month column to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(df['month']):
                df['month'] = pd.to_datetime(df['month'], errors='coerce')
            
            # Sorting by month
            df = df.sort_values('month').reset_index(drop=True)
            
            # Removing any rows with missing data
            df = df.dropna(subset=['month', 'revenue'])
            
            if df.empty:
                raise ValueError("No valid data after cleaning")
            
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to load CSV data: {str(e)}")
    
    async def _calculate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate key financial metrics.
        
        Args:
            df: DataFrame with financial data
            
        Returns:
            Dictionary containing calculated metrics
        """
        metrics = {}
        
        # Basic metrics
        metrics['total_revenue'] = df['revenue'].sum()
        metrics['avg_monthly_revenue'] = df['revenue'].mean()
        metrics['revenue_volatility'] = df['revenue'].std()
        metrics['num_months'] = len(df)
        
        # Month-over-Month growth rates
        if len(df) > 1:
            df['revenue_growth'] = df['revenue'].pct_change()
            metrics['mom_growth_rates'] = df['revenue_growth'].dropna().tolist()
            metrics['avg_mom_growth'] = df['revenue_growth'].mean()
            metrics['positive_growth_months'] = (df['revenue_growth'] > 0).sum()
            metrics['growth_consistency'] = metrics['positive_growth_months'] / (len(df) - 1)
        else:
            metrics['mom_growth_rates'] = []
            metrics['avg_mom_growth'] = 0
            metrics['positive_growth_months'] = 0
            metrics['growth_consistency'] = 0
        
        # Trend analysis
        if len(df) >= 3:
            # Linear trend
            x = np.arange(len(df))
            y = df['revenue'].values
            slope, intercept = np.polyfit(x, y, 1)
            metrics['trend_slope'] = slope
            metrics['trend_direction'] = 'increasing' if slope > 0 else 'decreasing'
            
            # Recent vs early performance
            mid_point = len(df) // 2
            early_avg = df['revenue'].iloc[:mid_point].mean()
            recent_avg = df['revenue'].iloc[mid_point:].mean()
            metrics['recent_vs_early_ratio'] = recent_avg / early_avg if early_avg > 0 else 0
        else:
            metrics['trend_slope'] = 0
            metrics['trend_direction'] = 'insufficient_data'
            metrics['recent_vs_early_ratio'] = 1
        
        return metrics
    
    async def _generate_quantitative_summary(self, metrics: Dict[str, Any]) -> str:
        """
        Generate a quantitative summary based on calculated metrics.
        
        Args:
            metrics: Dictionary of calculated financial metrics
            
        Returns:
            Quantitative summary string (one sentence as required by assignment)
        """
        # Revenue overview
        total_rev = metrics['total_revenue']
        
        # Growth analysis
        if metrics['num_months'] > 1:
            avg_growth = metrics['avg_mom_growth'] * 100
            consistency = metrics['growth_consistency'] * 100
            
            if avg_growth > 0:
                if consistency >= 80:
                    summary = f"The company shows strong MoM growth of {avg_growth:.1f}% with consistent revenue streams and total revenue of ${total_rev:,.0f} over {metrics['num_months']} months."
                else:
                    summary = f"The company shows strong MoM growth of {avg_growth:.1f}% but has inconsistent revenue streams with total revenue of ${total_rev:,.0f} over {metrics['num_months']} months."
            elif avg_growth > -5:
                summary = f"The company shows moderate decline of {abs(avg_growth):.1f}% with total revenue of ${total_rev:,.0f} over {metrics['num_months']} months."
            else:
                summary = f"The company shows significant decline of {abs(avg_growth):.1f}% with total revenue of ${total_rev:,.0f} over {metrics['num_months']} months."
        else:
            summary = f"The company has total revenue of ${total_rev:,.0f} over {metrics['num_months']} month(s) with insufficient data for growth analysis."
        
        return summary
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the quantitative analyzer"""
        return {
            "status": "operational",
            "data_processing": "pandas",
            "metrics_calculated": [
                "total_revenue",
                "month_over_month_growth",
                "revenue_volatility",
                "trend_analysis",
                "growth_consistency"
            ]
        } 