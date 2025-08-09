"""
Test server runner with SQLite configuration
"""

from dotenv import load_dotenv

load_dotenv()

from project import create_app
from test_config import TestConfig

app = create_app(TestConfig)

if __name__ == "__main__":
    print("🚀 Starting Flask-RESTX API Test Server...")
    print("📊 Using SQLite database for testing")
    print("🌐 Server will be available at: http://localhost:5000")
    print("📚 API Documentation: http://localhost:5000/api/v1/docs/")
    print("=" * 60)

    app.run(host="0.0.0.0", port=5000, debug=True)
