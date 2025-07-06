#!/usr/bin/env python3
"""
AI Agentic System for Dataset Analysis using Semantic Kernel
Dataset: Northwind Database (11 tables)
"""

import asyncio
import sqlite3
import pandas as pd
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Semantic Kernel imports
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.core_plugins.text_plugin import TextPlugin
from semantic_kernel.core_plugins.math_plugin import MathPlugin
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments

# Database setup and sample data creation
class NorthwindDatabase:
    def __init__(self, db_path: str = "northwind.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Create and populate the Northwind database with sample data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        tables = {
            'Categories': '''
                CREATE TABLE IF NOT EXISTS Categories (
                    CategoryID INTEGER PRIMARY KEY,
                    CategoryName TEXT NOT NULL,
                    Description TEXT
                )
            ''',
            'Suppliers': '''
                CREATE TABLE IF NOT EXISTS Suppliers (
                    SupplierID INTEGER PRIMARY KEY,
                    CompanyName TEXT NOT NULL,
                    ContactName TEXT,
                    Country TEXT
                )
            ''',
            'Products': '''
                CREATE TABLE IF NOT EXISTS Products (
                    ProductID INTEGER PRIMARY KEY,
                    ProductName TEXT NOT NULL,
                    CategoryID INTEGER,
                    SupplierID INTEGER,
                    UnitPrice REAL,
                    UnitsInStock INTEGER,
                    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID),
                    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID)
                )
            ''',
            'Customers': '''
                CREATE TABLE IF NOT EXISTS Customers (
                    CustomerID TEXT PRIMARY KEY,
                    CompanyName TEXT NOT NULL,
                    ContactName TEXT,
                    Country TEXT,
                    City TEXT
                )
            ''',
            'Employees': '''
                CREATE TABLE IF NOT EXISTS Employees (
                    EmployeeID INTEGER PRIMARY KEY,
                    FirstName TEXT NOT NULL,
                    LastName TEXT NOT NULL,
                    Title TEXT,
                    HireDate DATE,
                    Country TEXT
                )
            ''',
            'Shippers': '''
                CREATE TABLE IF NOT EXISTS Shippers (
                    ShipperID INTEGER PRIMARY KEY,
                    CompanyName TEXT NOT NULL,
                    Phone TEXT
                )
            ''',
            'Orders': '''
                CREATE TABLE IF NOT EXISTS Orders (
                    OrderID INTEGER PRIMARY KEY,
                    CustomerID TEXT,
                    EmployeeID INTEGER,
                    OrderDate DATE,
                    ShipperID INTEGER,
                    ShipCountry TEXT,
                    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
                    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
                    FOREIGN KEY (ShipperID) REFERENCES Shippers(ShipperID)
                )
            ''',
            'OrderDetails': '''
                CREATE TABLE IF NOT EXISTS OrderDetails (
                    OrderID INTEGER,
                    ProductID INTEGER,
                    UnitPrice REAL,
                    Quantity INTEGER,
                    Discount REAL,
                    PRIMARY KEY (OrderID, ProductID),
                    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
                    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
                )
            ''',
            'Region': '''
                CREATE TABLE IF NOT EXISTS Region (
                    RegionID INTEGER PRIMARY KEY,
                    RegionDescription TEXT NOT NULL
                )
            ''',
            'Territories': '''
                CREATE TABLE IF NOT EXISTS Territories (
                    TerritoryID TEXT PRIMARY KEY,
                    TerritoryDescription TEXT NOT NULL,
                    RegionID INTEGER,
                    FOREIGN KEY (RegionID) REFERENCES Region(RegionID)
                )
            ''',
            'EmployeeTerritories': '''
                CREATE TABLE IF NOT EXISTS EmployeeTerritories (
                    EmployeeID INTEGER,
                    TerritoryID TEXT,
                    PRIMARY KEY (EmployeeID, TerritoryID),
                    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
                    FOREIGN KEY (TerritoryID) REFERENCES Territories(TerritoryID)
                )
            '''
        }
        
        for table_name, create_sql in tables.items():
            cursor.execute(create_sql)
        
        # Insert sample data
        self.insert_sample_data(cursor)
        
        conn.commit()
        conn.close()
    
    def insert_sample_data(self, cursor):
        """Insert sample data into all tables"""
        # Categories
        categories = [
            (1, 'Beverages', 'Soft drinks, coffees, teas, beers, and ales'),
            (2, 'Condiments', 'Sweet and savory sauces, relishes, spreads, and seasonings'),
            (3, 'Dairy Products', 'Cheeses'),
            (4, 'Grains/Cereals', 'Breads, crackers, pasta, and cereal'),
            (5, 'Seafood', 'Seaweed and fish')
        ]
        cursor.executemany('INSERT OR IGNORE INTO Categories VALUES (?, ?, ?)', categories)
        
        # Suppliers
        suppliers = [
            (1, 'Exotic Liquids', 'Charlotte Cooper', 'UK'),
            (2, 'New Orleans Cajun Delights', 'Shelley Burke', 'USA'),
            (3, 'Tokyo Traders', 'Yoshi Nagase', 'Japan'),
            (4, 'Nord-Ost-Fisch', 'Sven Petersen', 'Germany'),
            (5, 'Formaggi Fortini', 'Elio Rossi', 'Italy')
        ]
        cursor.executemany('INSERT OR IGNORE INTO Suppliers VALUES (?, ?, ?, ?)', suppliers)
        
        # Products
        products = [
            (1, 'Chai', 1, 1, 18.0, 39),
            (2, 'Chang', 1, 1, 19.0, 17),
            (3, 'Aniseed Syrup', 2, 1, 10.0, 13),
            (4, 'Chef Anton Cajun Seasoning', 2, 2, 22.0, 53),
            (5, 'Gumbo Mix', 2, 2, 21.35, 0),
            (6, 'Mozzarella di Giovanni', 3, 5, 34.8, 14),
            (7, 'Gorgonzola Telino', 3, 5, 12.5, 0),
            (8, 'Mascarpone Fabioli', 3, 5, 32.0, 9),
            (9, 'Røgede sild', 5, 4, 9.65, 5),
            (10, 'Spegesild', 5, 4, 12.0, 95)
        ]
        cursor.executemany('INSERT OR IGNORE INTO Products VALUES (?, ?, ?, ?, ?, ?)', products)
        
        # Customers
        customers = [
            ('ALFKI', 'Alfreds Futterkiste', 'Maria Anders', 'Germany', 'Berlin'),
            ('ANATR', 'Ana Trujillo Emparedados', 'Ana Trujillo', 'Mexico', 'México D.F.'),
            ('BERGS', 'Berglunds snabbköp', 'Christina Berglund', 'Sweden', 'Luleå'),
            ('BLAUS', 'Blauer See Delikatessen', 'Hanna Moos', 'Germany', 'Mannheim'),
            ('BOLID', 'Bólido Comidas', 'Martín Sommer', 'Spain', 'Madrid')
        ]
        cursor.executemany('INSERT OR IGNORE INTO Customers VALUES (?, ?, ?, ?, ?)', customers)
        
        # Employees
        employees = [
            (1, 'Nancy', 'Davolio', 'Sales Representative', '1992-05-01', 'USA'),
            (2, 'Andrew', 'Fuller', 'Vice President, Sales', '1992-08-14', 'USA'),
            (3, 'Janet', 'Leverling', 'Sales Representative', '1992-04-01', 'USA'),
            (4, 'Margaret', 'Peacock', 'Sales Representative', '1993-05-03', 'USA'),
            (5, 'Steven', 'Buchanan', 'Sales Manager', '1993-10-17', 'UK')
        ]
        cursor.executemany('INSERT OR IGNORE INTO Employees VALUES (?, ?, ?, ?, ?, ?)', employees)
        
        # Continue with other tables...
        shippers = [
            (1, 'Speedy Express', '(503) 555-9831'),
            (2, 'United Package', '(503) 555-3199'),
            (3, 'Federal Shipping', '(503) 555-9931')
        ]
        cursor.executemany('INSERT OR IGNORE INTO Shippers VALUES (?, ?, ?)', shippers)
        
        # Orders and OrderDetails would be populated similarly
        # For brevity, I'll create a few sample orders
        orders = [
            (10248, 'ALFKI', 5, '1996-07-04', 3, 'Germany'),
            (10249, 'BERGS', 6, '1996-07-05', 1, 'Sweden'),
            (10250, 'BLAUS', 4, '1996-07-08', 2, 'Germany')
        ]
        cursor.executemany('INSERT OR IGNORE INTO Orders VALUES (?, ?, ?, ?, ?, ?)', orders)
        
        order_details = [
            (10248, 1, 18.0, 12, 0.0),
            (10248, 2, 19.0, 10, 0.0),
            (10249, 3, 10.0, 5, 0.0),
            (10250, 4, 22.0, 15, 0.15)
        ]
        cursor.executemany('INSERT OR IGNORE INTO OrderDetails VALUES (?, ?, ?, ?, ?)', order_details)

# Database Plugin for Semantic Kernel
class DatabasePlugin:
    def __init__(self, db_path: str = "northwind.db"):
        self.db_path = db_path
    
    @kernel_function(
        description="Execute a SQL query against the Northwind database",
        name="execute_query"
    )
    def execute_query(self, query: str) -> str:
        """Execute SQL query and return results as JSON"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df.to_json(orient='records', indent=2)
        except Exception as e:
            return f"Error executing query: {str(e)}"
    
    @kernel_function(
        description="Get table schema information",
        name="get_table_schema"
    )
    def get_table_schema(self, table_name: str) -> str:
        """Get schema information for a specific table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            conn.close()
            
            schema_info = []
            for col in columns:
                schema_info.append({
                    'column': col[1],
                    'type': col[2],
                    'nullable': not col[3],
                    'default': col[4]
                })
            
            return json.dumps(schema_info, indent=2)
        except Exception as e:
            return f"Error getting schema: {str(e)}"
    
    @kernel_function(
        description="List all tables in the database",
        name="list_tables"
    )
    def list_tables(self) -> str:
        """List all tables in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            table_list = [table[0] for table in tables]
            return json.dumps(table_list, indent=2)
        except Exception as e:
            return f"Error listing tables: {str(e)}"

# Analytics Plugin
class AnalyticsPlugin:
    def __init__(self, db_path: str = "northwind.db"):
        self.db_path = db_path
    
    @kernel_function(
        description="Analyze sales performance by category",
        name="analyze_sales_by_category"
    )
    def analyze_sales_by_category(self) -> str:
        """Analyze sales performance by product category"""
        query = """
        SELECT 
            c.CategoryName,
            COUNT(od.OrderID) as TotalOrders,
            SUM(od.Quantity) as TotalQuantity,
            SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) as TotalRevenue,
            AVG(od.UnitPrice * od.Quantity * (1 - od.Discount)) as AvgOrderValue
        FROM OrderDetails od
        JOIN Products p ON od.ProductID = p.ProductID
        JOIN Categories c ON p.CategoryID = c.CategoryID
        GROUP BY c.CategoryName
        ORDER BY TotalRevenue DESC
        """
        
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df.to_json(orient='records', indent=2)
        except Exception as e:
            return f"Error analyzing sales: {str(e)}"
    
    @kernel_function(
        description="Get top performing products",
        name="get_top_products"
    )
    def get_top_products(self, limit: int = 10) -> str:
        """Get top performing products by revenue"""
        query = f"""
        SELECT 
            p.ProductName,
            c.CategoryName,
            SUM(od.Quantity) as TotalQuantitySold,
            SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) as TotalRevenue
        FROM Products p
        JOIN Categories c ON p.CategoryID = c.CategoryID
        LEFT JOIN OrderDetails od ON p.ProductID = od.ProductID
        GROUP BY p.ProductName, c.CategoryName
        ORDER BY TotalRevenue DESC
        LIMIT {limit}
        """
        
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df.to_json(orient='records', indent=2)
        except Exception as e:
            return f"Error getting top products: {str(e)}"

# Main AI Agent Class
class NorthwindAIAgent:
    def __init__(self, openai_api_key: str, db_path: str = "northwind.db"):
        self.kernel = sk.Kernel()
        
        # Add OpenAI chat completion service
        self.kernel.add_service(OpenAIChatCompletion(
            ai_model_id="gpt-4",
            api_key=openai_api_key,
            service_id="chat-gpt"
        ))
        
        # Import plugins
        self.kernel.add_plugin(DatabasePlugin(db_path), plugin_name="database")
        self.kernel.add_plugin(AnalyticsPlugin(db_path), plugin_name="analytics")
        self.kernel.add_plugin(TextPlugin(), plugin_name="text")
        self.kernel.add_plugin(MathPlugin(), plugin_name="math")
        
        # Initialize database
        self.db = NorthwindDatabase(db_path)
        
        # Define main agent prompt
        self.agent_prompt = """
        You are an AI agent specializing in analyzing the Northwind database.
        
        The database contains 11 tables:
        1. Categories - Product categories
        2. Suppliers - Supplier information  
        3. Products - Product catalog
        4. Customers - Customer information
        5. Employees - Employee records
        6. Shippers - Shipping companies
        7. Orders - Order records
        8. OrderDetails - Order line items
        9. Region - Geographic regions
        10. Territories - Sales territories
        11. EmployeeTerritories - Employee territory assignments
        
        Available functions:
        - database.execute_query: Execute SQL queries
        - database.get_table_schema: Get table structure
        - database.list_tables: List all tables
        - analytics.analyze_sales_by_category: Analyze sales by category
        - analytics.get_top_products: Get top performing products
        
        User Query: {{$query}}
        
        Analyze the query and provide a comprehensive answer using the available functions.
        If you need to write SQL queries, make sure they are compatible with SQLite syntax.
        """
    
    async def process_query(self, user_query: str) -> str:
        """Process user query and return AI agent response"""
        try:
            # Create kernel arguments
            arguments = KernelArguments(query=user_query)
            
            # Execute the agent prompt
            response = await self.kernel.invoke_prompt(
                function_name="agent_response",
                plugin_name="main",
                prompt=self.agent_prompt,
                arguments=arguments
            )
            
            return str(response)
        except Exception as e:
            return f"Error processing query: {str(e)}"

# Example usage and demonstration
async def main():
    # You'll need to set your OpenAI API key here
    OPENAI_API_KEY = "your-openai-api-key-here"
    
    if OPENAI_API_KEY == "your-openai-api-key-here":
        print("⚠️  Please set your OpenAI API key in the OPENAI_API_KEY variable")
        return
    
    # Create AI agent
    agent = NorthwindAIAgent(OPENAI_API_KEY)
    
    print("🤖 Northwind AI Agent System")
    print("=" * 50)
    print("Dataset: Northwind Database with 11 tables")
    print("Ask me anything about the data!")
    print("Type 'exit' to quit, 'tables' to see available tables")
    print()
    
    while True:
        user_input = input("\n🔍 Your question: ").strip()
        
        if user_input.lower() == 'exit':
            print("👋 Goodbye!")
            break
        
        if user_input.lower() == 'tables':
            # Show available tables
            db_plugin = DatabasePlugin()
            tables = db_plugin.list_tables()
            print(f"\n📊 Available tables:\n{tables}")
            continue
        
        if not user_input:
            continue
        
        print("\n🤔 Processing your query...")
        
        try:
            response = await agent.process_query(user_input)
            print(f"\n🤖 Agent Response:\n{response}")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

# Demo queries for testing
async def run_demo():
    """Run a demonstration with sample queries"""
    OPENAI_API_KEY = "your-openai-api-key-here"
    
    if OPENAI_API_KEY == "your-openai-api-key-here":
        print("⚠️  Please set your OpenAI API key to run the demo")
        return
    
    agent = NorthwindAIAgent(OPENAI_API_KEY)
    
    demo_queries = [
        "What are the top 5 best-selling products?",
        "Show me sales performance by category",
        "Which customers have placed the most orders?",
        "What's the average order value?",
        "Show me the database schema for the Products table",
        "Which suppliers provide the most products?",
        "What are the total sales by country?",
        "Show me employee sales performance",
        "What products are currently out of stock?",
        "Analyze the seasonal trends in our sales data"
    ]
    
    print("🎯 Running Demo Queries")
    print("=" * 50)
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n📋 Demo Query {i}: {query}")
        try:
            response = await agent.process_query(query)
            print(f"🤖 Response: {response[:500]}...")  # Truncate for demo
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Add a small delay between queries
        await asyncio.sleep(1)

if __name__ == "__main__":
    print("Choose mode:")
    print("1. Interactive mode")
    print("2. Demo mode")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(main())
    elif choice == "2":
        asyncio.run(run_demo())
    else:
        print("Invalid choice. Running interactive mode...")
        asyncio.run(main())