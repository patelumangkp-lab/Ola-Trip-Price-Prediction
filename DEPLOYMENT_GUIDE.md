# 🚀 Deployment Guide - India Cab Service

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

1. Copy `env_example.txt` to `.env`
2. Add your Gemini API key:

   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Run the Application

```bash
streamlit run main.py
```

### 4. Access the Application

- **User Interface**: <http://localhost:8501>
- **Admin Panel**: Select "Admin Panel" in sidebar (Password: `admin123`)

## 🏗️ Project Architecture

### Modular Structure

```
├── main.py                    # Application entry point
├── config.py                  # Configuration and constants
├── services/                  # Core business logic
│   ├── ai_service.py         # AI analysis with Gemini
│   ├── route_service.py      # Route calculation and pricing
│   └── booking_service.py    # Booking management
├── ui/                       # User interfaces
│   ├── user_interface.py     # Customer booking interface
│   └── admin_interface.py    # Admin dashboard
└── data/                     # Data storage (auto-created)
    ├── bookings.json         # Booking records
    └── admin_data.json       # Analytics data
```

### Key Features Implemented

#### ✅ User Interface

- **Smart Route Planning**: AI-powered route analysis
- **Vehicle Selection**: Bike, Car, Premium, 6-Seater options
- **Transparent Pricing**: Clear fare breakdown
- **Real-time Conditions**: Weather and traffic analysis
- **Booking Management**: Track and manage rides

#### ✅ Admin Panel

- **Dashboard Overview**: Key metrics and analytics
- **Route Management**: Performance analysis
- **Booking Management**: Monitor all bookings
- **Advanced Analytics**: Revenue and profit insights
- **Settings**: Configure vehicle types

#### ✅ AI Integration

- **Gemini API**: Real-time weather and traffic analysis
- **Smart Pricing**: Dynamic fare calculation
- **Route Optimization**: Multiple route suggestions

## 🔧 Configuration Options

### Vehicle Types

Modify `config.py` to adjust vehicle settings:

```python
VEHICLE_TYPES = {
    "bike": {
        "base_rate_per_km": 8,
        "base_fare": 20,
        "name": "Bike",
        "capacity": 1,
        "icon": "🏍️"
    },
    # ... other vehicles
}
```

### Pricing Multipliers

Adjust weather and traffic multipliers:

```python
WEATHER_MULTIPLIERS = {
    "clear": 1.0,
    "light_rain": 1.2,
    "heavy_rain": 1.5,
    # ... other conditions
}
```

## 📊 Business Logic

### Pricing Calculation

1. **Base Cost** = Base Fare + (Distance × Rate per km)
2. **Weather Adjustment** = Base Cost × Weather Multiplier
3. **Traffic Adjustment** = Weather Adjusted Cost × Traffic Multiplier
4. **Final Fare** = Traffic Adjusted Cost
5. **Driver Earnings** = Final Fare × 75%
6. **Company Profit** = Final Fare × 25%

### Route Suggestions

- **Route 1**: Main roads (with traffic) - longer distance, higher time
- **Route 2**: Local roads (less traffic) - shorter distance, lower time

## 🛡️ Security Considerations

### For Production

1. **Change Admin Password**: Update in `ui/admin_interface.py`
2. **Environment Variables**: Use secure environment variable management
3. **Input Validation**: Add proper input sanitization
4. **Database**: Upgrade from JSON to proper database
5. **Authentication**: Implement proper user authentication

### Current Demo Security

- Admin password: `admin123` (change for production)
- No user authentication (add for production)
- JSON file storage (upgrade to database)

## 🚀 Production Deployment

### Recommended Stack

- **Frontend**: Streamlit (current) or React/Vue.js
- **Backend**: FastAPI or Django
- **Database**: PostgreSQL or MongoDB
- **AI**: Google Gemini API (current)
- **Maps**: Google Maps API or OpenStreetMap
- **Hosting**: AWS, Google Cloud, or Azure

### Database Migration

Replace JSON files with database:

```python
# Example with SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(String, primary_key=True)
    origin = Column(String)
    destination = Column(String)
    # ... other fields
```

## 📈 Monitoring and Analytics

### Key Metrics to Track

- Total bookings per day/week/month
- Revenue and profit trends
- Popular routes and vehicle types
- Driver earnings distribution
- Customer satisfaction scores

### Admin Dashboard Features

- Real-time metrics
- Revenue analytics
- Route performance
- Booking management
- System settings

## 🔄 Future Enhancements

### Phase 2 Features

- [ ] Real-time GPS tracking
- [ ] Payment gateway integration
- [ ] Driver mobile app
- [ ] Push notifications
- [ ] Advanced route optimization

### Phase 3 Features

- [ ] Multi-language support
- [ ] API endpoints for mobile apps
- [ ] Machine learning for demand prediction
- [ ] Dynamic pricing algorithms
- [ ] Customer loyalty program

## 🆘 Troubleshooting

### Common Issues

1. **API Key Error**: Ensure GEMINI_API_KEY is set in .env
2. **Import Errors**: Run `pip install -r requirements.txt`
3. **Data Directory**: Ensure `data/` directory exists
4. **Port Conflicts**: Change Streamlit port with `--server.port 8502`

### Debug Mode

Run with debug information:

```bash
streamlit run main.py --logger.level debug
```

## 📞 Support

For technical support:

1. Check the README.md file
2. Review error logs
3. Test with `python test_app.py`
4. Create an issue in the repository

---

**Ready to revolutionize India's cab service industry! 🚗✨**
