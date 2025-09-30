#!/usr/bin/env python3
"""
Data Processor for Bloomberg Options Data
Handles data cleaning, validation, and transformation
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and validate Bloomberg options data"""
    
    def __init__(self):
        """Initialize data processor"""
        self.required_fields = [
            'ticker', 'strike', 'option_type', 'expiry',
            'PX_BID', 'PX_ASK', 'PX_LAST'
        ]

        # Bloomberg field mappings
        self.bloomberg_field_mappings = {
            'PX_BID': 'bid',
            'PX_ASK': 'ask',
            'PX_LAST': 'last',
            'PX_VOLUME': 'volume',
            'VOLUME': 'volume',  # Handle both variants
            'OPEN_INT': 'open_interest',
            'IVOL_MID': 'implied_vol',
            'DELTA': 'delta',
            'GAMMA': 'gamma',
            'THETA': 'theta',
            'VEGA': 'vega',
            'RHO': 'rho',
            'OPT_UNDL_PX': 'underlying_price',
            'BID_SIZE': 'bid_size',
            'ASK_SIZE': 'ask_size',
            'PX_SETTLE': 'settle_price',
            'CHG_NET_1D': 'change_1d',
            'CHG_PCT_1D': 'change_pct_1d',
            'VOLATILITY_30D': 'volatility_30d',
            'PX_HIGH': 'high',
            'PX_LOW': 'low',
            'TIME_LAST_UPD': 'last_update_time',
            'IVOL_BID': 'implied_vol_bid',
            'IVOL_ASK': 'implied_vol_ask',
            'MONEYNESS': 'moneyness',
            'TIME_TO_EXPIRY': 'time_to_expiry'
        }

    def transform_bloomberg_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform Bloomberg historical data format to standardized format

        Args:
            df: DataFrame with Bloomberg column names (e.g., 'QQQ US 10/03/25 C490 Equity_PX_BID')

        Returns:
            DataFrame with standardized columns
        """
        if df.empty:
            return df

        # Extract ticker information and data from column names
        transformed_data = []

        # Group columns by ticker (everything before the last underscore)
        ticker_groups = {}
        for col in df.columns:
            if '_' in col:
                ticker_part = col.rsplit('_', 1)[0]  # Get everything before last underscore
                field_part = col.rsplit('_', 1)[1]   # Get field name after last underscore

                if ticker_part not in ticker_groups:
                    ticker_groups[ticker_part] = {}

                ticker_groups[ticker_part][field_part] = col

        # Process each ticker group
        for ticker_key, fields in ticker_groups.items():
            # Parse ticker information
            ticker_info = self._parse_bloomberg_ticker(ticker_key)

            if not ticker_info:
                continue

            # Get all dates that have data for this ticker
            dates_with_data = set()
            for field_name, col_name in fields.items():
                if col_name in df.columns:
                    dates_with_data.update(df[col_name].dropna().index)

            # Create records for each date
            for date in dates_with_data:
                record = ticker_info.copy()
                # Ensure proper date formatting
                try:
                    if isinstance(date, str):
                        # If it's already a string, try to parse it
                        parsed_date = pd.to_datetime(date)
                        record['fetch_date'] = parsed_date.strftime('%Y-%m-%d')
                    elif hasattr(date, 'strftime'):
                        # If it's a datetime object
                        record['fetch_date'] = date.strftime('%Y-%m-%d')
                    else:
                        # If it's something else (like int index), convert to datetime
                        parsed_date = pd.to_datetime(date)
                        record['fetch_date'] = parsed_date.strftime('%Y-%m-%d')
                except Exception:
                    # Fallback: use current date with offset
                    from datetime import datetime, timedelta
                    fallback_date = datetime.now() - timedelta(days=int(str(date)) if str(date).isdigit() else 0)
                    record['fetch_date'] = fallback_date.strftime('%Y-%m-%d')

                # Add field data
                for field_name, col_name in fields.items():
                    if col_name in df.columns and date in df.index:
                        value = df.loc[date, col_name]
                        if pd.notna(value):
                            # Map Bloomberg field to standard field
                            standard_field = self.bloomberg_field_mappings.get(field_name, field_name.lower())
                            record[standard_field] = value

                transformed_data.append(record)

        if not transformed_data:
            logger.warning("No data could be transformed")
            return pd.DataFrame()

        result_df = pd.DataFrame(transformed_data)
        logger.info(f"Transformed {len(result_df)} records from Bloomberg format")

        return result_df

    def _parse_bloomberg_ticker(self, ticker_key: str) -> Optional[Dict]:
        """
        Parse Bloomberg ticker to extract option information

        Example: 'QQQ US 10/03/25 C490 Equity' -> {
            'underlying': 'QQQ',
            'expiry': '20251003',
            'option_type': 'C',
            'strike': 490.0,
            'ticker': 'QQQ US 10/03/25 C490 Equity'
        }
        """
        try:
            parts = ticker_key.split()
            if len(parts) < 4:
                return None

            underlying = parts[0]  # QQQ
            country = parts[1]     # US
            date_part = parts[2]   # 10/03/25
            option_part = parts[3] # C490

            # Parse date (MM/DD/YY format)
            month, day, year = date_part.split('/')
            year = f"20{year}"  # Convert 25 -> 2025
            expiry = f"{year}{month.zfill(2)}{day.zfill(2)}"

            # Parse option type and strike
            option_type = option_part[0]  # C or P
            strike = float(option_part[1:])  # 490

            return {
                'ticker': ticker_key,
                'underlying': underlying,
                'expiry': expiry,
                'option_type': option_type,
                'strike': strike
            }

        except Exception as e:
            logger.warning(f"Could not parse ticker '{ticker_key}': {e}")
            return None

    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and clean options data
        
        Args:
            df: Raw DataFrame from Bloomberg
            
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            logger.warning("Empty DataFrame received")
            return df
        
        # Determine if this is transformed data or Bloomberg format
        is_transformed = 'underlying' in df.columns and 'strike' in df.columns

        if is_transformed:
            # Check transformed format required fields
            transformed_required = ['ticker', 'underlying', 'expiry', 'strike', 'option_type']
            missing_fields = [f for f in transformed_required if f not in df.columns]
            if missing_fields:
                logger.warning(f"Missing transformed fields: {missing_fields}")
        else:
            # Check Bloomberg format required fields
            missing_fields = [f for f in self.required_fields if f not in df.columns]
            if missing_fields:
                logger.warning(f"Missing Bloomberg fields: {missing_fields}")
        
        # Clean data
        df = self._clean_prices(df)
        df = self._calculate_derived_fields(df)
        df = self._remove_invalid_records(df)
        
        logger.info(f"Validated {len(df)} records")
        return df
    
    def _clean_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean price fields"""
        # Bloomberg format fields
        bloomberg_price_fields = ['PX_BID', 'PX_ASK', 'PX_LAST', 'PX_HIGH', 'PX_LOW',
                                'PX_SETTLE', 'IVOL_MID', 'IVOL_BID', 'IVOL_ASK',
                                'DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO',
                                'CHG_NET_1D', 'CHG_PCT_1D', 'VOLATILITY_30D',
                                'VOLUME', 'OPEN_INT', 'BID_SIZE', 'ASK_SIZE',
                                'OPT_UNDL_PX', 'MONEYNESS', 'TIME_TO_EXPIRY']

        # Transformed format fields
        transformed_price_fields = ['bid', 'ask', 'last', 'high', 'low', 'settle_price',
                                  'implied_vol', 'implied_vol_bid', 'implied_vol_ask',
                                  'delta', 'gamma', 'theta', 'vega', 'rho',
                                  'volume', 'open_interest', 'bid_size', 'ask_size',
                                  'underlying_price', 'change_1d', 'change_pct_1d',
                                  'volatility_30d', 'moneyness', 'time_to_expiry']

        # Combine all possible price fields
        all_price_fields = bloomberg_price_fields + transformed_price_fields

        for field in all_price_fields:
            if field in df.columns:
                # Convert to numeric, handle errors
                df[field] = pd.to_numeric(df[field], errors='coerce')

                # Handle negative prices for bid/ask/last fields
                negative_check_fields = ['PX_BID', 'PX_ASK', 'PX_LAST', 'bid', 'ask', 'last']
                if field in negative_check_fields:
                    df.loc[df[field] < 0, field] = np.nan
        
        return df
    
    def _calculate_derived_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived fields"""
        # Calculate spread - handle both Bloomberg and transformed formats
        if 'PX_BID' in df.columns and 'PX_ASK' in df.columns:
            df['spread'] = df['PX_ASK'] - df['PX_BID']
            df['spread_pct'] = (df['spread'] / df['PX_ASK']) * 100
        elif 'bid' in df.columns and 'ask' in df.columns:
            df['spread'] = df['ask'] - df['bid']
            df['spread_pct'] = (df['spread'] / df['ask']) * 100
        
        # Calculate moneyness
        if 'strike' in df.columns and 'spot_price' in df.columns:
            df['moneyness'] = df['spot_price'] / df['strike']
            
            # Classify moneyness
            df['moneyness_class'] = pd.cut(
                df['moneyness'],
                bins=[0, 0.95, 1.05, np.inf],
                labels=['OTM', 'ATM', 'ITM']
            )
        
        # Calculate time to expiry
        if 'expiry' in df.columns:
            df['expiry_date'] = pd.to_datetime(df['expiry'], format='%Y%m%d')
            df['days_to_expiry'] = (df['expiry_date'] - datetime.now()).dt.days
            df['years_to_expiry'] = df['days_to_expiry'] / 365.25
        
        return df
    
    def _remove_invalid_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove invalid records with comprehensive validation"""
        initial_count = len(df)
        validation_log = []

        # Remove records with invalid bid/ask spreads (both formats)
        if 'PX_BID' in df.columns and 'PX_ASK' in df.columns:
            invalid_spreads = df['PX_BID'] > df['PX_ASK']
            removed = invalid_spreads.sum()
            if removed > 0:
                validation_log.append(f"Removed {removed} records with invalid bid > ask (Bloomberg format)")
            df = df[~invalid_spreads]
        elif 'bid' in df.columns and 'ask' in df.columns:
            invalid_spreads = df['bid'] > df['ask']
            removed = invalid_spreads.sum()
            if removed > 0:
                validation_log.append(f"Removed {removed} records with invalid bid > ask (transformed format)")
            df = df[~invalid_spreads]

        # Remove expired options
        if 'days_to_expiry' in df.columns:
            expired = df['days_to_expiry'] <= 0
            removed = expired.sum()
            if removed > 0:
                validation_log.append(f"Removed {removed} expired options")
            df = df[~expired]

        # Remove options with extreme spreads
        if 'spread_pct' in df.columns:
            extreme_spreads = df['spread_pct'] > 50
            removed = extreme_spreads.sum()
            if removed > 0:
                validation_log.append(f"Removed {removed} options with spreads > 50%")
            df = df[~extreme_spreads]

        # Remove options with invalid implied volatility
        iv_fields = ['IVOL_MID', 'implied_vol', 'implied_vol_bid', 'implied_vol_ask']
        for iv_field in iv_fields:
            if iv_field in df.columns:
                invalid_iv = (df[iv_field] < 0) | (df[iv_field] > 5)  # IV should be between 0 and 500%
                removed = invalid_iv.sum()
                if removed > 0:
                    validation_log.append(f"Removed {removed} records with invalid {iv_field}")
                df = df[~invalid_iv]

        # Remove options with zero volume and zero open interest
        volume_fields = ['VOLUME', 'volume']
        oi_fields = ['OPEN_INT', 'open_interest']

        for vol_field in volume_fields:
            if vol_field in df.columns:
                for oi_field in oi_fields:
                    if oi_field in df.columns:
                        no_activity = (df[vol_field] == 0) & (df[oi_field] == 0)
                        removed = no_activity.sum()
                        if removed > 0:
                            validation_log.append(f"Removed {removed} options with no volume and no open interest")
                        df = df[~no_activity]
                        break
                break

        # Log validation results
        total_removed = initial_count - len(df)
        if total_removed > 0:
            logger.info(f"Data validation removed {total_removed} invalid records:")
            for log_entry in validation_log:
                logger.info(f"  - {log_entry}")

        return df
    
    def aggregate_by_strike(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate data by strike for summary view
        
        Args:
            df: Options DataFrame
            
        Returns:
            Aggregated DataFrame
        """
        if df.empty:
            return df
        
        agg_dict = {
            'PX_LAST': 'mean',
            'VOLUME': 'sum',
            'OPEN_INT': 'sum',
            'IVOL_MID': 'mean',
            'spread': 'mean'
        }
        
        # Filter columns that exist
        agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
        
        grouped = df.groupby(['expiry', 'strike', 'option_type']).agg(agg_dict)
        grouped = grouped.reset_index()
        
        return grouped
    
    def create_summary_report(self, df: pd.DataFrame) -> Dict:
        """
        Create summary statistics report
        
        Args:
            df: Options DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_records': len(df),
            'unique_strikes': df['strike'].nunique() if 'strike' in df.columns else 0,
            'unique_expiries': df['expiry'].nunique() if 'expiry' in df.columns else 0
        }
        
        # Price statistics
        if 'PX_LAST' in df.columns:
            summary['avg_price'] = df['PX_LAST'].mean()
            summary['min_price'] = df['PX_LAST'].min()
            summary['max_price'] = df['PX_LAST'].max()
        
        # Volume statistics
        if 'VOLUME' in df.columns:
            summary['total_volume'] = df['VOLUME'].sum()
            summary['avg_volume'] = df['VOLUME'].mean()
        
        # IV statistics
        if 'IVOL_MID' in df.columns:
            summary['avg_iv'] = df['IVOL_MID'].mean()
            summary['min_iv'] = df['IVOL_MID'].min()
            summary['max_iv'] = df['IVOL_MID'].max()
        
        # Spread statistics
        if 'spread' in df.columns:
            summary['avg_spread'] = df['spread'].mean()
            summary['avg_spread_pct'] = df['spread_pct'].mean() if 'spread_pct' in df.columns else None
        
        return summary
    
    def filter_liquid_options(self, 
                            df: pd.DataFrame, 
                            min_volume: int = 100,
                            max_spread_pct: float = 10.0) -> pd.DataFrame:
        """
        Filter for liquid options only
        
        Args:
            df: Options DataFrame
            min_volume: Minimum volume threshold
            max_spread_pct: Maximum spread percentage
            
        Returns:
            Filtered DataFrame
        """
        filtered = df.copy()
        
        # Filter by volume
        if 'VOLUME' in filtered.columns:
            filtered = filtered[filtered['VOLUME'] >= min_volume]
        
        # Filter by spread
        if 'spread_pct' in filtered.columns:
            filtered = filtered[filtered['spread_pct'] <= max_spread_pct]
        
        logger.info(f"Filtered to {len(filtered)} liquid options from {len(df)} total")
        return filtered
    
    def export_for_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data for analysis with clean column names
        
        Args:
            df: Options DataFrame
            
        Returns:
            DataFrame with clean column names
        """
        # Rename columns for clarity
        column_mapping = {
            'PX_BID': 'bid',
            'PX_ASK': 'ask',
            'PX_LAST': 'last',
            'VOLUME': 'volume',
            'OPEN_INT': 'open_interest',
            'IVOL_MID': 'implied_vol',
            'DELTA': 'delta',
            'GAMMA': 'gamma',
            'THETA': 'theta',
            'VEGA': 'vega',
            'RHO': 'rho',
            'OPT_UNDL_PX': 'underlying_price',
            'BID_SIZE': 'bid_size',
            'ASK_SIZE': 'ask_size'
        }
        
        df_clean = df.rename(columns=column_mapping)
        
        # Select and order columns
        columns_order = [
            'ticker', 'underlying', 'expiry', 'strike', 'option_type',
            'bid', 'ask', 'last', 'volume', 'open_interest',
            'implied_vol', 'delta', 'gamma', 'theta', 'vega',
            'spread', 'spread_pct', 'moneyness', 'days_to_expiry'
        ]
        
        # Keep only columns that exist
        columns_to_keep = [col for col in columns_order if col in df_clean.columns]
        df_clean = df_clean[columns_to_keep]
        
        return df_clean

    def create_data_quality_report(self, df: pd.DataFrame) -> Dict:
        """
        Create comprehensive data quality report

        Args:
            df: Options DataFrame

        Returns:
            Dictionary with data quality metrics
        """
        report = {
            'summary': {
                'total_records': len(df),
                'data_completeness': {},
                'quality_scores': {}
            },
            'field_analysis': {},
            'data_issues': [],
            'recommendations': []
        }

        if df.empty:
            report['data_issues'].append("No data available")
            return report

        # Analyze data completeness
        total_records = len(df)
        for column in df.columns:
            non_null_count = df[column].notna().sum()
            completeness_pct = (non_null_count / total_records) * 100
            report['summary']['data_completeness'][column] = {
                'non_null_count': int(non_null_count),
                'completeness_percentage': round(completeness_pct, 2),
                'missing_count': int(total_records - non_null_count)
            }

            # Flag fields with low completeness
            if completeness_pct < 80:
                report['data_issues'].append(
                    f"Low data completeness for {column}: {completeness_pct:.1f}%"
                )

        # Analyze price fields
        price_fields = ['bid', 'ask', 'last', 'PX_BID', 'PX_ASK', 'PX_LAST']
        for field in price_fields:
            if field in df.columns:
                field_data = df[field].dropna()
                if len(field_data) > 0:
                    report['field_analysis'][field] = {
                        'min': float(field_data.min()),
                        'max': float(field_data.max()),
                        'mean': float(field_data.mean()),
                        'std': float(field_data.std()) if len(field_data) > 1 else 0,
                        'zero_values': int((field_data == 0).sum()),
                        'negative_values': int((field_data < 0).sum())
                    }

                    # Flag unusual values
                    if (field_data < 0).any():
                        report['data_issues'].append(f"Negative values found in {field}")
                    if (field_data == 0).sum() > total_records * 0.5:
                        report['data_issues'].append(f"High number of zero values in {field}")

        # Analyze spreads
        if 'spread_pct' in df.columns:
            spreads = df['spread_pct'].dropna()
            if len(spreads) > 0:
                wide_spreads = (spreads > 20).sum()
                if wide_spreads > 0:
                    report['data_issues'].append(
                        f"{wide_spreads} options have spreads > 20%"
                    )

        # Analyze time series consistency
        if 'fetch_date' in df.columns:
            unique_dates = df['fetch_date'].nunique()
            date_coverage = df.groupby('fetch_date').size()
            report['field_analysis']['date_coverage'] = {
                'unique_dates': int(unique_dates),
                'records_per_date': date_coverage.to_dict(),
                'avg_records_per_date': float(date_coverage.mean()),
                'date_gaps': []
            }

            # Check for date gaps (if dates are properly formatted)
            try:
                dates = pd.to_datetime(df['fetch_date'].unique())
                dates = sorted(dates)
                for i in range(1, len(dates)):
                    gap = (dates[i] - dates[i-1]).days
                    if gap > 1:  # More than 1 day gap
                        report['field_analysis']['date_coverage']['date_gaps'].append({
                            'from': dates[i-1].strftime('%Y-%m-%d'),
                            'to': dates[i].strftime('%Y-%m-%d'),
                            'gap_days': gap
                        })
            except:
                report['data_issues'].append("Date formatting issues prevent gap analysis")

        # Calculate overall quality score
        completeness_scores = [v['completeness_percentage'] for v in
                             report['summary']['data_completeness'].values()]
        avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0

        quality_deductions = len(report['data_issues']) * 5  # 5 points per issue
        overall_score = max(0, avg_completeness - quality_deductions)

        report['summary']['quality_scores'] = {
            'overall_score': round(overall_score, 2),
            'data_completeness_score': round(avg_completeness, 2),
            'issues_count': len(report['data_issues']),
            'quality_grade': self._get_quality_grade(overall_score)
        }

        # Generate recommendations
        if overall_score < 70:
            report['recommendations'].append("Data quality is below acceptable threshold")
        if len(report['data_issues']) > 0:
            report['recommendations'].append("Address identified data issues before analysis")
        if avg_completeness < 90:
            report['recommendations'].append("Improve data collection to reduce missing values")

        return report

    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


if __name__ == "__main__":
    # Test data processor
    processor = DataProcessor()
    
    # Create sample data
    sample_data = pd.DataFrame({
        'ticker': ['QQQ US 12/20/24 C500 Equity'] * 3,
        'strike': [500, 500, 500],
        'option_type': ['C', 'C', 'C'],
        'expiry': ['20241220', '20241220', '20241220'],
        'PX_BID': [10.5, 10.6, 10.4],
        'PX_ASK': [10.7, 10.8, 10.6],
        'PX_LAST': [10.6, 10.7, 10.5],
        'VOLUME': [1000, 1500, 800],
        'spot_price': [495, 495, 495]
    })
    
    # Process data
    processed = processor.validate_data(sample_data)
    print("Processed data:")
    print(processed)
    
    # Create summary
    summary = processor.create_summary_report(processed)
    print("\nSummary:")
    for key, value in summary.items():
        print(f"{key}: {value}")