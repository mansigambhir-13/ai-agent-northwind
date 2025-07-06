# test_agent.py
import pytest
import asyncio
from main import NorthwindAIAgent, NorthwindDatabase
from plugins.database_plugin import DatabasePlugin
from plugins.analytics_plugin import AnalyticsPlugin

class TestNorthwindAIAgent:
    """Test suite for the AI agent system"""
    
    @pytest.fixture
    def setup_database(self):
        """Setup test database"""
        db = NorthwindDatabase("test_northwind.db")
        yield db
        # Cleanup
        import os
        if os.path.exists("test_northwind.db"):
            os.remove("test_northwind.db")
    
    @pytest.fixture
    def database_plugin(self, setup_database):
        """Create database plugin for testing"""
        return DatabasePlugin("test_northwind.db")
    
    @pytest.fixture
    def analytics_plugin(self, setup_database):
        """Create analytics plugin for testing"""
        return AnalyticsPlugin("test_northwind.db")
    
    def test_database_creation(self, setup_database):
        """Test database creation and table setup"""
        db_plugin = DatabasePlugin("test_northwind.db")
        tables = db_plugin.list_tables()
        
        # Should have 11 tables
        import json
        table_list = json.loads(tables)
        assert len(table_list) >= 11
        
        # Check for specific tables
        required_tables = [
            'Categories', 'Suppliers', 'Products', 'Customers', 
            'Employees', 'Shippers', 'Orders', 'OrderDetails',
            'Region', 'Territories', 'EmployeeTerritories'
        ]
        
        for table in required_tables:
            assert table in table_list
    
    def test_query_execution(self, database_plugin):
        """Test SQL query execution"""
        result = database_plugin.execute_query("SELECT COUNT(*) as count FROM Categories")
        assert "Error" not in result
        
        import json
        data = json.loads(result)
        assert len(data) > 0
        assert 'count' in data[0]
    
    def test_schema_retrieval(self, database_plugin):
        """Test table schema retrieval"""
        schema = database_plugin.get_table_schema("Products")
        assert "Error" not in schema
        
        import json
        schema_data = json.loads(schema)
        assert len(schema_data) > 0
        
        # Check for expected columns
        column_names = [col['column'] for col in schema_data]
        expected_columns = ['ProductID', 'ProductName', 'CategoryID', 'SupplierID']
        
        for col in expected_columns:
            assert col in column_names
    
    def test_analytics_functions(self, analytics_plugin):
        """Test analytics plugin functions"""
        # Test sales analysis
        sales_data = analytics_plugin.analyze_sales_by_category()
        assert "Error" not in sales_data
        
        # Test top products
        top_products = analytics_plugin.get_top_products(5)
        assert "Error" not in top_products
    
    def test_error_handling(self, database_plugin):
        """Test error handling for invalid queries"""
        # Invalid SQL should return error message
        result = database_plugin.execute_query("INVALID SQL QUERY")
        assert "Error" in result
        
        # Invalid table name should return error
        schema = database_plugin.get_table_schema("NonExistentTable")
        assert "Error" in schema

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])