# 🚗 India Cab Service - AI-Powered Ride Booking Platform

A comprehensive cab service application with user authentication, city-based place suggestions, AI-powered route analysis, real-time pricing, and admin management dashboard.

## 🚀 New Features

### Real Geocoding & Distance Calculation

- **Geopy Integration**: Real latitude/longitude coordinates using OpenStreetMap Nominatim
- **Accurate Distance**: GPS-calculated distances between origin and destination
- **Real Route Points**: Actual coordinates for route visualization
- **Fallback System**: Smart fallback to predefined distances if geocoding fails
- **Enhanced Places**: Real coordinates for places along routes

### User Authentication System

- **Sign Up/Sign In**: Complete user registration with password protection and state/city selection
- **Password Security**: SHA-256 hashed passwords for secure authentication
- **First User Admin**: The very first user to sign up automatically becomes admin
- **User Profiles**: Each user has a default city and state for personalized experience

### City-Based Place Management

- **State & City Selection**: Users select their state and city during sign-up
- **AI-Powered Place Validation**: Gemini grounding search validates if places exist in selected cities
- **Dynamic Place Suggestions**: Real-time AI-generated suggestions for famous places in any city
- **Smart Validation**: "Place not found in city" error for invalid locations with AI verification

### Enhanced Booking Flow

- **City Selection**: Separate city selection for origin and destination
- **Place Validation**: "Place not found in city" error for invalid locations
- **Default City**: User's sign-up city is set as default for both origin and destination
- **Cross-City Travel**: Support for inter-city and intra-city bookings

## 🌟 Core Features

### User Interface

- **Smart Route Planning**: AI analyzes traffic and weather conditions for optimal routes
- **Multiple Vehicle Options**: Bike, Car, Premium, and 6-Seater vehicles
- **Transparent Pricing**: Clear breakdown of fares, driver earnings, and company profit
- **Real-time Conditions**: Live weather and traffic data integration
- **Booking Management**: Track and manage your ride bookings
- **City-Based Suggestions**: Get suggestions for famous places in your city

### Admin Panel

- **Dashboard Overview**: Key metrics and revenue analytics
- **User Management**: View all users, admin privileges, and registration details
- **Route Management**: Analyze route performance and profitability
- **Booking Management**: Monitor and manage all bookings
- **Advanced Analytics**: Vehicle performance and revenue insights
- **Settings**: Configure vehicle types and system parameters

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI Analysis**: Google Gemini API
- **Data Visualization**: Plotly
- **Backend**: Python
- **Data Storage**: JSON files (easily upgradeable to database)

## 📁 Project Structure

```
Ride Price Prediction/
├── main.py                          # Main application entry point
├── config.py                        # Configuration settings
├── requirements.txt                 # Python dependencies
├── env_example.txt                  # Environment variables template
├── README.md                        # This file
├── services/                        # Core business logic
│   ├── __init__.py
│   ├── ai_service.py               # AI analysis service
│   ├── auth_service.py             # User authentication service
│   ├── database_service.py         # SQLite database operations
│   ├── route_service.py            # Route calculation service
│   └── booking_service.py          # Booking management service
├── ui/                             # User interfaces
│   ├── __init__.py
│   ├── user_interface.py          # User booking interface
│   └── admin_interface.py         # Admin dashboard
└── main.db                         # SQLite database (created automatically)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

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

- **Welcome Page**: Non-logged-in users see features and get started info
- **Sign Up**: Create account with state and city selection (first user becomes admin)
- **Sign In**: Use email to log in
- **User Interface**: Book rides with city-based place suggestions
- **Admin Panel**: First user and other admins can access management features

## 🎯 Usage Guide

### For New Users

1. **Sign Up**:
   - Enter your details (name, email, phone, password)
   - Select your state and city
   - Password must be at least 6 characters
   - First user automatically gets admin access
   - Get personalized city-based suggestions

2. **Book a Ride**:
   - Select origin city and enter specific place
   - Select destination city and enter specific place
   - System validates places exist in selected cities
   - Choose vehicle type (Bike, Car, Premium, 6-Seater)
   - Get city-specific place suggestions
   - Click "Search for Rides"
   - Choose between suggested routes
   - Confirm your booking

3. **View Bookings**:
   - Navigate to "My Bookings" page
   - View booking history and status
   - Cancel pending bookings if needed

### For Existing Users

1. **Sign In**: Use your email and password to log in
2. **Book Rides**: Same process as new users with your default city pre-selected
3. **Admin Access**: If you're an admin, access the admin panel

### For Admins

1. **User Management**:
   - View all users and their details
   - See admin privileges and first user status
   - Monitor user registration and city preferences

2. **Dashboard Overview**:
   - Monitor key business metrics
   - View recent bookings
   - Analyze revenue trends

3. **Route Management**:
   - Analyze route performance
   - View top-performing routes
   - Manual route analysis

4. **Booking Management**:
   - Filter and view all bookings
   - Confirm pending bookings
   - Monitor booking status

5. **Analytics**:
   - Vehicle type performance
   - Revenue breakdown
   - Business insights

## 🗺️ AI-Powered Place Management

The platform uses Gemini's grounding search for dynamic place validation and suggestions:

- **Real-time Validation**: AI verifies if places exist in selected cities
- **Dynamic Suggestions**: Get famous places for any Indian city instantly
- **Smart Error Handling**: Clear feedback when places don't exist in the specified city
- **No Static Database**: All place data is fetched dynamically using AI

### Supported Cities

The platform supports all major Indian cities across all states:

- **Maharashtra**: Mumbai, Pune, Nagpur, Nashik, Aurangabad, etc.
- **Delhi**: New Delhi, Central Delhi, North Delhi, South Delhi, etc.
- **Karnataka**: Bangalore, Mysore, Hubli, Mangalore, etc.
- **Tamil Nadu**: Chennai, Coimbatore, Madurai, Tiruchirappalli, etc.
- **Gujarat**: Ahmedabad, Surat, Vadodara, Rajkot, etc.
- And many more states and cities!

### AI-Powered Features

- **Place Validation**: Gemini searches and validates if places exist in cities
- **City Suggestions**: AI generates famous places for any city on demand
- **Real-time Data**: Always up-to-date information from web search
- **Intelligent Parsing**: Smart response parsing for accurate validation

## 🔧 Configuration

### Vehicle Types

Modify `config.py` to adjust vehicle pricing and settings:

```python
VEHICLE_TYPES = {
    "bike": {
        "base_rate_per_km": 8,
        "base_fare": 20,
        "name": "Bike",
        "capacity": 1,
        "icon": "🏍️"
    },
    # ... other vehicle types
}
```

### States and Cities

Add new states and cities in `config.py` (for dropdown selection only):

```python
INDIAN_STATES = {
    "Your State": [
        "City1", "City2", "City3"
    ]
}
```

**Note**: Place validation and suggestions are now handled dynamically by Gemini AI, so no need to maintain a static database of famous places.

### Pricing Multipliers

Adjust weather and traffic multipliers in `config.py`:

```python
WEATHER_MULTIPLIERS = {
    "clear": 1.0,
    "light_rain": 1.2,
    "heavy_rain": 1.5,
    # ... other conditions
}
```

## 📊 Data Storage

The application uses SQLite database for secure data storage:

- `main.db`: SQLite database containing all application data
- **Users Table**: User accounts, profiles, and authentication data
- **Admins Table**: Admin users and privileges
- **Bookings Table**: All booking records and history
- **Admin Data Table**: Analytics and statistics

### Security Features

- **Password Hashing**: All passwords are SHA-256 hashed before storage
- **No Plain Text**: Sensitive data is never stored in readable format
- **Database Integrity**: ACID compliance ensures data consistency

### User Data Structure

```json
{
  "id": "USER20241201123456",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "state": "Maharashtra",
  "city": "Mumbai",
  "is_admin": true,
  "created_at": "2024-12-01T12:34:56"
}
```

For production use, consider upgrading to a proper database (PostgreSQL, MongoDB, etc.).

## 🔐 Security Notes

- First user automatically becomes admin (secure for initial setup)
- Use environment variables for sensitive data
- User authentication is required for all operations
- Place validation prevents invalid location entries
- Add input validation and sanitization for production

## 🗺️ Geocoding & Distance Features

### Real GPS Integration

- **Geopy Library**: Uses OpenStreetMap Nominatim for geocoding
- **Accurate Distances**: GPS-calculated distances between any two locations
- **Real Coordinates**: Actual latitude/longitude for route visualization
- **Smart Fallback**: Predefined distances for known city pairs if geocoding fails

### Installation

To use the geocoding features, install the required dependency:

```bash
# Install geopy for real geocoding
pip install geopy==2.4.1

# Or run the installation script
python install_geopy.py
```

### Features

- **Real Distance Calculation**: GPS-accurate distances using geodesic calculations
- **Route Visualization**: Real coordinates for route points and waypoints
- **Place Coordinates**: Actual coordinates for places along routes
- **Fallback System**: Smart fallback to predefined distances for reliability

## 🚀 Future Enhancements

- [x] Real geocoding and distance calculation
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Real-time GPS tracking
- [ ] Payment gateway integration
- [ ] Driver mobile app
- [ ] Push notifications
- [ ] Advanced route optimization
- [ ] Multi-language support
- [ ] API endpoints for mobile apps

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Developed with ❤️ for India's transportation needs**
