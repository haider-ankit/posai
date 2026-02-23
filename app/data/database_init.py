"""
SQLite Database Initialization Script for Local-First POS System

This module provides database initialization, schema creation, and configuration
for the Local-First POS system. It implements the database design specified
in the design document with proper indexing, constraints, and performance optimizations.
"""

import sqlite3
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

configurations = {
    # Enable WAL mode for concurrent access.
    "JOURNAL_MODE": "PRAGMA JOURNAL_MODE = WAL",
    
    # Set synchronous mode to NORMAL for balanced performance/safety.
    "SYNCHRONOUS": "PRAGMA SYNCHRONOUS = NORMAL",
    
    # Enable foreign key constraints for data integrity.
    "FOREIGN_KEYS": "PRAGMA FOREIGN_KEYS = ON",
    
    # Set cache size to 64MB for better performance.
    "CACHE_SIZE": "PRAGMA CACHE_SIZE = -64000",
    
    # Enable automatic index creation for foreign keys.
    "AUTOMATIC_INDEX": "PRAGMA AUTOMATIC_INDEX = ON",
    
    # Set temp store to memory for faster operations.
    "TEMP_STORE": "PRAGMA TEMP_STORE = MEMORY"
}

tables = {
    # CATEGORIES table: Organizes products into categories, supporting a hierarchical 
    # structure (e.g., 'Electronics' can have 'Phones' as a child category). 
    # It stores the category's name, description, and a reference to its parent category.
    "CATEGORIES":        """CREATE TABLE IF NOT EXISTS CATEGORIES 
                            (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                NAME TEXT NOT NULL UNIQUE,
                                DESCRIPTION TEXT,
                                PARENT_ID INTEGER,
                                CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (PARENT_ID) REFERENCES CATEGORIES(ID) ON DELETE SET NULL
                            )
                        """,
    
    # SUPPLIERS table:  Manages information about product suppliers, 
    # including contact details, address, and lead time in days for orders.
    "SUPPLIERS":         """CREATE TABLE IF NOT EXISTS SUPPLIERS
                            (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                NAME TEXT NOT NULL UNIQUE,
                                CONTACT_PERSON TEXT,
                                EMAIL TEXT,
                                PHONE TEXT,
                                ADDRESS TEXT,
                                LEAD_TIME_DAYS INTEGER DEFAULT 7,
                                CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """,
    
    # PRODUCTS table: Stores details for each product, such as SKU, name, description, 
    # pricing (cost and selling), current stock levels, reorder levels, and links to its 
    # category and supplier. It ensures stock and pricing values are non-negative.
    "PRODUCTS":          """CREATE TABLE IF NOT EXISTS PRODUCTS
                            (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                SKU TEXT NOT NULL UNIQUE,
                                NAME TEXT NOT NULL,
                                DESCRIPTION TEXT,
                                CATEGORY_ID INTEGER,
                                SUPPLIER_ID INTEGER,
                                COST_PRICE DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                                SELLING_PRICE DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                                CURRENT_STOCK INTEGER NOT NULL DEFAULT 0,
                                REORDER_LEVEL INTEGER NOT NULL DEFAULT 10,
                                MAX_STOCK INTEGER,
                                IS_ACTIVE BOOLEAN DEFAULT 1,
                                CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (CATEGORY_ID) REFERENCES CATEGORIES(ID) ON DELETE SET NULL,
                                FOREIGN KEY (SUPPLIER_ID) REFERENCES SUPPLIERS(ID) ON DELETE SET NULL,
                                CHECK (COST_PRICE >= 0),
                                CHECK (SELLING_PRICE >= 0),
                                CHECK (CURRENT_STOCK >= 0),
                                CHECK (REORDER_LEVEL >= 0)
                            )
                        """,
    
    # TRANSACTIONS table: Records overall sales transactions, including a unique 
    # transaction number, subtotal, tax, discount, total amount, payment method, 
    # transaction status, and cashier information.
    "TRANSACTIONS":      """ CREATE TABLE IF NOT EXISTS TRANSACTIONS
                            (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                TRANSACTION_NUMBER TEXT NOT NULL UNIQUE,
                                SUBTOTAL DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                                TAX_AMOUNT DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                                DISCOUNT_AMOUNT DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                                TOTAL_AMOUNT DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                                PAYMENT_METHOD TEXT NOT NULL DEFAULT 'CASH',
                                STATUS TEXT NOT NULL DEFAULT 'PENDING',
                                CASHIER_ID TEXT,
                                NOTES TEXT,
                                CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                COMPLETED_AT TIMESTAMP,
                                CHECK (SUBTOTAL >= 0),
                                CHECK (TAX_AMOUNT >= 0),
                                CHECK (DISCOUNT_AMOUNT >= 0),
                                CHECK (TOTAL_AMOUNT >= 0),
                                CHECK (STATUS IN ('PENDING', 'COMPLETED', 'VOIDED', 'RETURNED')),
                                CHECK (PAYMENT_METHOD IN ('CASH', 'CARD', 'CHECK', 'OTHER'))
                            )
                        """,
    
    # TRANSACTION_ITEMS table: Details the individual products included in 
    # each transaction. It links to a specific transaction and product, 
    # storing the quantity, unit price, and discount for that item, with a calculated line total.
    "TRANSACTION_ITEMS": """CREATE TABLE IF NOT EXISTS TRANSACTION_ITEMS
                            (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                TRANSACTION_ID INTEGER NOT NULL,
                                PRODUCT_ID INTEGER NOT NULL,
                                SKU TEXT NOT NULL,
                                PRODUCT_NAME TEXT NOT NULL,
                                QUANTITY INTEGER NOT NULL DEFAULT 1,
                                UNIT_PRICE DECIMAL(10,2) NOT NULL,
                                DISCOUNT_AMOUNT DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                                LINE_TOTAL DECIMAL(10,2) GENERATED ALWAYS AS (
                                    (QUANTITY * UNIT_PRICE) - DISCOUNT_AMOUNT
                                ) STORED,
                                CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (TRANSACTION_ID) REFERENCES TRANSACTIONS(ID) ON DELETE CASCADE,
                                FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCTS(ID) ON DELETE RESTRICT,
                                CHECK (QUANTITY > 0),
                                CHECK (UNIT_PRICE >= 0),
                                CHECK (DISCOUNT_AMOUNT >= 0)
                            )
                        """,
    
    # INVENTORY_LOG table: Serves as an audit trail for all inventory 
    # movements (sales, restocks, adjustments, etc.). It records the product, 
    # movement type, quantity change, previous and new stock levels,
    "INVENTORY_LOG":     """CREATE TABLE IF NOT EXISTS INVENTORY_LOG
                            (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                PRODUCT_ID INTEGER NOT NULL,
                                SKU TEXT NOT NULL,
                                MOVEMENT_TYPE TEXT NOT NULL,
                                QUANTITY_CHANGE INTEGER NOT NULL,
                                PREVIOUS_STOCK INTEGER NOT NULL,
                                NEW_STOCK INTEGER NOT NULL,
                                REASON TEXT,
                                REFERENCE_TYPE TEXT,
                                REFERENCE_ID INTEGER,
                                USER_ID TEXT,
                                CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCTS(ID) ON DELETE RESTRICT,
                                CHECK (MOVEMENT_TYPE IN ('SALE', 'RESTOCK', 'ADJUSTMENT', 'DAMAGE', 'RETURN', 'TRANSFER')),
                                CHECK (NEW_STOCK >= 0)
                            )
                        """
}

indexes = {
    # Product table indexes.
    "IDX_PRODUCTS_SKU": "CREATE INDEX IF NOT EXISTS IDX_PRODUCTS_SKU ON PRODUCTS(SKU)",
    "IDX_PRODUCTS_CATEGORY": "CREATE INDEX IF NOT EXISTS IDX_PRODUCTS_CATEGORY ON PRODUCTS(CATEGORY_ID)",
    "IDX_PRODUCTS_SUPPLIER": "CREATE INDEX IF NOT EXISTS IDX_PRODUCTS_SUPPLIER ON PRODUCTS(SUPPLIER_ID)",
    "IDX_PRODUCTS_STOCK": "CREATE INDEX IF NOT EXISTS IDX_PRODUCTS_STOCK ON PRODUCTS(CURRENT_STOCK)",
    "IDX_PRODUCTS_ACTIVE": "CREATE INDEX IF NOT EXISTS IDX_PRODUCTS_ACTIVE ON PRODUCTS(IS_ACTIVE)",
    
    # Transaction table indexes.
    "IDX_TRANSACTIONS_NUMBER": "CREATE INDEX IF NOT EXISTS IDX_TRANSACTIONS_NUMBER ON TRANSACTIONS(TRANSACTION_NUMBER)",
    "IDX_TRANSACTIONS_DATE": "CREATE INDEX IF NOT EXISTS IDX_TRANSACTIONS_DATE ON TRANSACTIONS(CREATED_AT)",
    "IDX_TRANSACTIONS_STATUS": "CREATE INDEX IF NOT EXISTS IDX_TRANSACTIONS_STATUS ON TRANSACTIONS(STATUS)",
    "IDX_TRANSACTIONS_CASHIER": "CREATE INDEX IF NOT EXISTS IDX_TRANSACTIONS_CASHIER ON TRANSACTIONS(CASHIER_ID)",
    
    # Transaction items table indexes.
    "IDX_TRANSACTION_ITEMS_TRANSACTION": "CREATE INDEX IF NOT EXISTS IDX_TRANSACTION_ITEMS_TRANSACTION ON TRANSACTION_ITEMS(TRANSACTION_ID)",
    "IDX_TRANSACTION_ITEMS_PRODUCT": "CREATE INDEX IF NOT EXISTS IDX_TRANSACTION_ITEMS_PRODUCT ON TRANSACTION_ITEMS(PRODUCT_ID)",
    "IDX_TRANSACTION_ITEMS_SKU": "CREATE INDEX IF NOT EXISTS IDX_TRANSACTION_ITEMS_SKU ON TRANSACTION_ITEMS(SKU)",
    
    # Inventory log table indexes.
    "IDX_INVENTORY_LOG_PRODUCT": "CREATE INDEX IF NOT EXISTS IDX_INVENTORY_LOG_PRODUCT ON INVENTORY_LOG(PRODUCT_ID)",
    "IDX_INVENTORY_LOG_DATE": "CREATE INDEX IF NOT EXISTS IDX_INVENTORY_LOG_DATE ON INVENTORY_LOG(CREATED_AT)",
    "IDX_INVENTORY_LOG_TYPE": "CREATE INDEX IF NOT EXISTS IDX_INVENTORY_LOG_TYPE ON INVENTORY_LOG(MOVEMENT_TYPE)",
    "IDX_INVENTORY_LOG_REFERENCE": "CREATE INDEX IF NOT EXISTS IDX_INVENTORY_LOG_REFERENCE ON INVENTORY_LOG(REFERENCE_TYPE, REFERENCE_ID)",
    
    # Categories table indexes.
    "IDX_CATEGORIES_PARENT": "CREATE INDEX IF NOT EXISTS IDX_CATEGORIES_PARENT ON CATEGORIES(PARENT_ID)"
}

views = {
    # DAILY_SALES_SUMMARY view: Provides a daily summary of sales transactions, 
    # including total revenue, tax, discounts, and average transaction value for completed transactions.
    "DAILY_SALES_SUMMARY":  """CREATE VIEW IF NOT EXISTS DAILY_SALES_SUMMARY AS
                                SELECT 
                                    DATE(CREATED_AT) as SALE_DATE,
                                    COUNT(*) as TRANSACTION_COUNT,
                                    SUM(SUBTOTAL) as TOTAL_SUBTOTAL,
                                    SUM(TAX_AMOUNT) as TOTAL_TAX,
                                    SUM(DISCOUNT_AMOUNT) as TOTAL_DISCOUNTS,
                                    SUM(TOTAL_AMOUNT) as TOTAL_REVENUE,
                                    AVG(TOTAL_AMOUNT) as AVERAGE_TRANSACTION_VALUE
                                FROM TRANSACTIONS 
                                WHERE STATUS = 'COMPLETED'
                                GROUP BY DATE(CREATED_AT)
                                ORDER BY SALE_DATE DESC
                            """,
    
    # PRODUCT_PERFORMANCE view: Combines product details with sales performance metrics,
    # such as total quantity sold, total revenue, and profit. It also indicates stock status 
    # based on current stock levels and reorder thresholds.
    "PRODUCT_PERFORMANCE":  """CREATE VIEW IF NOT EXISTS PRODUCT_PERFORMANCE AS
                                SELECT 
                                    P.ID,
                                    P.SKU,
                                    P.NAME,
                                    C.NAME AS CATEGORY_NAME,
                                    S.NAME AS SUPPLIER_NAME,
                                    P.CURRENT_STOCK,
                                    P.REORDER_LEVEL,
                                    P.COST_PRICE,
                                    P.SELLING_PRICE,
                                    COALESCE(SALES.TOTAL_QUANTITY_SOLD, 0) AS TOTAL_QUANTITY_SOLD,
                                    COALESCE(SALES.TOTAL_REVENUE, 0) AS TOTAL_REVENUE,
                                    COALESCE(SALES.TOTAL_PROFIT, 0) AS TOTAL_PROFIT,
                                    CASE 
                                        WHEN P.CURRENT_STOCK <= P.REORDER_LEVEL THEN 'LOW_STOCK'
                                        WHEN P.CURRENT_STOCK = 0 THEN 'OUT_OF_STOCK'
                                        ELSE 'IN_STOCK'
                                    END AS STOCK_STATUS
                                FROM PRODUCTS P
                                LEFT JOIN CATEGORIES C ON P.CATEGORY_ID = C.ID
                                LEFT JOIN SUPPLIERS S ON P.SUPPLIER_ID = S.ID
                                LEFT JOIN (
                                    SELECT 
                                        TI.PRODUCT_ID,
                                        SUM(TI.QUANTITY) AS TOTAL_QUANTITY_SOLD,
                                        SUM(TI.LINE_TOTAL) AS TOTAL_REVENUE,
                                        SUM(TI.LINE_TOTAL - (TI.QUANTITY * P2.COST_PRICE)) AS TOTAL_PROFIT
                                    FROM TRANSACTION_ITEMS TI
                                    JOIN TRANSACTIONS T ON TI.TRANSACTION_ID = T.ID
                                    JOIN PRODUCTS P2 ON TI.PRODUCT_ID = P2.ID
                                    WHERE T.STATUS = 'COMPLETED'
                                    GROUP BY TI.PRODUCT_ID
                                ) SALES ON P.ID = SALES.PRODUCT_ID
                                WHERE P.IS_ACTIVE = 1
                            """,
    
    # LOW_STOCK_ALERTS view: Identifies products that are at or below their reorder level,
    # providing details such as current stock, supplier lead time, and an alert level 
    # (CRITICAL, URGENT, WARNING) based on how low the stock is compared to the reorder level.
    "LOW_STOCK_ALERTS":     """CREATE VIEW IF NOT EXISTS LOW_STOCK_ALERTS AS
                                SELECT 
                                    P.ID,
                                    P.SKU,
                                    P.NAME,
                                    C.NAME AS CATEGORY_NAME,
                                    P.CURRENT_STOCK,
                                    P.REORDER_LEVEL,
                                    S.NAME AS SUPPLIER_NAME,
                                    S.LEAD_TIME_DAYS,
                                    CASE 
                                        WHEN P.CURRENT_STOCK = 0 THEN 'CRITICAL'
                                        WHEN P.CURRENT_STOCK <= (P.REORDER_LEVEL * 0.5) THEN 'URGENT'
                                        ELSE 'WARNING'
                                    END AS ALERT_LEVEL
                                FROM PRODUCTS P
                                LEFT JOIN CATEGORIES C ON P.CATEGORY_ID = C.ID
                                LEFT JOIN SUPPLIERS S ON P.SUPPLIER_ID = S.ID
                                WHERE P.CURRENT_STOCK <= P.REORDER_LEVEL 
                                AND P.IS_ACTIVE = 1
                                ORDER BY ALERT_LEVEL, P.CURRENT_STOCK ASC
                            """
}

triggers = {
    # UPDATE_PRODUCT_TIMESTAMP trigger: To automatically update the UPDATED_AT timestamp on PRODUCTS, 
    # CATEGORIES, and SUPPLIERS when they are modified.
    "UPDATE_PRODUCT_TIMESTAMP": """CREATE TRIGGER IF NOT EXISTS UPDATE_PRODUCT_TIMESTAMP
                                    AFTER UPDATE ON PRODUCTS
                                    FOR EACH ROW
                                    BEGIN
                                        UPDATE PRODUCTS SET UPDATED_AT = CURRENT_TIMESTAMP WHERE ID = NEW.ID;
                                    END
                                """,
    
    # UPDATE_CATEGORY_TIMESTAMP trigger: To update CATEGORY UPDATED_AT timestamp.
    "UPDATE_CATEGORY_TIMESTAMP": """CREATE TRIGGER IF NOT EXISTS UPDATE_CATEGORY_TIMESTAMP
                                    AFTER UPDATE ON CATEGORIES
                                    FOR EACH ROW
                                    BEGIN
                                        UPDATE CATEGORIES SET UPDATED_AT = CURRENT_TIMESTAMP WHERE ID = NEW.ID;
                                    END
                                """,
    
    # UPDATE_SUPPLIER_TIMESTAMP trigger: To update SUPPLIER UPDATED_AT timestamp.
    "UPDATE_SUPPLIER_TIMESTAMP": """CREATE TRIGGER IF NOT EXISTS UPDATE_SUPPLIER_TIMESTAMP
                                    AFTER UPDATE ON SUPPLIERS
                                    FOR EACH ROW
                                    BEGIN
                                        UPDATE SUPPLIERS SET UPDATED_AT = CURRENT_TIMESTAMP WHERE ID = NEW.ID;
                                    END
                                """,
    
    # LOG_INVENTORY_CHANGES trigger: To automatically log any changes to product 
    # stock levels in the INVENTORY_LOG table, capturing the previous and new stock levels,
    # the reason for the change, and the type of movement (e.g., SALE, RESTOCK, ADJUSTMENT).
    "LOG_INVENTORY_CHANGES":     """CREATE TRIGGER IF NOT EXISTS LOG_INVENTORY_CHANGES
                                    AFTER UPDATE OF CURRENT_STOCK ON PRODUCTS
                                    FOR EACH ROW
                                    WHEN OLD.CURRENT_STOCK != NEW.CURRENT_STOCK
                                    BEGIN
                                        INSERT INTO INVENTORY_LOG (
                                            PRODUCT_ID, SKU, MOVEMENT_TYPE, QUANTITY_CHANGE, 
                                            PREVIOUS_STOCK, NEW_STOCK, REASON, REFERENCE_TYPE
                                        ) VALUES (
                                            NEW.ID, NEW.SKU, 'ADJUSTMENT', 
                                            NEW.CURRENT_STOCK - OLD.CURRENT_STOCK,
                                            OLD.CURRENT_STOCK, NEW.CURRENT_STOCK, 
                                            'STOCK LEVEL UPDATED', 'MANUAL'
                                        );
                                    END
                                """
}


class DatabaseInitializer:
    """
    Handles SQLite database initialization with proper schema creation,
    indexing, and performance configuration.
    """
    
    def __init__(self, db_path: str = "", conn = None, config: dict = None, table: dict = None, index: dict = None, view: dict = None, trigger: dict = None) -> None:
        """
        Initialize the database initializer.
        
        Args:
            conn: Database connection
            db_path: Path to the database file
            config: Dictionary of database pragmas for configuration
            table: Dictionary of table creation SQL statements
            index: Dictionary of index creation SQL statements
            view: Dictionary of view creation SQL statements
            trigger: Dictionary of trigger creation SQL statements
        """
        self.db_path = db_path
        self.conn = conn
        self.db_dir = os.path.dirname(db_path)
        self.config = config
        self.table = table
        self.index = index
        self.view = view
        self.trigger = trigger
        
    def initialize_database(self) -> bool:
        """
        Initialize the complete database with schema, indexes, and configuration.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Ensure database directory exists
            if self.db_dir:
                Path(self.db_dir).mkdir(parents=True, exist_ok=True)
            
            # Configure SQLite for optimal performance
            self._configure_sqlite()
            
            # Create all tables
            self._create_tables()
            
            # Create indexes for performance
            self._create_indexes()
            
            # Create views for AI queries
            self._create_views()
            
            # Create triggers for audit trail
            self._create_triggers()
            
            self.conn.commit()
            self.conn.close()
            
            logger.info(f"Database initialized successfully at {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    def _configure_sqlite(self) -> None:
        """
        Configure SQLite pragmas for optimal performance and data integrity.
        
        Args:
            conn: SQLite database connection
        """
        cursor = self.conn.cursor()
        
        for key, pragma in self.config.items():
            cursor.execute(f"{pragma}")
            logger.info(f"Applied pragma: {key} as {pragma}")
    
    def _create_tables(self) -> None:
        """
        Create all database tables according to the schema design.
        
        Args:
            conn: SQLite database connection
        """
        cursor = self.conn.cursor()
        
        for table_name, create_statement in self.table.items():
            cursor.execute(create_statement)
            logger.info(f"Table '{table_name}' created successfully")
    
    def _create_indexes(self) -> None:
        """
        Create database indexes for optimal query performance.
        
        Args:
            conn: SQLite database connection
        """
        cursor = self.conn.cursor()

        for index_name, create_statement in self.index.items():
            cursor.execute(create_statement)
            logger.info(f"Index '{index_name}' created successfully")
    
    def _create_views(self) -> None:
        """
        Create database views for AI queries and reporting.
        
        Args:
            conn: SQLite database connection
        """
        cursor = self.conn.cursor()

        for view_name, create_statement in self.view.items():
            cursor.execute(create_statement)
            logger.info(f"View '{view_name}' created successfully")
    
    def _create_triggers(self) -> None:
        """
        Create database triggers for automatic audit trail and data integrity.
        
        Args:
            conn: SQLite database connection
        """
        cursor = self.conn.cursor()

        for trigger_name, create_statement in self.trigger.items():
            cursor.execute(create_statement)
            logger.info(f"Trigger '{trigger_name}' created successfully")
    
    def verify_database(self, conn) -> bool:
        """
        Verify that the database was created correctly with all tables and indexes.
        
        Returns:
            bool: True if verification successful, False otherwise
        """
        try:
            cursor = conn.cursor()
            
            # Check if all tables exist
            expected_tables = self.table.keys()
            
            cursor.execute("SELECT NAME FROM SQLITE_MASTER WHERE TYPE = LOWER('TABLE')")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = set(expected_tables) - set(existing_tables)
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False
            
            # Check if views exist
            expected_views = self.view.keys()
            
            cursor.execute("SELECT NAME FROM SQLITE_MASTER WHERE TYPE = LOWER('VIEW')")
            existing_views = [row[0] for row in cursor.fetchall()]
            
            missing_views = set(expected_views) - set(existing_views)
            if missing_views:
                logger.error(f"Missing views: {missing_views}")
                return False
            
            # Verify WAL mode is enabled
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            if journal_mode.upper() != 'WAL':
                logger.error(f"WAL mode not enabled. Current mode: {journal_mode}")
                return False
            
            # Verify foreign keys are enabled
            # cursor.execute("PRAGMA foreign_keys = ON")
            # foreign_keys = cursor.fetchone()[0]
            # if not foreign_keys:
            #     logger.error("Foreign keys not enabled")
            #     return False
            
            conn.close()
            logger.info("Database verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            return False


def main():
    """
    Main function to initialize the database.
    """
    db_path = "database/posai.db"
    connection = sqlite3.connect(db_path)
    initializer = DatabaseInitializer(db_path=db_path, conn=connection, config=configurations, table=tables, index=indexes, view=views, trigger=triggers)
    
    if initializer.initialize_database():
        verification_connection = sqlite3.connect(db_path)
        if initializer.verify_database(verification_connection):
            print("Database initialization completed successfully!")
        else:
            print("Database initialization completed but verification failed!")
    else:
        print("Database initialization failed!")


if __name__ == "__main__":
    main()
