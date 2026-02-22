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


class DatabaseInitializer:
    """
    Handles SQLite database initialization with proper schema creation,
    indexing, and performance configuration.
    """
    
    def __init__(self, db_path: str = "database/posai.db"):
        """
        Initialize the database initializer.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.db_dir = os.path.dirname(db_path)
        
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
            
            # Create database connection
            conn = sqlite3.connect(self.db_path)
            
            # Configure SQLite for optimal performance
            self._configure_sqlite(conn)
            
            # Create all tables
            self._create_tables(conn)
            
            # Create indexes for performance
            self._create_indexes(conn)
            
            # Create views for AI queries
            self._create_views(conn)
            
            # Create triggers for audit trail
            self._create_triggers(conn)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database initialized successfully at {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    def _configure_sqlite(self, conn: sqlite3.Connection) -> None:
        """
        Configure SQLite pragmas for optimal performance and data integrity.
        
        Args:
            conn: SQLite database connection
        """
        cursor = conn.cursor()
        
        # Enable WAL mode for concurrent access
        cursor.execute("PRAGMA journal_mode = WAL")
        
        # Set synchronous mode to NORMAL for balanced performance/safety
        cursor.execute("PRAGMA synchronous = NORMAL")
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Set cache size to 64MB for better performance
        cursor.execute("PRAGMA cache_size = -64000")
        
        # Enable automatic index creation for foreign keys
        cursor.execute("PRAGMA automatic_index = ON")
        
        # Set temp store to memory for faster operations
        cursor.execute("PRAGMA temp_store = MEMORY")
        
        logger.info("SQLite configuration applied successfully")
    
    def _create_tables(self, conn: sqlite3.Connection) -> None:
        """
        Create all database tables according to the schema design.
        
        Args:
            conn: SQLite database connection
        """
        cursor = conn.cursor()
        
        # Categories table with hierarchical support
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CATEGORIES (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NAME TEXT NOT NULL UNIQUE,
                DESCRIPTION TEXT,
                PARENT_ID INTEGER,
                CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (PARENT_ID) REFERENCES CATEGORIES(ID) ON DELETE SET NULL
            )
        """)
        
        # Suppliers table with lead time tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS SUPPLIERS (
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
        """)
        
        # Products table with stock constraints and indexing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS PRODUCTS (
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
        """)
        
        # Transactions table with status tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TRANSACTIONS (
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
        """)
        
        # Transaction Items table with calculated columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TRANSACTION_ITEMS (
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
        """)
        
        # Inventory Log table for audit trail
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS INVENTORY_LOG (
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
        """)
        
        logger.info("Database tables created successfully")
    
    def _create_indexes(self, conn: sqlite3.Connection) -> None:
        """
        Create database indexes for optimal query performance.
        
        Args:
            conn: SQLite database connection
        """
        cursor = conn.cursor()
        
        # Product indexes for fast lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(supplier_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_stock ON products(current_stock)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active)")
        
        # Transaction indexes for reporting
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_number ON transactions(transaction_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_cashier ON transactions(cashier_id)")
        
        # Transaction items indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transaction_items_transaction ON transaction_items(transaction_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transaction_items_product ON transaction_items(product_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transaction_items_sku ON transaction_items(sku)")
        
        # Inventory log indexes for audit queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_log_product ON inventory_log(product_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_log_date ON inventory_log(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_log_type ON inventory_log(movement_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_log_reference ON inventory_log(reference_type, reference_id)")
        
        # Category hierarchy index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id)")
        
        logger.info("Database indexes created successfully")
    
    def _create_views(self, conn: sqlite3.Connection) -> None:
        """
        Create database views for AI queries and reporting.
        
        Args:
            conn: SQLite database connection
        """
        cursor = conn.cursor()
        
        # Daily sales summary view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS DAILY_SALES_SUMMARY AS
            SELECT 
                DATE(created_at) as sale_date,
                COUNT(*) as transaction_count,
                SUM(subtotal) as total_subtotal,
                SUM(tax_amount) as total_tax,
                SUM(discount_amount) as total_discounts,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as average_transaction_value
            FROM transactions 
            WHERE status = 'COMPLETED'
            GROUP BY DATE(created_at)
            ORDER BY sale_date DESC
        """)
        
        # Product performance view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS PRODUCT_PERFORMANCE AS
            SELECT 
                p.id,
                p.sku,
                p.name,
                c.name as category_name,
                s.name as supplier_name,
                p.current_stock,
                p.reorder_level,
                p.cost_price,
                p.selling_price,
                COALESCE(sales.total_quantity_sold, 0) as total_quantity_sold,
                COALESCE(sales.total_revenue, 0) as total_revenue,
                COALESCE(sales.total_profit, 0) as total_profit,
                CASE 
                    WHEN p.current_stock <= p.reorder_level THEN 'LOW_STOCK'
                    WHEN p.current_stock = 0 THEN 'OUT_OF_STOCK'
                    ELSE 'IN_STOCK'
                END as stock_status
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            LEFT JOIN (
                SELECT 
                    ti.product_id,
                    SUM(ti.quantity) as total_quantity_sold,
                    SUM(ti.line_total) as total_revenue,
                    SUM(ti.line_total - (ti.quantity * p2.cost_price)) as total_profit
                FROM transaction_items ti
                JOIN transactions t ON ti.transaction_id = t.id
                JOIN products p2 ON ti.product_id = p2.id
                WHERE t.status = 'COMPLETED'
                GROUP BY ti.product_id
            ) sales ON p.id = sales.product_id
            WHERE p.is_active = 1
        """)
        
        # Low stock alert view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS LOW_STOCK_ALERTS AS
            SELECT 
                p.id,
                p.sku,
                p.name,
                c.name as category_name,
                p.current_stock,
                p.reorder_level,
                s.name as supplier_name,
                s.lead_time_days,
                CASE 
                    WHEN p.current_stock = 0 THEN 'CRITICAL'
                    WHEN p.current_stock <= (p.reorder_level * 0.5) THEN 'URGENT'
                    ELSE 'WARNING'
                END as alert_level
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.current_stock <= p.reorder_level 
            AND p.is_active = 1
            ORDER BY alert_level, p.current_stock ASC
        """)
        
        logger.info("Database views created successfully")
    
    def _create_triggers(self, conn: sqlite3.Connection) -> None:
        """
        Create database triggers for automatic audit trail and data integrity.
        
        Args:
            conn: SQLite database connection
        """
        cursor = conn.cursor()
        
        # Trigger to update product updated_at timestamp
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_product_timestamp
            AFTER UPDATE ON products
            FOR EACH ROW
            BEGIN
                UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
        """)
        
        # Trigger to update category updated_at timestamp
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_category_timestamp
            AFTER UPDATE ON categories
            FOR EACH ROW
            BEGIN
                UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
        """)
        
        # Trigger to update supplier updated_at timestamp
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_supplier_timestamp
            AFTER UPDATE ON suppliers
            FOR EACH ROW
            BEGIN
                UPDATE suppliers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
        """)
        
        # Trigger to log inventory changes
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS log_inventory_changes
            AFTER UPDATE OF current_stock ON products
            FOR EACH ROW
            WHEN OLD.current_stock != NEW.current_stock
            BEGIN
                INSERT INTO inventory_log (
                    product_id, sku, movement_type, quantity_change, 
                    previous_stock, new_stock, reason, reference_type
                ) VALUES (
                    NEW.id, NEW.sku, 'ADJUSTMENT', 
                    NEW.current_stock - OLD.current_stock,
                    OLD.current_stock, NEW.current_stock, 
                    'Stock level updated', 'MANUAL'
                );
            END
        """)
        
        logger.info("Database triggers created successfully")
    
    def verify_database(self) -> bool:
        """
        Verify that the database was created correctly with all tables and indexes.
        
        Returns:
            bool: True if verification successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if all tables exist
            expected_tables = [
                'CATEGORIES', 'SUPPLIERS', 'PRODUCTS', 
                'TRANSACTIONS', 'TRANSACTION_ITEMS', 'INVENTORY_LOG'
            ]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = set(expected_tables) - set(existing_tables)
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False
            
            # Check if views exist
            expected_views = [
                'DAILY_SALES_SUMMARY', 'PRODUCT_PERFORMANCE', 'LOW_STOCK_ALERTS'
            ]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
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
    initializer = DatabaseInitializer()
    
    if initializer.initialize_database():
        if initializer.verify_database():
            print("Database initialization completed successfully!")
        else:
            print("Database initialization completed but verification failed!")
    else:
        print("Database initialization failed!")


if __name__ == "__main__":
    main()