# Local-First POS System - Design Document

## 1. System Architecture Overview

### 1.1 Architectural Philosophy: Edge-Centric Intelligence

The Local-First POS system implements an "Edge-Centric Intelligence" architecture where all application logic, data storage, and AI inference occur on the local device. This design eliminates cloud dependencies while providing enterprise-grade capabilities.

**Core Principles:**
- **Local-First Data**: SQLite database as the single source of truth
- **Offline AI**: Embedded LLM for natural language processing
- **Atomic Operations**: ACID-compliant transaction processing
- **Hardware Integration**: Direct control of POS peripherals

### 1.2 System Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Local POS Terminal                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    Flet     │  │   SQLite    │  │    Ollama + LLM     │  │
│  │     UI      │  │  Database   │  │   (Mistral/Llama)   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Vanna.ai  │  │ Statsmodels │  │     Hardware        │  │
│  │ Text-to-SQL │  │ Forecasting │  │   Integration       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────▼────────┐  ┌──────▼──────┐
            │ Thermal Printer │  │   Barcode   │
            │   (ESC/POS)     │  │   Scanner   │
            └────────────────┘  └─────────────┘
```

## 2. Technology Stack and Rationale

### 2.1 Database Layer: SQLite with WAL Mode

**Selection Rationale:**
- **Serverless Architecture**: No background processes to manage or crash
- **ACID Compliance**: Atomic transactions with rollback capability
- **Concurrent Access**: WAL mode enables simultaneous read/write operations
- **Portability**: Single-file database simplifies backup and migration
- **Performance**: Optimized for local access patterns

**Configuration:**
```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
PRAGMA foreign_keys=ON;
```

### 2.2 User Interface: Flet Framework

**Selection Rationale:**
- **Modern Performance**: Flutter engine with Skia graphics
- **Python Integration**: Native Python development without JavaScript
- **Touch Optimization**: Material Design with responsive layouts
- **Offline Assets**: Local asset bundling for complete offline operation
- **Cross-Platform**: Single codebase for Windows, macOS, Linux

**Architecture Pattern:**
- **Model-View-Controller (MVC)**: Clear separation of concerns
- **Reactive State Management**: Automatic UI updates on data changes
- **Asynchronous Operations**: Non-blocking AI queries and hardware I/O

### 2.3 AI Stack: Vanna.ai + Ollama + Local LLM

**Selection Rationale:**
- **Offline Operation**: Complete independence from cloud APIs
- **Specialized Framework**: Vanna optimized for Text-to-SQL tasks
- **RAG Architecture**: Retrieval-Augmented Generation for accuracy
- **Local Inference**: Ollama for quantized model execution
- **Cost Efficiency**: Zero marginal cost per query

**Model Selection:**
- **Primary**: Mistral 7B (4-bit quantized)
- **Alternative**: Llama 3 8B (4-bit quantized)
- **Specialized**: SQLCoder for enhanced SQL generation

### 2.4 Analytics Engine: Statsmodels

**Selection Rationale:**
- **Statistical Rigor**: Classical time series analysis methods
- **Computational Efficiency**: Lightweight compared to deep learning
- **Interpretability**: Clear mathematical foundations
- **Reliability**: Proven algorithms for retail forecasting

## 3. Database Design

### 3.1 Entity Relationship Diagram

```
Categories (1) ──────── (M) Products (M) ──────── (1) Suppliers
    │                        │
    │                        │
    │                   (1)  │  (M)
    │                        │
    │                 TransactionItems
    │                        │
    │                   (M)  │  (1)
    │                        │
    └─────────────────── Transactions
                             │
                        (1)  │  (M)
                             │
                      InventoryLog
```

### 3.2 Schema Definition

#### 3.2.1 Categories Table
```sql
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    parent_category_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
);
```

#### 3.2.2 Suppliers Table
```sql
CREATE TABLE suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_email TEXT,
    contact_phone TEXT,
    address TEXT,
    lead_time_days INTEGER DEFAULT 7,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.2.3 Products Table
```sql
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL,
    supplier_id INTEGER,
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    cost_price REAL NOT NULL CHECK (cost_price >= 0),
    current_stock INTEGER NOT NULL DEFAULT 0 CHECK (current_stock >= 0),
    reorder_level INTEGER NOT NULL DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category_id);
```

#### 3.2.4 Transactions Table
```sql
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount REAL NOT NULL CHECK (total_amount >= 0),
    tax_amount REAL DEFAULT 0 CHECK (tax_amount >= 0),
    payment_method TEXT NOT NULL CHECK (payment_method IN ('CASH', 'CARD', 'OTHER')),
    user_id TEXT,
    status TEXT DEFAULT 'COMPLETED' CHECK (status IN ('PENDING', 'COMPLETED', 'VOIDED')),
    notes TEXT
);

CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_transactions_status ON transactions(status);
```

#### 3.2.5 Transaction Items Table
```sql
CREATE TABLE transaction_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_at_sale REAL NOT NULL CHECK (price_at_sale >= 0),
    discount_amount REAL DEFAULT 0 CHECK (discount_amount >= 0),
    line_total REAL GENERATED ALWAYS AS (quantity * price_at_sale - discount_amount) STORED,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX idx_transaction_items_transaction ON transaction_items(transaction_id);
CREATE INDEX idx_transaction_items_product ON transaction_items(product_id);
```

#### 3.2.6 Inventory Log Table
```sql
CREATE TABLE inventory_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    change_amount INTEGER NOT NULL,
    reason TEXT NOT NULL CHECK (reason IN ('SALE', 'RESTOCK', 'ADJUSTMENT', 'DAMAGE', 'RETURN')),
    reference_id INTEGER, -- Links to transaction_id for sales
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT,
    notes TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX idx_inventory_log_product ON inventory_log(product_id);
CREATE INDEX idx_inventory_log_timestamp ON inventory_log(timestamp);
```

### 3.3 Database Views for AI Queries

#### 3.3.1 Daily Sales Summary
```sql
CREATE VIEW daily_sales_summary AS
SELECT 
    DATE(timestamp) as sale_date,
    COUNT(*) as transaction_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as average_transaction,
    SUM(tax_amount) as total_tax
FROM transactions 
WHERE status = 'COMPLETED'
GROUP BY DATE(timestamp);
```

#### 3.3.2 Product Performance View
```sql
CREATE VIEW product_performance AS
SELECT 
    p.product_id,
    p.sku,
    p.name,
    c.name as category_name,
    p.current_stock,
    p.reorder_level,
    COALESCE(SUM(ti.quantity), 0) as total_sold,
    COALESCE(SUM(ti.line_total), 0) as total_revenue,
    COALESCE(AVG(ti.price_at_sale), p.unit_price) as avg_selling_price,
    (p.unit_price - p.cost_price) as profit_margin
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN transaction_items ti ON p.product_id = ti.product_id
LEFT JOIN transactions t ON ti.transaction_id = t.transaction_id 
    AND t.status = 'COMPLETED'
GROUP BY p.product_id;
```

## 4. Application Architecture

### 4.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Presentation Layer                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │   POS UI    │ │  Admin UI   │ │   Reports UI    │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                  Business Logic Layer                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │Transaction  │ │ Inventory   │ │   AI Query      │   │
│  │ Manager     │ │ Manager     │ │   Engine        │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                   Data Access Layer                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │   SQLite    │ │  ChromaDB   │ │    File I/O     │   │
│  │   Gateway   │ │  Vector     │ │   (Config/Log)  │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │   Ollama    │ │  Hardware   │ │   Logging &     │   │
│  │   Runtime   │ │  Drivers    │ │   Monitoring    │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Core Components

#### 4.2.1 Transaction Manager
**Responsibilities:**
- Atomic transaction processing
- Cart management and state
- Payment processing coordination
- Receipt generation

**Key Methods:**
```python
class TransactionManager:
    def create_transaction(self, cart_items: List[CartItem]) -> Transaction
    def add_item_to_cart(self, product_id: int, quantity: int) -> None
    def apply_discount(self, item_id: int, discount: Decimal) -> None
    def process_payment(self, payment_method: str, amount: Decimal) -> bool
    def void_transaction(self, transaction_id: int) -> bool
```

#### 4.2.2 Inventory Manager
**Responsibilities:**
- Stock level management
- Reorder point monitoring
- Audit trail maintenance
- Forecasting integration

**Key Methods:**
```python
class InventoryManager:
    def update_stock(self, product_id: int, change: int, reason: str) -> None
    def get_low_stock_products(self) -> List[Product]
    def generate_reorder_report(self) -> ReorderReport
    def get_stock_history(self, product_id: int) -> List[InventoryLog]
```

#### 4.2.3 AI Query Engine
**Responsibilities:**
- Natural language processing
- SQL generation and validation
- Result formatting and visualization
- Safety and security enforcement

**Key Methods:**
```python
class AIQueryEngine:
    def process_query(self, question: str) -> QueryResult
    def train_on_schema(self, ddl_statements: List[str]) -> None
    def validate_sql(self, sql: str) -> bool
    def format_results(self, data: DataFrame) -> FormattedResult
```

## 5. AI Implementation Design

### 5.1 Vanna.ai Configuration for Offline Operation

```python
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

class LocalVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config={
            'path': './data/chromadb',
            'collection_name': 'pos_schema'
        })
        Ollama.__init__(self, config={
            'model': 'mistral:7b-instruct-q4_0',
            'base_url': 'http://localhost:11434'
        })
    
    def setup_database_connection(self):
        self.connect_to_sqlite('data/pos_system.db')
        
    def train_on_pos_schema(self):
        # Train on DDL statements
        ddl_statements = self.get_database_schema()
        for ddl in ddl_statements:
            self.train(ddl=ddl)
            
        # Train on example queries
        example_queries = [
            ("What were total sales yesterday?", 
             "SELECT SUM(total_amount) FROM transactions WHERE DATE(timestamp) = DATE('now', '-1 day')"),
            ("Show top 5 selling products this month",
             "SELECT p.name, SUM(ti.quantity) as sold FROM products p JOIN transaction_items ti ON p.product_id = ti.product_id JOIN transactions t ON ti.transaction_id = t.transaction_id WHERE strftime('%Y-%m', t.timestamp) = strftime('%Y-%m', 'now') GROUP BY p.product_id ORDER BY sold DESC LIMIT 5")
        ]
        
        for question, sql in example_queries:
            self.train(question=question, sql=sql)
```

### 5.2 Query Safety and Validation

```python
class QueryValidator:
    ALLOWED_OPERATIONS = {'SELECT'}
    FORBIDDEN_KEYWORDS = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE'}
    
    def validate_sql(self, sql: str) -> Tuple[bool, str]:
        sql_upper = sql.upper().strip()
        
        # Check for forbidden operations
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in sql_upper:
                return False, f"Forbidden operation: {keyword}"
        
        # Ensure only SELECT statements
        if not sql_upper.startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
            
        # Additional safety checks
        if ';' in sql and sql.count(';') > 1:
            return False, "Multiple statements not allowed"
            
        return True, "Query is safe"
```

## 6. Hardware Integration Design

### 6.1 Thermal Printer Integration

```python
from escpos.printer import Usb
from escpos.exceptions import USBNotFoundError

class ReceiptPrinter:
    def __init__(self, vendor_id: int = 0x04b8, product_id: int = 0x0202):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.printer = None
        
    def connect(self) -> bool:
        try:
            self.printer = Usb(self.vendor_id, self.product_id)
            return True
        except USBNotFoundError:
            return False
    
    def print_receipt(self, transaction: Transaction) -> bool:
        if not self.printer:
            return False
            
        try:
            # Header
            self.printer.set(align='center', text_type='B')
            self.printer.text("STORE NAME\n")
            self.printer.text("123 Main Street\n")
            self.printer.text("City, State 12345\n\n")
            
            # Transaction details
            self.printer.set(align='left', text_type='normal')
            self.printer.text(f"Transaction: {transaction.transaction_id}\n")
            self.printer.text(f"Date: {transaction.timestamp.strftime('%Y-%m-%d %H:%M')}\n")
            self.printer.text("-" * 32 + "\n")
            
            # Items
            for item in transaction.items:
                self.printer.text(f"{item.product_name[:20]:<20}\n")
                self.printer.text(f"  {item.quantity} x ${item.price_at_sale:.2f} = ${item.line_total:.2f}\n")
            
            # Totals
            self.printer.text("-" * 32 + "\n")
            self.printer.text(f"Subtotal: ${transaction.subtotal:.2f}\n")
            self.printer.text(f"Tax: ${transaction.tax_amount:.2f}\n")
            self.printer.set(text_type='B')
            self.printer.text(f"TOTAL: ${transaction.total_amount:.2f}\n")
            
            # Footer
            self.printer.text("\nThank you for your business!\n\n")
            self.printer.cut()
            
            return True
        except Exception as e:
            print(f"Printing error: {e}")
            return False
```

### 6.2 Barcode Scanner Integration

```python
import flet as ft

class BarcodeHandler:
    def __init__(self, inventory_manager: InventoryManager):
        self.inventory_manager = inventory_manager
        self.scan_buffer = ""
        self.last_scan_time = 0
        
    def handle_barcode_input(self, e: ft.ControlEvent):
        current_time = time.time()
        
        # Reset buffer if too much time has passed
        if current_time - self.last_scan_time > 0.1:
            self.scan_buffer = ""
        
        self.last_scan_time = current_time
        
        # Accumulate characters
        if e.data == "Enter":
            # Process complete barcode
            self.process_barcode(self.scan_buffer)
            self.scan_buffer = ""
        else:
            self.scan_buffer += e.data
    
    def process_barcode(self, sku: str):
        product = self.inventory_manager.get_product_by_sku(sku)
        if product:
            self.add_to_cart(product)
        else:
            self.show_product_not_found(sku)
```

## 7. Forecasting and Analytics Design

### 7.1 Statistical Forecasting Engine

```python
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing

class ForecastingEngine:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def generate_demand_forecast(self, product_id: int, days_ahead: int = 30) -> ForecastResult:
        # Get historical sales data
        sales_data = self.get_sales_history(product_id)
        
        if len(sales_data) < 14:  # Need minimum data
            return self.simple_average_forecast(sales_data, days_ahead)
        
        # Prepare time series
        ts = pd.Series(sales_data['quantity'].values, 
                      index=pd.to_datetime(sales_data['date']))
        ts = ts.resample('D').sum().fillna(0)
        
        # Seasonal decomposition
        if len(ts) >= 14:
            decomposition = seasonal_decompose(ts, model='additive', period=7)
            
            # Exponential smoothing forecast
            model = ExponentialSmoothing(ts, 
                                       trend='add', 
                                       seasonal='add', 
                                       seasonal_periods=7)
            fitted_model = model.fit()
            forecast = fitted_model.forecast(days_ahead)
            
            return ForecastResult(
                forecast_values=forecast.tolist(),
                confidence_intervals=self.calculate_confidence_intervals(fitted_model, days_ahead),
                trend_component=decomposition.trend.iloc[-7:].mean(),
                seasonal_component=decomposition.seasonal.iloc[-7:].tolist()
            )
        
        return self.simple_exponential_smoothing(ts, days_ahead)
    
    def generate_reorder_recommendations(self) -> List[ReorderRecommendation]:
        recommendations = []
        
        # Get products approaching reorder level
        low_stock_products = self.get_low_stock_products()
        
        for product in low_stock_products:
            forecast = self.generate_demand_forecast(product.product_id)
            lead_time = product.supplier.lead_time_days
            
            # Calculate recommended order quantity
            expected_demand = sum(forecast.forecast_values[:lead_time])
            safety_stock = expected_demand * 0.2  # 20% safety buffer
            
            recommended_quantity = max(
                expected_demand + safety_stock - product.current_stock,
                product.reorder_level
            )
            
            recommendations.append(ReorderRecommendation(
                product=product,
                recommended_quantity=int(recommended_quantity),
                urgency_score=self.calculate_urgency(product, forecast),
                expected_stockout_date=self.estimate_stockout_date(product, forecast)
            ))
        
        return sorted(recommendations, key=lambda x: x.urgency_score, reverse=True)
```

## 8. User Interface Design

### 8.1 Main POS Interface Layout

```python
import flet as ft

class POSMainView:
    def __init__(self):
        self.cart_items = []
        self.current_total = 0.0
        
    def build(self) -> ft.Control:
        return ft.Row([
            # Left Panel - Product Catalog
            ft.Container(
                content=ft.Column([
                    ft.TextField(
                        label="Search products or scan barcode",
                        on_submit=self.handle_search_or_scan,
                        autofocus=True
                    ),
                    ft.Divider(),
                    self.build_product_grid()
                ]),
                width=400,
                padding=10
            ),
            
            # Right Panel - Shopping Cart
            ft.Container(
                content=ft.Column([
                    ft.Text("Shopping Cart", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Container(
                        content=self.build_cart_list(),
                        expand=True
                    ),
                    ft.Divider(),
                    self.build_totals_section(),
                    self.build_payment_buttons()
                ]),
                width=400,
                padding=10
            )
        ])
    
    def build_product_grid(self) -> ft.GridView:
        return ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=120,
            child_aspect_ratio=0.8,
            spacing=5,
            run_spacing=5
        )
    
    def build_cart_list(self) -> ft.ListView:
        return ft.ListView(
            expand=True,
            spacing=5
        )
    
    def build_totals_section(self) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Subtotal:", weight=ft.FontWeight.BOLD),
                    ft.Text(f"${self.current_total:.2f}", weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Tax:", weight=ft.FontWeight.BOLD),
                    ft.Text(f"${self.current_total * 0.08:.2f}", weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Row([
                    ft.Text("TOTAL:", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"${self.current_total * 1.08:.2f}", size=18, weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            padding=10,
            bgcolor=ft.colors.GREY_100,
            border_radius=5
        )
```

### 8.2 AI Query Interface

```python
class AIQueryDialog:
    def __init__(self, ai_engine: AIQueryEngine):
        self.ai_engine = ai_engine
        self.chat_history = []
        
    def build_dialog(self) -> ft.AlertDialog:
        return ft.AlertDialog(
            title=ft.Text("Ask AI about your business"),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=self.build_chat_history(),
                        height=300,
                        width=500
                    ),
                    ft.TextField(
                        label="Ask a question about sales, inventory, or performance...",
                        multiline=True,
                        on_submit=self.handle_query
                    )
                ]),
                width=600,
                height=400
            ),
            actions=[
                ft.TextButton("Close", on_click=self.close_dialog),
                ft.ElevatedButton("Ask", on_click=self.handle_query)
            ]
        )
    
    async def handle_query(self, e):
        question = e.control.value
        if not question.strip():
            return
            
        # Add user question to chat
        self.add_to_chat("user", question)
        
        # Show loading indicator
        self.add_to_chat("assistant", "Thinking...")
        
        try:
            # Process query asynchronously
            result = await self.ai_engine.process_query_async(question)
            
            # Replace loading message with result
            self.chat_history[-1] = ("assistant", self.format_result(result))
            
        except Exception as ex:
            self.chat_history[-1] = ("assistant", f"Sorry, I encountered an error: {str(ex)}")
        
        self.update_chat_display()
```

## 9. Correctness Properties

Based on the prework analysis, here are the key correctness properties that must be validated through property-based testing:

### 9.1 Transaction Atomicity Properties

**Property 1.1: Transaction Completeness**
```python
def test_transaction_atomicity(transaction_data):
    """
    **Validates: Requirements 2.1.2**
    
    Property: Either all parts of a transaction complete successfully, 
    or none of them do (atomic operation).
    """
    # Test that transaction, items, and inventory updates are atomic
    pass
```

**Property 1.2: Inventory Consistency**
```python
def test_inventory_consistency(operations):
    """
    **Validates: Requirements 2.1.3**
    
    Property: The sum of all inventory movements must equal 
    the difference between initial and final stock levels.
    """
    # Test that inventory logs maintain mathematical consistency
    pass
```

### 9.2 Data Integrity Properties

**Property 2.1: Stock Level Constraints**
```python
def test_stock_never_negative(product_operations):
    """
    **Validates: Requirements 2.1.3**
    
    Property: Product stock levels must never go below zero 
    through any sequence of operations.
    """
    # Test that stock constraints are enforced
    pass
```

**Property 2.2: Audit Trail Completeness**
```python
def test_audit_trail_completeness(transactions):
    """
    **Validates: Requirements 3.4**
    
    Property: Every stock change must have a corresponding 
    entry in the inventory log.
    """
    # Test that all operations are logged
    pass
```

### 9.3 Business Logic Properties

**Property 3.1: Price Calculation Accuracy**
```python
def test_price_calculations(cart_items):
    """
    **Validates: Requirements 2.1.2**
    
    Property: Transaction totals must equal the sum of 
    (quantity × price - discount) for all items plus tax.
    """
    # Test mathematical accuracy of pricing
    pass
```

**Property 3.2: Forecasting Mathematical Consistency**
```python
def test_forecasting_bounds(historical_data):
    """
    **Validates: Requirements 2.3.2**
    
    Property: Moving averages must fall between the minimum 
    and maximum values of the input data range.
    """
    # Test statistical calculation bounds
    pass
```

### 9.4 AI Query Safety Properties

**Property 4.1: SQL Generation Safety**
```python
def test_sql_safety(natural_language_queries):
    """
    **Validates: Requirements 2.2.1**
    
    Property: Generated SQL must only contain SELECT statements 
    and never include destructive operations.
    """
    # Test that AI never generates unsafe SQL
    pass
```

### 9.5 Hardware Integration Properties

**Property 5.1: Barcode Processing Consistency**
```python
def test_barcode_processing(barcode_inputs):
    """
    **Validates: Requirements 2.4.2**
    
    Property: Valid barcodes must always resolve to the same 
    product, and invalid barcodes must always be rejected.
    """
    # Test barcode lookup consistency
    pass
```

## 10. Testing Strategy

### 10.1 Property-Based Testing Framework
- **Framework**: Hypothesis (Python)
- **Test Data Generation**: Custom strategies for retail data
- **Coverage**: All critical business logic and data integrity rules
- **Execution**: Automated testing with CI/CD integration

### 10.2 Example-Based Testing
- **AI Query Accuracy**: Known question-answer pairs
- **Receipt Formatting**: Template validation with sample data
- **Hardware Integration**: Mock device testing

### 10.3 Performance Testing
- **Load Testing**: Concurrent transaction processing
- **Memory Testing**: Long-running operation monitoring
- **Response Time**: UI interaction latency measurement

## 11. Deployment Architecture

### 11.1 Application Packaging
```python
# Build configuration for standalone executable
import flet as ft

def main():
    ft.app(
        target=pos_main,
        assets_dir="assets",
        web=False,  # Desktop application only
        port=0      # No web server needed
    )

if __name__ == "__main__":
    main()
```

### 11.2 Installation Requirements
- **Python Runtime**: Embedded with application
- **Ollama Installation**: Automated setup script
- **Model Download**: Mistral 7B quantized (4GB)
- **Database Initialization**: Automated schema creation
- **Hardware Drivers**: Printer and scanner detection

### 11.3 Configuration Management
```json
{
  "database": {
    "path": "./data/pos_system.db",
    "backup_interval_hours": 24,
    "wal_checkpoint_interval": 1000
  },
  "ai": {
    "model": "mistral:7b-instruct-q4_0",
    "ollama_url": "http://localhost:11434",
    "vector_store_path": "./data/chromadb"
  },
  "hardware": {
    "printer": {
      "vendor_id": "0x04b8",
      "product_id": "0x0202",
      "auto_cut": true
    },
    "scanner": {
      "beep_on_scan": true
    }
  },
  "business": {
    "store_name": "Your Store Name",
    "tax_rate": 0.08,
    "currency": "USD",
    "receipt_footer": "Thank you for your business!"
  }
}
```

This design document provides a comprehensive blueprint for implementing the Local-First POS system with all the architectural decisions, technical specifications, and correctness properties needed for successful development and deployment.