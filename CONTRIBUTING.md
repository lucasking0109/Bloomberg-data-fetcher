# Contributing to Bloomberg QQQ Options Fetcher

Thank you for your interest in contributing! This project helps traders and analysts fetch comprehensive options data from Bloomberg Terminal.

## 🤝 How to Contribute

### **Reporting Issues**
- Search existing issues first
- Use the issue template
- Include error messages and logs
- Specify Bloomberg Terminal version and Python version

### **Suggesting Features**
- Check if the feature already exists
- Explain the use case clearly
- Consider backward compatibility

### **Submitting Code**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly (see Testing section)
5. Commit with clear messages
6. Push and create a Pull Request

## 🧪 Testing Guidelines

### **Before Submitting**
```bash
# Test basic functionality
python setup_and_run.py

# Test with small dataset
python scripts/robust_fetch.py --top-n 5 --dry-run

# Verify configuration
python -c "from src.bloomberg_api import test_connection; test_connection()"
```

### **Required Tests**
- Bloomberg connection works
- Data fetching completes without errors
- Export functions work (CSV and Parquet)
- Resume capability functions
- Configuration parsing works

## 📝 Code Standards

### **Python Style**
- Follow PEP 8
- Use type hints where possible
- Add docstrings to public functions
- Keep functions focused and small

### **Documentation**
- Update README.md for new features
- Add docstrings to new functions
- Update configuration examples if needed

## 🚨 Bloomberg API Guidelines

### **Important Considerations**
- **Never include actual Bloomberg API keys or credentials**
- Respect Bloomberg's Terms of Service
- Be mindful of API rate limits (50K daily)
- Test with small datasets first
- Document any Bloomberg API changes

### **What NOT to Commit**
- Real market data files
- Database files with actual trading data
- Log files with API responses
- Personal Bloomberg configuration

## 🔧 Development Setup

### **Local Development**
```bash
# Clone and setup
git clone https://github.com/lucasking0109/bloomberg-qqq-fetcher.git
cd bloomberg-qqq-fetcher

# Create virtual environment
python -m venv bloom_env
source bloom_env/bin/activate  # Linux/Mac
# or
bloom_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Test setup
python setup_and_run.py
```

### **Project Structure**
```
src/                    # Core functionality
├── bloomberg_api.py    # Bloomberg Terminal connection
├── qqq_options_fetcher.py  # QQQ options fetching
├── constituents_fetcher.py # Stock options fetching
├── database_manager.py     # Data storage and export
└── fetch_state_manager.py  # Resume capability

scripts/                # Command line tools
├── robust_fetch.py     # Main fetching script
├── check_progress.py   # Progress monitoring
└── setup_bloomberg.py  # Bloomberg API setup

config/                 # Configuration files
├── config.yaml         # Main configuration
└── qqq_constituents.yaml  # Stock list and settings
```

## 📊 Data Requirements

### **Critical Fields**
Always ensure these fields are included in options data:
- `OPEN_INT` - Open Interest (critical for liquidity analysis)
- All Greeks: `DELTA`, `GAMMA`, `THETA`, `VEGA`, `RHO`
- Pricing: `PX_BID`, `PX_ASK`, `PX_LAST`
- Volume and size data

### **Data Quality**
- Validate strike ranges (ATM ± 40)
- Ensure expiry dates include weekly options for QQQ
- Check for null values in critical fields
- Verify data export formats (CSV/Parquet)

## 🎯 Areas for Contribution

### **High Priority**
- Error handling improvements
- Additional export formats
- Performance optimizations
- Better logging and monitoring
- Enhanced Bloomberg API compatibility

### **Medium Priority**
- Additional data validation
- Configuration file enhancements
- Web interface improvements
- Documentation updates

### **Enhancement Ideas**
- Support for other ETFs
- Real-time data streaming
- Advanced filtering options
- Integration with analysis tools
- Cloud deployment options

## 📞 Getting Help

### **Questions?**
- Check existing [Issues](https://github.com/lucasking0109/bloomberg-qqq-fetcher/issues)
- Read the documentation in `/docs` folder
- Review [AI_ASSISTANT_GUIDE.md](AI_ASSISTANT_GUIDE.md) for common patterns

### **Bloomberg-Specific Help**
- Review [BLOOMBERG_SETUP.md](BLOOMBERG_SETUP.md)
- Check [BLOOMBERG_API_QUICK_REFERENCE.md](BLOOMBERG_API_QUICK_REFERENCE.md)
- Ensure you have proper Bloomberg Terminal access

## ⚖️ Legal Notes

### **Important**
- This tool connects to Bloomberg Terminal but contains no Bloomberg proprietary code
- Users must have valid Bloomberg subscriptions
- Respect Bloomberg's Terms of Service
- This is an educational/research tool

### **By Contributing**
- You agree your code will be licensed under MIT License
- You have the right to contribute the code
- Your contributions may be modified or incorporated

---

## 🙏 Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes for significant contributions
- Special thanks for major improvements

Thank you for helping make this tool better for the trading and research community! 📈