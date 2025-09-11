# Changelog

All notable changes to Bloomberg QQQ Options Fetcher will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2025-09-10

### 🚀 Major Enhancements
- **BREAKING**: Expanded strike range from ATM ±20 to ATM ±40 (80 strikes total)
- **NEW**: QQQ weekly expiry support (previously only monthly)
- **NEW**: Smart export format selection (CSV for testing ≤5 stocks, Parquet for production)
- **NEW**: Comprehensive documentation suite with 8 specialized guides

### ✨ New Features
- Added Parquet export for efficient large dataset handling (10x faster loading)
- Enhanced web interface with format selection dropdown
- Real-time progress monitoring with detailed statistics
- Resume capability for interrupted fetches with state management
- Automated Bloomberg API installation and setup
- Professional-grade documentation for all user types

### 📊 Data Improvements
- Increased data volume from ~24K to ~97K options records (4x improvement)
- Enhanced QQQ options with all weekly expiries within 60 days
- Added quarterly expiries for better liquidity coverage
- Improved strike range calculation for better ATM coverage

### 🔧 Technical Enhancements
- Added `export_to_parquet()` method in DatabaseManager
- Implemented smart format selection in robust_fetch.py
- Enhanced error recovery and retry mechanisms
- Improved API usage monitoring and throttling
- Added comprehensive data validation and verification

### 📚 Documentation
- Professional README.md with badges and comprehensive specs
- Quick start guide for 2-minute setup
- AI assistant reference guide
- Contributing guidelines and development setup
- Bloomberg API installation and troubleshooting guides

### 🐛 Bug Fixes
- Fixed expiry date calculation for weekly options
- Improved Bloomberg connection error handling
- Fixed database schema for large datasets
- Corrected CSV export encoding issues

## [1.0.0] - 2025-09-09

### 🎯 Initial Release
- Core Bloomberg QQQ options fetching functionality
- SQLite database storage with comprehensive schema
- Web interface with Streamlit dashboard
- Command-line interface for automated fetching
- Top 20 QQQ constituents support
- Basic Greeks and Open Interest data collection

### 📦 Features
- QQQ index options fetching (ATM ±20 strikes)
- Top 20 constituent stock options
- Comprehensive Greeks calculation (Delta, Gamma, Theta, Vega, Rho)
- Open Interest data for liquidity analysis
- CSV export functionality
- Real-time progress monitoring
- API usage tracking and limits management

### 🏗️ Architecture
- Modular design with separate fetchers for QQQ and constituents
- State management for resume capability
- Configurable strike ranges and expiry periods
- Robust error handling and recovery
- Bloomberg Terminal API integration

### ⚙️ Configuration
- YAML-based configuration system
- Support for custom constituent lists
- Configurable API limits and throttling
- Flexible output formats and paths

---

## Development Notes

### Version Numbering
- **Major.Minor.Patch** format
- Major: Breaking changes or significant feature additions
- Minor: New features, backward compatible
- Patch: Bug fixes and minor improvements

### Release Process
1. Update version in setup.py and __init__.py
2. Update this CHANGELOG.md
3. Create git tag: `git tag -a v2.0.0 -m "Release v2.0.0"`
4. Push tag: `git push origin v2.0.0`
5. Create GitHub release with release notes

### Future Roadmap
- [ ] Support for additional ETFs (SPY, QQQ, IWM)
- [ ] Real-time streaming data capability  
- [ ] Advanced filtering and screening options
- [ ] Integration with popular analysis frameworks
- [ ] Cloud deployment options (AWS, GCP, Azure)
- [ ] Enhanced visualization dashboard
- [ ] Machine learning integration for pattern recognition
- [ ] Multi-threading for faster data fetching

---

*For detailed technical specifications, see [CURSOR_AI_INSTRUCTIONS.md](CURSOR_AI_INSTRUCTIONS.md)*